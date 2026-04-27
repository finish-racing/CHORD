from __future__ import annotations
import json
import typer
from chord.config import load_settings
from chord.logging_setup import configure_logging
from chord.utils.paths import ensure_runtime_dirs
from chord.utils.validation import validate_quiz_answers
from chord.db.session import make_engine, make_session_factory
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
from chord.services.diagnostics_service import collect_run_diagnostics, export_debug_index
from chord.services.operator_service import (
    get_run_status_payload, export_results_payload, export_curated_payload,
    write_json_export, soft_reset as soft_reset_run, hard_reset as hard_reset_run
)

app = typer.Typer(help="CHORD Ubuntu CLI")

def bootstrap(config_path: str | None = None):
    settings = load_settings(config_path)
    configure_logging(settings)
    ensure_runtime_dirs(settings)
    session_factory = make_session_factory(settings)
    return settings, session_factory

@app.command("initdb")
def initdb(config: str | None = typer.Option(None, help="Path to config TOML")):
    settings, _ = bootstrap(config)
    engine = make_engine(settings)
    Base.metadata.create_all(engine)
    typer.echo("Initialized CHORD database schema.")

@app.command("quiz")
def quiz():
    typer.echo(json.dumps(get_quiz_definition(), indent=2))

@app.command("create-run")
def create_run(config: str | None = typer.Option(None), mode: str = typer.Option("analysis"), notes: str | None = typer.Option(None)):
    settings, session_factory = bootstrap(config)
    with session_factory() as session:
        run = repo.create_run(session, mode=mode, debug_enabled=settings.debug.enabled, notes=notes)
        typer.echo(json.dumps({"run_id": run.id, "status": run.status}, indent=2))

@app.command("import-playlists")
def import_playlists(
    run_id: int = typer.Option(...),
    top25: str = typer.Option(..., help="Path to Top 25 Most Played export"),
    playlist: list[str] = typer.Option([], help="One or more playlist exports"),
    config: str | None = typer.Option(None),
):
    if not playlist:
        raise typer.BadParameter("At least one --playlist is required.")
    settings, session_factory = bootstrap(config)
    with session_factory() as session:
        repo.update_run_status(session, run_id, "importing")
        ingest_playlist_file(session, settings, run_id=run_id, file_path=top25, playlist_name=__import__("pathlib").Path(top25).stem, playlist_kind="top25", source_order=0)
        for idx, item in enumerate(playlist, start=1):
            ingest_playlist_file(session, settings, run_id=run_id, file_path=item, playlist_name=__import__("pathlib").Path(item).stem, playlist_kind="playlist", source_order=idx)
        repo.update_run_status(session, run_id, "imported")
    typer.echo("Imported Top 25 and playlist set.")

@app.command("submit-quiz")
def submit_quiz(
    run_id: int = typer.Option(...),
    answers_json: str = typer.Option(..., help='JSON object of quiz answers'),
    config: str | None = typer.Option(None),
):
    answers = json.loads(answers_json)
    validate_quiz_answers(answers)
    _, session_factory = bootstrap(config)
    with session_factory() as session:
        profile = submit_quiz_answers(session, run_id=run_id, answers=answers)
        repo.update_run_status(session, run_id, "quiz_captured")
        typer.echo(json.dumps({"run_id": run_id, "profile_id": profile.id}, indent=2))

@app.command("build-aggregates")
def build_aggregates(run_id: int = typer.Option(...), config: str | None = typer.Option(None)):
    settings, session_factory = bootstrap(config)
    with session_factory() as session:
        payload = compute_wave_b1_aggregates(session, settings, run_id=run_id)
        repo.update_run_status(session, run_id, "aggregates_built")
        typer.echo(json.dumps(payload, indent=2))

@app.command("show-aggregates")
def show_aggregates(run_id: int = typer.Option(...), config: str | None = typer.Option(None)):
    _, session_factory = bootstrap(config)
    with session_factory() as session:
        item = repo.get_run_aggregate(session, run_id)
        if item is None:
            raise typer.BadParameter(f"No aggregate payload found for run {run_id}")
        typer.echo(json.dumps(item.aggregate_payload, indent=2))

@app.command("enrich-run")
def enrich_run_command(run_id: int = typer.Option(...), config: str | None = typer.Option(None)):
    settings, session_factory = bootstrap(config)
    with session_factory() as session:
        payload = enrich_run(session, settings, run_id=run_id)
        repo.update_run_status(session, run_id, "enriched")
        typer.echo(json.dumps(payload, indent=2))

@app.command("show-enrichment")
def show_enrichment(run_id: int = typer.Option(...), config: str | None = typer.Option(None)):
    _, session_factory = bootstrap(config)
    with session_factory() as session:
        item = repo.get_run_enrichment_summary(session, run_id)
        if item is None:
            raise typer.BadParameter(f"No enrichment summary found for run {run_id}")
        typer.echo(json.dumps(item.summary_payload, indent=2))

@app.command("build-identity")
def build_identity(run_id: int = typer.Option(...), config: str | None = typer.Option(None)):
    settings, session_factory = bootstrap(config)
    with session_factory() as session:
        payload = build_identity_profile(session, settings, run_id=run_id)
        repo.update_run_status(session, run_id, "identity_built")
        typer.echo(json.dumps(payload, indent=2))

@app.command("show-identity")
def show_identity(run_id: int = typer.Option(...), config: str | None = typer.Option(None)):
    _, session_factory = bootstrap(config)
    with session_factory() as session:
        item = repo.get_identity_profile(session, run_id)
        if item is None:
            raise typer.BadParameter(f"No identity profile found for run {run_id}")
        typer.echo(json.dumps(item.profile_payload, indent=2))

@app.command("run-prism")
def run_prism_command(run_id: int = typer.Option(...), mode: str = typer.Option("balanced"), config: str | None = typer.Option(None)):
    settings, session_factory = bootstrap(config)
    with session_factory() as session:
        payload = run_prism(session, settings, run_id=run_id, mode=mode)
        repo.update_run_status(session, run_id, "prism_scored")
        typer.echo(json.dumps(payload["summary"], indent=2))

@app.command("show-prism")
def show_prism(run_id: int = typer.Option(...), mode: str = typer.Option("balanced"), config: str | None = typer.Option(None)):
    _, session_factory = bootstrap(config)
    with session_factory() as session:
        payload = export_results_payload(session, run_id, mode)
        typer.echo(json.dumps(payload, indent=2))

@app.command("build-curated")
def build_curated(run_id: int = typer.Option(...), mode: str = typer.Option("balanced"), length: int = typer.Option(60), config: str | None = typer.Option(None)):
    settings, session_factory = bootstrap(config)
    with session_factory() as session:
        payload = build_curated_playlist(session, settings, run_id=run_id, mode=mode, requested_length=length)
        repo.update_run_status(session, run_id, "curated_built")
        typer.echo(json.dumps(payload["summary"], indent=2))

@app.command("show-curated")
def show_curated(run_id: int = typer.Option(...), mode: str = typer.Option("balanced"), config: str | None = typer.Option(None)):
    _, session_factory = bootstrap(config)
    with session_factory() as session:
        payload = export_curated_payload(session, run_id, mode)
        typer.echo(json.dumps(payload, indent=2))

@app.command("show-status")
def show_status(run_id: int = typer.Option(...), config: str | None = typer.Option(None)):
    _, session_factory = bootstrap(config)
    with session_factory() as session:
        typer.echo(json.dumps(get_run_status_payload(session, run_id), indent=2))

@app.command("list-runs")
def list_runs(config: str | None = typer.Option(None)):
    _, session_factory = bootstrap(config)
    with session_factory() as session:
        runs = repo.list_runs(session)
        typer.echo(json.dumps([
            {"id": r.id, "status": r.status, "mode": r.mode, "debug_enabled": r.debug_enabled}
            for r in runs
        ], indent=2))

@app.command("list-playlists")
def list_playlists(run_id: int = typer.Option(...), config: str | None = typer.Option(None)):
    _, session_factory = bootstrap(config)
    with session_factory() as session:
        playlists = repo.list_playlists_for_run(session, run_id)
        typer.echo(json.dumps([
            {"id": p.id, "playlist_name": p.playlist_name, "playlist_kind": p.playlist_kind, "source_order": p.source_order}
            for p in playlists
        ], indent=2))

@app.command("export-results")
def export_results(run_id: int = typer.Option(...), mode: str = typer.Option("balanced"), out: str = typer.Option(...), config: str | None = typer.Option(None)):
    _, session_factory = bootstrap(config)
    with session_factory() as session:
        payload = export_results_payload(session, run_id, mode)
        path = write_json_export(payload, out)
        typer.echo(json.dumps({"exported_to": path}, indent=2))

@app.command("export-curated-playlist")
def export_curated(run_id: int = typer.Option(...), mode: str = typer.Option("balanced"), out: str = typer.Option(...), config: str | None = typer.Option(None)):
    _, session_factory = bootstrap(config)
    with session_factory() as session:
        payload = export_curated_payload(session, run_id, mode)
        path = write_json_export(payload, out)
        typer.echo(json.dumps({"exported_to": path}, indent=2))

@app.command("list-debug-artifacts")
def list_debug_artifacts(run_id: int = typer.Option(...), config: str | None = typer.Option(None)):
    _, session_factory = bootstrap(config)
    with session_factory() as session:
        items = repo.list_debug_artifacts_for_run(session, run_id)
        typer.echo(json.dumps([
            {"id": x.id, "artifact_type": x.artifact_type, "artifact_path": x.artifact_path}
            for x in items
        ], indent=2))

@app.command("soft-reset")
def soft_reset(run_id: int = typer.Option(...), config: str | None = typer.Option(None)):
    _, session_factory = bootstrap(config)
    with session_factory() as session:
        soft_reset_run(session, run_id)
        typer.echo(json.dumps({"run_id": run_id, "status": "imported", "reset": "soft"}, indent=2))

@app.command("hard-reset")
def hard_reset(run_id: int = typer.Option(...), config: str | None = typer.Option(None)):
    _, session_factory = bootstrap(config)
    with session_factory() as session:
        hard_reset_run(session, run_id)
        typer.echo(json.dumps({"run_id": run_id, "reset": "hard", "deleted": True}, indent=2))

if __name__ == "__main__":
    app()


@app.command("run-openai-enhancement")
def run_openai_enhancement_cmd(run_id: int = typer.Option(...), mode: str = typer.Option("balanced"), config: str | None = typer.Option(None)):
    settings, session_factory = bootstrap(config)
    with session_factory() as session:
        payload = run_openai_enhancement(session, settings, run_id=run_id, mode=mode)
        repo.update_run_status(session, run_id, "openai_enhanced")
        typer.echo(json.dumps(payload["summary"], indent=2))

@app.command("show-openai-enhancement")
def show_openai_enhancement(run_id: int = typer.Option(...), mode: str = typer.Option("balanced"), config: str | None = typer.Option(None)):
    _, session_factory = bootstrap(config)
    with session_factory() as session:
        enh_set = repo.get_openai_enhancement_set(session, run_id, mode)
        if enh_set is None:
            raise typer.BadParameter(f"No OpenAI enhancement set found for run {run_id} and mode {mode}")
        items = repo.list_openai_enhancement_items(session, enh_set.id)
        typer.echo(json.dumps({
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
        }, indent=2))


@app.command("diagnose-run")
def diagnose_run(run_id: int = typer.Option(...), config: str | None = typer.Option(None)):
    settings, session_factory = bootstrap(config)
    with session_factory() as session:
        payload = collect_run_diagnostics(session, settings, run_id=run_id)
        typer.echo(json.dumps(payload, indent=2))

@app.command("export-debug-index")
def export_debug_index_cmd(run_id: int = typer.Option(...), out: str = typer.Option(...), config: str | None = typer.Option(None)):
    _, session_factory = bootstrap(config)
    with session_factory() as session:
        payload = export_debug_index(session, run_id=run_id)
        path = write_json_export(payload, out)
        typer.echo(json.dumps({"exported_to": path, "artifact_count": payload["artifact_count"]}, indent=2))
