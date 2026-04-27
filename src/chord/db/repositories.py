from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import select
from chord.db.models import Run, Upload, Playlist, Track, CanonicalTrack, PlaylistTrackLink, QuizAnswer, CuratorProfile, DebugArtifact

def utcnow():
    return datetime.now(timezone.utc)

def create_run(session, *, mode: str = "analysis", debug_enabled: bool = False, notes: str | None = None) -> Run:
    run = Run(created_at=utcnow(), updated_at=utcnow(), status="created", mode=mode, debug_enabled=debug_enabled, notes=notes)
    session.add(run)
    session.commit()
    session.refresh(run)
    return run

def update_run_status(session, run_id: int, status: str) -> None:
    run = session.get(Run, run_id)
    if not run:
        raise ValueError(f"Run not found: {run_id}")
    run.status = status
    run.updated_at = utcnow()
    session.commit()

def list_runs(session):
    return list(session.execute(select(Run).order_by(Run.id.desc())).scalars())

def create_upload(session, **kwargs) -> Upload:
    item = Upload(created_at=utcnow(), **kwargs)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

def create_playlist(session, **kwargs) -> Playlist:
    item = Playlist(created_at=utcnow(), **kwargs)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

def list_playlists_for_run(session, run_id: int):
    return list(session.execute(select(Playlist).where(Playlist.run_id == run_id).order_by(Playlist.id)).scalars())

def create_track(session, **kwargs) -> Track:
    item = Track(created_at=utcnow(), **kwargs)
    session.add(item)
    session.flush()
    return item

def get_or_create_canonical_track(session, *, run_id: int, canonical_title: str, canonical_artist: str, defaults: dict):
    existing = session.execute(
        select(CanonicalTrack).where(
            CanonicalTrack.run_id == run_id,
            CanonicalTrack.canonical_title == canonical_title,
            CanonicalTrack.canonical_artist == canonical_artist,
        )
    ).scalar_one_or_none()
    if existing:
        return existing, False
    item = CanonicalTrack(run_id=run_id, canonical_title=canonical_title, canonical_artist=canonical_artist, created_at=utcnow(), **defaults)
    session.add(item)
    session.flush()
    return item, True

def link_track(session, canonical_track_id: int, track_id: int):
    item = PlaylistTrackLink(canonical_track_id=canonical_track_id, track_id=track_id, created_at=utcnow())
    session.add(item)
    session.flush()

def add_quiz_answers(session, run_id: int, quiz_version: str, answers: dict[str, str]):
    for key, value in answers.items():
        session.add(QuizAnswer(run_id=run_id, quiz_version=quiz_version, question_key=key, answer_value=value, created_at=utcnow()))
    session.commit()

def upsert_curator_profile_seed(session, run_id: int, quiz_version: str, profile_seed: dict):
    item = session.execute(select(CuratorProfile).where(CuratorProfile.run_id == run_id)).scalar_one_or_none()
    if item is None:
        item = CuratorProfile(run_id=run_id, quiz_version=quiz_version, profile_seed=profile_seed, created_at=utcnow(), updated_at=utcnow())
        session.add(item)
    else:
        item.quiz_version = quiz_version
        item.profile_seed = profile_seed
        item.updated_at = utcnow()
    session.commit()
    session.refresh(item)
    return item

def record_debug_artifact(session, artifact_type: str, artifact_path: str, run_id: int | None = None):
    item = DebugArtifact(run_id=run_id, artifact_type=artifact_type, artifact_path=artifact_path, created_at=utcnow())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def upsert_run_aggregate(session, run_id: int, payload: dict, intake_quality_score: float | None):
    from chord.db.models import RunAggregate
    item = session.execute(select(RunAggregate).where(RunAggregate.run_id == run_id)).scalar_one_or_none()
    if item is None:
        item = RunAggregate(run_id=run_id, aggregate_payload=payload, intake_quality_score=intake_quality_score, created_at=utcnow(), updated_at=utcnow())
        session.add(item)
    else:
        item.aggregate_payload = payload
        item.intake_quality_score = intake_quality_score
        item.updated_at = utcnow()
    session.commit()
    session.refresh(item)
    return item

def upsert_canonical_track_aggregate(session, canonical_track_id: int, payload: dict):
    from chord.db.models import CanonicalTrackAggregate
    item = session.execute(select(CanonicalTrackAggregate).where(CanonicalTrackAggregate.canonical_track_id == canonical_track_id)).scalar_one_or_none()
    if item is None:
        item = CanonicalTrackAggregate(canonical_track_id=canonical_track_id, aggregate_payload=payload, created_at=utcnow(), updated_at=utcnow())
        session.add(item)
    else:
        item.aggregate_payload = payload
        item.updated_at = utcnow()
    session.flush()
    return item

def list_canonical_tracks_for_run(session, run_id: int):
    return list(session.execute(select(CanonicalTrack).where(CanonicalTrack.run_id == run_id).order_by(CanonicalTrack.id)).scalars())

def get_run_aggregate(session, run_id: int):
    from chord.db.models import RunAggregate
    return session.execute(select(RunAggregate).where(RunAggregate.run_id == run_id)).scalar_one_or_none()


def upsert_track_enrichment(session, canonical_track_id: int, source_name: str, *, source_key: str | None, status: str, confidence_score: float | None, provenance_payload: dict, data_payload: dict):
    from chord.db.models import TrackEnrichment
    item = session.execute(
        select(TrackEnrichment).where(
            TrackEnrichment.canonical_track_id == canonical_track_id,
            TrackEnrichment.source_name == source_name
        )
    ).scalar_one_or_none()
    if item is None:
        item = TrackEnrichment(
            canonical_track_id=canonical_track_id,
            source_name=source_name,
            source_key=source_key,
            status=status,
            confidence_score=confidence_score,
            provenance_payload=provenance_payload,
            data_payload=data_payload,
            created_at=utcnow(),
            updated_at=utcnow(),
        )
        session.add(item)
    else:
        item.source_key = source_key
        item.status = status
        item.confidence_score = confidence_score
        item.provenance_payload = provenance_payload
        item.data_payload = data_payload
        item.updated_at = utcnow()
    session.flush()
    return item

def list_track_enrichments_for_run(session, run_id: int):
    from chord.db.models import TrackEnrichment
    return list(session.execute(
        select(TrackEnrichment)
        .join(CanonicalTrack, TrackEnrichment.canonical_track_id == CanonicalTrack.id)
        .where(CanonicalTrack.run_id == run_id)
        .order_by(TrackEnrichment.id)
    ).scalars())

def upsert_run_enrichment_summary(session, run_id: int, summary_payload: dict):
    from chord.db.models import RunEnrichmentSummary
    item = session.execute(select(RunEnrichmentSummary).where(RunEnrichmentSummary.run_id == run_id)).scalar_one_or_none()
    if item is None:
        item = RunEnrichmentSummary(run_id=run_id, summary_payload=summary_payload, created_at=utcnow(), updated_at=utcnow())
        session.add(item)
    else:
        item.summary_payload = summary_payload
        item.updated_at = utcnow()
    session.commit()
    session.refresh(item)
    return item

def get_run_enrichment_summary(session, run_id: int):
    from chord.db.models import RunEnrichmentSummary
    return session.execute(select(RunEnrichmentSummary).where(RunEnrichmentSummary.run_id == run_id)).scalar_one_or_none()


def upsert_identity_profile(session, run_id: int, payload: dict):
    from chord.db.models import IdentityProfile
    item = session.execute(select(IdentityProfile).where(IdentityProfile.run_id == run_id)).scalar_one_or_none()
    if item is None:
        item = IdentityProfile(run_id=run_id, profile_payload=payload, created_at=utcnow(), updated_at=utcnow())
        session.add(item)
    else:
        item.profile_payload = payload
        item.updated_at = utcnow()
    session.commit()
    session.refresh(item)
    return item

def get_identity_profile(session, run_id: int):
    from chord.db.models import IdentityProfile
    return session.execute(select(IdentityProfile).where(IdentityProfile.run_id == run_id)).scalar_one_or_none()

def upsert_canonical_track_identity(session, canonical_track_id: int, payload: dict):
    from chord.db.models import CanonicalTrackIdentity
    item = session.execute(select(CanonicalTrackIdentity).where(CanonicalTrackIdentity.canonical_track_id == canonical_track_id)).scalar_one_or_none()
    if item is None:
        item = CanonicalTrackIdentity(canonical_track_id=canonical_track_id, identity_payload=payload, created_at=utcnow(), updated_at=utcnow())
        session.add(item)
    else:
        item.identity_payload = payload
        item.updated_at = utcnow()
    session.flush()
    return item

def list_canonical_track_identity_for_run(session, run_id: int):
    from chord.db.models import CanonicalTrackIdentity
    return list(session.execute(
        select(CanonicalTrackIdentity)
        .join(CanonicalTrack, CanonicalTrackIdentity.canonical_track_id == CanonicalTrack.id)
        .where(CanonicalTrack.run_id == run_id)
        .order_by(CanonicalTrackIdentity.id)
    ).scalars())


def replace_recommendation_set(session, run_id: int, mode: str, summary_payload: dict, items: list[dict]):
    from chord.db.models import RecommendationSet, RecommendationItem
    old_sets = list(session.execute(select(RecommendationSet).where(RecommendationSet.run_id == run_id, RecommendationSet.mode == mode)).scalars())
    for old in old_sets:
        session.execute(__import__("sqlalchemy").delete(RecommendationItem).where(RecommendationItem.recommendation_set_id == old.id))
        session.execute(__import__("sqlalchemy").delete(RecommendationSet).where(RecommendationSet.id == old.id))
    session.flush()

    rec_set = RecommendationSet(run_id=run_id, mode=mode, summary_payload=summary_payload, created_at=utcnow(), updated_at=utcnow())
    session.add(rec_set)
    session.flush()
    for item in items:
        session.add(RecommendationItem(
            recommendation_set_id=rec_set.id,
            canonical_track_id=item["canonical_track_id"],
            rank=item["rank"],
            final_score=item["final_score"],
            confidence_score=item["confidence_score"],
            mode=mode,
            score_breakdown=item["score_breakdown"],
            explanation_text=item["explanation_text"],
            created_at=utcnow(),
        ))
    session.commit()
    session.refresh(rec_set)
    return rec_set

def get_recommendation_set(session, run_id: int, mode: str):
    from chord.db.models import RecommendationSet
    return session.execute(select(RecommendationSet).where(RecommendationSet.run_id == run_id, RecommendationSet.mode == mode).order_by(RecommendationSet.id.desc())).scalar_one_or_none()

def list_recommendation_items(session, recommendation_set_id: int):
    from chord.db.models import RecommendationItem
    return list(session.execute(select(RecommendationItem).where(RecommendationItem.recommendation_set_id == recommendation_set_id).order_by(RecommendationItem.rank)).scalars())


def replace_curated_playlist_set(session, run_id: int, mode: str, requested_length: int, summary_payload: dict, items: list[dict]):
    from chord.db.models import CuratedPlaylistSet, CuratedPlaylistItem
    old_sets = list(session.execute(select(CuratedPlaylistSet).where(CuratedPlaylistSet.run_id == run_id, CuratedPlaylistSet.mode == mode)).scalars())
    for old in old_sets:
        session.execute(__import__("sqlalchemy").delete(CuratedPlaylistItem).where(CuratedPlaylistItem.curated_playlist_set_id == old.id))
        session.execute(__import__("sqlalchemy").delete(CuratedPlaylistSet).where(CuratedPlaylistSet.id == old.id))
    session.flush()

    cp_set = CuratedPlaylistSet(run_id=run_id, mode=mode, requested_length=requested_length, summary_payload=summary_payload, created_at=utcnow(), updated_at=utcnow())
    session.add(cp_set)
    session.flush()
    for item in items:
        session.add(CuratedPlaylistItem(
            curated_playlist_set_id=cp_set.id,
            canonical_track_id=item["canonical_track_id"],
            rank=item["rank"],
            source_type=item["source_type"],
            role_label=item.get("role_label"),
            inclusion_reason=item["inclusion_reason"],
            score_payload=item["score_payload"],
            created_at=utcnow(),
        ))
    session.commit()
    session.refresh(cp_set)
    return cp_set

def get_curated_playlist_set(session, run_id: int, mode: str):
    from chord.db.models import CuratedPlaylistSet
    return session.execute(select(CuratedPlaylistSet).where(CuratedPlaylistSet.run_id == run_id, CuratedPlaylistSet.mode == mode).order_by(CuratedPlaylistSet.id.desc())).scalar_one_or_none()

def list_curated_playlist_items(session, curated_playlist_set_id: int):
    from chord.db.models import CuratedPlaylistItem
    return list(session.execute(select(CuratedPlaylistItem).where(CuratedPlaylistItem.curated_playlist_set_id == curated_playlist_set_id).order_by(CuratedPlaylistItem.rank)).scalars())


def get_run(session, run_id: int):
    return session.get(Run, run_id)

def list_debug_artifacts_for_run(session, run_id: int):
    return list(session.execute(select(DebugArtifact).where(DebugArtifact.run_id == run_id).order_by(DebugArtifact.id)).scalars())

def delete_run_outputs(session, run_id: int):
    from chord.db.models import (
        RecommendationSet, RecommendationItem,
        CuratedPlaylistSet, CuratedPlaylistItem,
        IdentityProfile, CanonicalTrackIdentity,
        RunAggregate, CanonicalTrackAggregate,
        TrackEnrichment, RunEnrichmentSummary,
    )
    # recommendation sets
    rec_sets = list(session.execute(select(RecommendationSet).where(RecommendationSet.run_id == run_id)).scalars())
    for rs in rec_sets:
        session.execute(__import__("sqlalchemy").delete(RecommendationItem).where(RecommendationItem.recommendation_set_id == rs.id))
    session.execute(__import__("sqlalchemy").delete(RecommendationSet).where(RecommendationSet.run_id == run_id))
    # curated sets
    cp_sets = list(session.execute(select(CuratedPlaylistSet).where(CuratedPlaylistSet.run_id == run_id)).scalars())
    for cp in cp_sets:
        session.execute(__import__("sqlalchemy").delete(CuratedPlaylistItem).where(CuratedPlaylistItem.curated_playlist_set_id == cp.id))
    session.execute(__import__("sqlalchemy").delete(CuratedPlaylistSet).where(CuratedPlaylistSet.run_id == run_id))
    # identity
    session.execute(__import__("sqlalchemy").delete(IdentityProfile).where(IdentityProfile.run_id == run_id))
    ct_ids = [ct.id for ct in list_canonical_tracks_for_run(session, run_id)]
    if ct_ids:
        session.execute(__import__("sqlalchemy").delete(CanonicalTrackIdentity).where(CanonicalTrackIdentity.canonical_track_id.in_(ct_ids)))
        session.execute(__import__("sqlalchemy").delete(CanonicalTrackAggregate).where(CanonicalTrackAggregate.canonical_track_id.in_(ct_ids)))
        session.execute(__import__("sqlalchemy").delete(TrackEnrichment).where(TrackEnrichment.canonical_track_id.in_(ct_ids)))
    session.execute(__import__("sqlalchemy").delete(RunAggregate).where(RunAggregate.run_id == run_id))
    session.execute(__import__("sqlalchemy").delete(RunEnrichmentSummary).where(RunEnrichmentSummary.run_id == run_id))
    session.commit()

def delete_run_everything(session, run_id: int):
    run = get_run(session, run_id)
    if run is None:
        return
    delete_run_outputs(session, run_id)
    # remove quiz answers, track links, canonical tracks, tracks, playlists, uploads, artifacts, run
    session.execute(__import__("sqlalchemy").delete(QuizAnswer).where(QuizAnswer.run_id == run_id))
    ct_ids = [ct.id for ct in list_canonical_tracks_for_run(session, run_id)]
    if ct_ids:
        session.execute(__import__("sqlalchemy").delete(PlaylistTrackLink).where(PlaylistTrackLink.canonical_track_id.in_(ct_ids)))
        session.execute(__import__("sqlalchemy").delete(CanonicalTrack).where(CanonicalTrack.run_id == run_id))
    playlist_ids = [p.id for p in list_playlists_for_run(session, run_id)]
    if playlist_ids:
        session.execute(__import__("sqlalchemy").delete(Track).where(Track.playlist_id.in_(playlist_ids)))
        session.execute(__import__("sqlalchemy").delete(Playlist).where(Playlist.run_id == run_id))
    session.execute(__import__("sqlalchemy").delete(Upload).where(Upload.run_id == run_id))
    session.execute(__import__("sqlalchemy").delete(DebugArtifact).where(DebugArtifact.run_id == run_id))
    session.execute(__import__("sqlalchemy").delete(Run).where(Run.id == run_id))
    session.commit()


def replace_openai_enhancement_set(session, run_id: int, mode: str, enabled: bool, summary_payload: dict, items: list[dict]):
    from chord.db.models import OpenAIEnhancementSet, OpenAIEnhancementItem
    old_sets = list(session.execute(select(OpenAIEnhancementSet).where(OpenAIEnhancementSet.run_id == run_id, OpenAIEnhancementSet.mode == mode)).scalars())
    for old in old_sets:
        session.execute(__import__("sqlalchemy").delete(OpenAIEnhancementItem).where(OpenAIEnhancementItem.openai_enhancement_set_id == old.id))
        session.execute(__import__("sqlalchemy").delete(OpenAIEnhancementSet).where(OpenAIEnhancementSet.id == old.id))
    session.flush()

    oa_set = OpenAIEnhancementSet(run_id=run_id, mode=mode, enabled=enabled, summary_payload=summary_payload, created_at=utcnow(), updated_at=utcnow())
    session.add(oa_set)
    session.flush()
    for item in items:
        session.add(OpenAIEnhancementItem(
            openai_enhancement_set_id=oa_set.id,
            recommendation_item_id=item.get("recommendation_item_id"),
            rank=item["rank"],
            enhancement_type=item["enhancement_type"],
            enhanced_explanation_text=item["enhanced_explanation_text"],
            enhancement_payload=item["enhancement_payload"],
            created_at=utcnow(),
        ))
    session.commit()
    session.refresh(oa_set)
    return oa_set

def get_openai_enhancement_set(session, run_id: int, mode: str):
    from chord.db.models import OpenAIEnhancementSet
    return session.execute(select(OpenAIEnhancementSet).where(OpenAIEnhancementSet.run_id == run_id, OpenAIEnhancementSet.mode == mode).order_by(OpenAIEnhancementSet.id.desc())).scalar_one_or_none()

def list_openai_enhancement_items(session, openai_enhancement_set_id: int):
    from chord.db.models import OpenAIEnhancementItem
    return list(session.execute(select(OpenAIEnhancementItem).where(OpenAIEnhancementItem.openai_enhancement_set_id == openai_enhancement_set_id).order_by(OpenAIEnhancementItem.rank)).scalars())
