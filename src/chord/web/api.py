from __future__ import annotations
import json, tempfile
from pathlib import Path
from fastapi import FastAPI, Form, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from chord.config import load_settings
from chord.logging_setup import configure_logging
from chord.utils.paths import ensure_runtime_dirs
from chord.utils.validation import validate_quiz_answers
from chord.db.session import make_session_factory, make_engine
from chord.db.base import Base
from chord.db import repositories as repo
from chord.domain.quiz import get_quiz_definition
from chord.services.run_service import ingest_playlist_file, submit_quiz_answers
from chord.services.feature_service import compute_wave_b1_aggregates
from chord.services.enrichment_service import enrich_run
from chord.services.identity_service import build_identity_profile
from chord.services.prism_service import run_prism
from chord.services.curated_playlist_service import build_curated_playlist
from chord.services.openai_service import run_openai_enhancement
from chord.services.operator_service import get_run_status_payload, export_results_payload, export_curated_payload
from chord.services.diagnostics_service import collect_run_diagnostics, export_debug_index
from chord.errors import ChordError
from chord.web.ui_helpers import progress_for_status

settings = load_settings(None)
configure_logging(settings)
ensure_runtime_dirs(settings)
session_factory = make_session_factory(settings)

api = FastAPI(title="CHORD Web")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))
api.mount("/static", StaticFiles(directory=str(Path(__file__).resolve().parent / "static")), name="static")

@api.on_event("startup")
def startup():
    engine = make_engine(settings)
    Base.metadata.create_all(engine)

# JSON routes
@api.get("/health")
def health():
    return {"ok": True, "product": "CHORD", "wave": "C4"}

@api.get("/quiz")
def quiz():
    return get_quiz_definition()

@api.get("/runs")
def runs():
    with session_factory() as session:
        items = repo.list_runs(session)
        return [{"id": x.id, "status": x.status, "mode": x.mode, "debug_enabled": x.debug_enabled} for x in items]

@api.post("/runs")
def create_run(mode: str = Form("analysis"), notes: str | None = Form(None)):
    with session_factory() as session:
        run = repo.create_run(session, mode=mode, debug_enabled=settings.debug.enabled, notes=notes)
        return {"run_id": run.id, "status": run.status}

@api.get("/runs/{run_id}/playlists")
def playlists(run_id: int):
    with session_factory() as session:
        items = repo.list_playlists_for_run(session, run_id)
        return [{"id": p.id, "playlist_name": p.playlist_name, "playlist_kind": p.playlist_kind, "source_order": p.source_order} for p in items]

@api.post("/runs/{run_id}/quiz")
def post_quiz(run_id: int, answers_json: str = Form(...)):
    answers = json.loads(answers_json)
    validate_quiz_answers(answers)
    with session_factory() as session:
        submit_quiz_answers(session, run_id=run_id, answers=answers)
        repo.update_run_status(session, run_id, "quiz_captured")
        return {"run_id": run_id, "status": "quiz_captured"}

@api.post("/runs/{run_id}/uploads")
async def upload_playlists(run_id: int, top25: UploadFile = File(...), playlists: list[UploadFile] = File(...)):
    if not playlists:
        raise HTTPException(status_code=400, detail="At least one playlist upload is required.")
    tmpdir = Path(tempfile.mkdtemp(prefix="chord_wave_c4_"))
    top25_path = tmpdir / top25.filename
    top25_path.write_bytes(await top25.read())
    playlist_paths = []
    for item in playlists:
        path = tmpdir / item.filename
        path.write_bytes(await item.read())
        playlist_paths.append(path)

    with session_factory() as session:
        repo.update_run_status(session, run_id, "importing")
        ingest_playlist_file(session, settings, run_id=run_id, file_path=str(top25_path), playlist_name=top25_path.stem, playlist_kind="top25", source_order=0)
        for idx, item in enumerate(playlist_paths, start=1):
            ingest_playlist_file(session, settings, run_id=run_id, file_path=str(item), playlist_name=item.stem, playlist_kind="playlist", source_order=idx)
        repo.update_run_status(session, run_id, "imported")
    return {"run_id": run_id, "status": "imported", "playlist_count": len(playlist_paths) + 1}

@api.post("/runs/{run_id}/aggregates")
def build_aggregates(run_id: int):
    with session_factory() as session:
        payload = compute_wave_b1_aggregates(session, settings, run_id=run_id)
        repo.update_run_status(session, run_id, "aggregates_built")
        return payload

@api.get("/runs/{run_id}/aggregates")
def get_aggregates(run_id: int):
    with session_factory() as session:
        item = repo.get_run_aggregate(session, run_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Aggregate payload not found")
        return item.aggregate_payload

@api.post("/runs/{run_id}/enrich")
def enrich_run_route(run_id: int):
    with session_factory() as session:
        payload = enrich_run(session, settings, run_id=run_id)
        repo.update_run_status(session, run_id, "enriched")
        return payload

@api.get("/runs/{run_id}/enrichment")
def get_enrichment(run_id: int):
    with session_factory() as session:
        item = repo.get_run_enrichment_summary(session, run_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Enrichment summary not found")
        return item.summary_payload

@api.post("/runs/{run_id}/identity")
def build_identity_route(run_id: int):
    with session_factory() as session:
        payload = build_identity_profile(session, settings, run_id=run_id)
        repo.update_run_status(session, run_id, "identity_built")
        return payload

@api.get("/runs/{run_id}/identity")
def get_identity(run_id: int):
    with session_factory() as session:
        item = repo.get_identity_profile(session, run_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Identity profile not found")
        return item.profile_payload

@api.post("/runs/{run_id}/prism")
def run_prism_route(run_id: int, mode: str = "balanced"):
    with session_factory() as session:
        payload = run_prism(session, settings, run_id=run_id, mode=mode)
        repo.update_run_status(session, run_id, "prism_scored")
        return payload

@api.get("/runs/{run_id}/prism")
def get_prism(run_id: int, mode: str = "balanced"):
    with session_factory() as session:
        return export_results_payload(session, run_id, mode)

@api.post("/runs/{run_id}/curated")
def build_curated_route(run_id: int, mode: str = "balanced", length: int = 60):
    with session_factory() as session:
        payload = build_curated_playlist(session, settings, run_id=run_id, mode=mode, requested_length=length)
        repo.update_run_status(session, run_id, "curated_built")
        return payload

@api.get("/runs/{run_id}/curated")
def get_curated(run_id: int, mode: str = "balanced"):
    with session_factory() as session:
        return export_curated_payload(session, run_id, mode)

@api.get("/runs/{run_id}/status")
def get_status(run_id: int):
    with session_factory() as session:
        return get_run_status_payload(session, run_id)

@api.get("/runs/{run_id}/debug-artifacts")
def get_debug_artifacts(run_id: int):
    with session_factory() as session:
        items = repo.list_debug_artifacts_for_run(session, run_id)
        return [{"id": x.id, "artifact_type": x.artifact_type, "artifact_path": x.artifact_path} for x in items]

@api.get("/runs/{run_id}/exports/results")
def api_export_results(run_id: int, mode: str = "balanced"):
    with session_factory() as session:
        return export_results_payload(session, run_id, mode)

@api.get("/runs/{run_id}/exports/curated")
def api_export_curated(run_id: int, mode: str = "balanced"):
    with session_factory() as session:
        return export_curated_payload(session, run_id, mode)

# HTML routes
@api.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "CHORD"})

@api.get("/new-run", response_class=HTMLResponse)
def new_run_form(request: Request):
    return templates.TemplateResponse("new_run.html", {"request": request, "title": "New Run - CHORD"})

@api.post("/new-run")
def new_run_submit(mode: str = Form("analysis"), notes: str | None = Form(None)):
    with session_factory() as session:
        run = repo.create_run(session, mode=mode, debug_enabled=settings.debug.enabled, notes=notes)
    return RedirectResponse(url=f"/runs/{run.id}", status_code=303)

@api.get("/runs/{run_id}", response_class=HTMLResponse)
def run_detail(request: Request, run_id: int):
    with session_factory() as session:
        status = get_run_status_payload(session, run_id)
        aggregates = None
        enrichment = None
        identity = None
        prism = None
        curated = None
        debug_artifacts = None
        ra = repo.get_run_aggregate(session, run_id)
        if ra: aggregates = ra.aggregate_payload
        re = repo.get_run_enrichment_summary(session, run_id)
        if re: enrichment = re.summary_payload
        ip = repo.get_identity_profile(session, run_id)
        if ip: identity = ip.profile_payload
        rs = repo.get_recommendation_set(session, run_id, "balanced")
        if rs: prism = export_results_payload(session, run_id, "balanced")
        cps = repo.get_curated_playlist_set(session, run_id, "balanced")
        if cps: curated = export_curated_payload(session, run_id, "balanced")
        if settings.debug.enabled:
            debug_artifacts = [{"id": x.id, "artifact_type": x.artifact_type, "artifact_path": x.artifact_path} for x in repo.list_debug_artifacts_for_run(session, run_id)]
    return templates.TemplateResponse(
        "run_detail.html",
        {
            "request": request,
            "title": f"Run {run_id} - CHORD",
            "status": status,
            "progress": progress_for_status(status["status"]),
            "aggregates": aggregates,
            "enrichment": enrichment,
            "identity": identity,
            "prism": prism,
            "curated": curated,
            "debug_artifacts": debug_artifacts,
            "debug_enabled": settings.debug.enabled,
        },
    )

@api.get("/runs/{run_id}/upload-form", response_class=HTMLResponse)
def upload_form(request: Request, run_id: int):
    return templates.TemplateResponse("upload_form.html", {"request": request, "run_id": run_id, "title": f"Upload - Run {run_id}"})

@api.post("/runs/{run_id}/upload-form")
async def upload_form_submit(request: Request, run_id: int, top25: UploadFile = File(...), playlists: list[UploadFile] = File(...)):
    await upload_playlists(run_id, top25, playlists)
    return RedirectResponse(url=f"/runs/{run_id}", status_code=303)

@api.get("/runs/{run_id}/quiz-form", response_class=HTMLResponse)
def quiz_form(request: Request, run_id: int):
    return templates.TemplateResponse("quiz_form.html", {"request": request, "run_id": run_id, "quiz": get_quiz_definition(), "title": f"Quiz - Run {run_id}"})

@api.post("/runs/{run_id}/quiz-form")
async def quiz_form_submit(request: Request, run_id: int):
    form = await request.form()
    answers = {k: str(v) for k, v in form.items()}
    validate_quiz_answers(answers)
    with session_factory() as session:
        submit_quiz_answers(session, run_id=run_id, answers=answers)
        repo.update_run_status(session, run_id, "quiz_captured")
    return RedirectResponse(url=f"/runs/{run_id}", status_code=303)

@api.post("/runs/{run_id}/pipeline/run-all")
def pipeline_run_all(run_id: int):
    with session_factory() as session:
        compute_wave_b1_aggregates(session, settings, run_id=run_id)
        repo.update_run_status(session, run_id, "aggregates_built")
        enrich_run(session, settings, run_id=run_id)
        repo.update_run_status(session, run_id, "enriched")
        build_identity_profile(session, settings, run_id=run_id)
        repo.update_run_status(session, run_id, "identity_built")
        run_prism(session, settings, run_id=run_id, mode="balanced")
        repo.update_run_status(session, run_id, "prism_scored")
        build_curated_playlist(session, settings, run_id=run_id, mode="balanced", requested_length=60)
        repo.update_run_status(session, run_id, "curated_built")
    return RedirectResponse(url=f"/runs/{run_id}", status_code=303)

@api.get("/runs/{run_id}/dashboard", response_class=HTMLResponse)
def dashboard_alias(request: Request, run_id: int):
    return run_detail(request, run_id)


@api.post("/runs/{run_id}/openai")
def run_openai_route(run_id: int, mode: str = "balanced"):
    with session_factory() as session:
        payload = run_openai_enhancement(session, settings, run_id=run_id, mode=mode)
        repo.update_run_status(session, run_id, "openai_enhanced")
        return payload

@api.get("/runs/{run_id}/openai")
def get_openai_enhancement(run_id: int, mode: str = "balanced"):
    with session_factory() as session:
        enh_set = repo.get_openai_enhancement_set(session, run_id, mode)
        if enh_set is None:
            raise HTTPException(status_code=404, detail="OpenAI enhancement set not found")
        items = repo.list_openai_enhancement_items(session, enh_set.id)
        return {
            "summary": enh_set.summary_payload,
            "items": [
                {
                    "rank": x.rank,
                    "recommendation_item_id": x.recommendation_item_id,
                    "enhancement_type": x.enhancement_type,
                    "enhanced_explanation_text": x.enhanced_explanation_text,
                    "enhancement_payload": x.enhancement_payload,
                } for x in items
            ]
        }


@api.exception_handler(ChordError)
async def chord_error_handler(request: Request, exc: ChordError):
    return JSONResponse(status_code=400, content=exc.to_dict(debug=settings.debug.enabled))

@api.get("/runs/{run_id}/diagnostics")
def get_diagnostics(run_id: int):
    with session_factory() as session:
        return collect_run_diagnostics(session, settings, run_id=run_id)

@api.get("/runs/{run_id}/debug-index")
def get_debug_index(run_id: int):
    with session_factory() as session:
        return export_debug_index(session, run_id=run_id)
