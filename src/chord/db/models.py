from __future__ import annotations
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, BigInteger, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from chord.db.base import Base

class Run(Base):
    __tablename__ = "runs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(Text)
    mode: Mapped[str] = mapped_column(Text)
    debug_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

class Upload(Base):
    __tablename__ = "uploads"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"))
    source_kind: Mapped[str] = mapped_column(Text)
    original_filename: Mapped[str] = mapped_column(Text)
    stored_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    sha256: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Playlist(Base):
    __tablename__ = "playlists"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"))
    upload_id: Mapped[int | None] = mapped_column(ForeignKey("uploads.id", ondelete="SET NULL"), nullable=True)
    playlist_name: Mapped[str] = mapped_column(Text)
    playlist_kind: Mapped[str] = mapped_column(Text)
    source_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Track(Base):
    __tablename__ = "tracks"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id", ondelete="CASCADE"))
    source_row_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    artist: Mapped[str | None] = mapped_column(Text, nullable=True)
    album: Mapped[str | None] = mapped_column(Text, nullable=True)
    genre: Mapped[str | None] = mapped_column(Text, nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    play_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    skip_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date_added: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_kind: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class CanonicalTrack(Base):
    __tablename__ = "canonical_tracks"
    __table_args__ = (UniqueConstraint("run_id", "canonical_title", "canonical_artist", name="uq_canonical_tracks_run_title_artist"),)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"))
    canonical_title: Mapped[str] = mapped_column(Text)
    canonical_artist: Mapped[str] = mapped_column(Text)
    display_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_artist: Mapped[str | None] = mapped_column(Text, nullable=True)
    sample_album: Mapped[str | None] = mapped_column(Text, nullable=True)
    sample_genre: Mapped[str | None] = mapped_column(Text, nullable=True)
    sample_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    top25_anchor: Mapped[bool] = mapped_column(Boolean, default=False)
    playlist_occurrences: Mapped[int] = mapped_column(Integer, default=0)
    total_play_count: Mapped[int] = mapped_column(Integer, default=0)
    total_skip_count: Mapped[int] = mapped_column(Integer, default=0)
    rating_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    first_seen_playlist_kind: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class PlaylistTrackLink(Base):
    __tablename__ = "playlist_track_links"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    canonical_track_id: Mapped[int] = mapped_column(ForeignKey("canonical_tracks.id", ondelete="CASCADE"))
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class QuizAnswer(Base):
    __tablename__ = "quiz_answers"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"))
    quiz_version: Mapped[str] = mapped_column(Text)
    question_key: Mapped[str] = mapped_column(Text)
    answer_value: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class CuratorProfile(Base):
    __tablename__ = "curator_profiles"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), unique=True)
    quiz_version: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_seed: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class DebugArtifact(Base):
    __tablename__ = "debug_artifacts"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int | None] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), nullable=True)
    artifact_type: Mapped[str] = mapped_column(Text)
    artifact_path: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


from sqlalchemy import Float

class RunAggregate(Base):
    __tablename__ = "run_aggregates"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), unique=True)
    aggregate_payload: Mapped[dict] = mapped_column(JSONB)
    intake_quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class CanonicalTrackAggregate(Base):
    __tablename__ = "canonical_track_aggregates"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    canonical_track_id: Mapped[int] = mapped_column(ForeignKey("canonical_tracks.id", ondelete="CASCADE"), unique=True)
    aggregate_payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class TrackEnrichment(Base):
    __tablename__ = "track_enrichments"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    canonical_track_id: Mapped[int] = mapped_column(ForeignKey("canonical_tracks.id", ondelete="CASCADE"))
    source_name: Mapped[str] = mapped_column(Text)
    source_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    provenance_payload: Mapped[dict] = mapped_column(JSONB)
    data_payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class RunEnrichmentSummary(Base):
    __tablename__ = "run_enrichment_summaries"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), unique=True)
    summary_payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class IdentityProfile(Base):
    __tablename__ = "identity_profiles"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), unique=True)
    profile_payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class CanonicalTrackIdentity(Base):
    __tablename__ = "canonical_track_identity"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    canonical_track_id: Mapped[int] = mapped_column(ForeignKey("canonical_tracks.id", ondelete="CASCADE"), unique=True)
    identity_payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class RecommendationSet(Base):
    __tablename__ = "recommendation_sets"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"))
    mode: Mapped[str] = mapped_column(Text)
    summary_payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class RecommendationItem(Base):
    __tablename__ = "recommendation_items"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    recommendation_set_id: Mapped[int] = mapped_column(ForeignKey("recommendation_sets.id", ondelete="CASCADE"))
    canonical_track_id: Mapped[int] = mapped_column(ForeignKey("canonical_tracks.id", ondelete="CASCADE"))
    rank: Mapped[int] = mapped_column(Integer)
    final_score: Mapped[float] = mapped_column(nullable=False)
    confidence_score: Mapped[float] = mapped_column(nullable=False)
    mode: Mapped[str] = mapped_column(Text)
    score_breakdown: Mapped[dict] = mapped_column(JSONB)
    explanation_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CuratedPlaylistSet(Base):
    __tablename__ = "curated_playlist_sets"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"))
    mode: Mapped[str] = mapped_column(Text)
    requested_length: Mapped[int] = mapped_column(Integer)
    summary_payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class CuratedPlaylistItem(Base):
    __tablename__ = "curated_playlist_items"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    curated_playlist_set_id: Mapped[int] = mapped_column(ForeignKey("curated_playlist_sets.id", ondelete="CASCADE"))
    canonical_track_id: Mapped[int] = mapped_column(ForeignKey("canonical_tracks.id", ondelete="CASCADE"))
    rank: Mapped[int] = mapped_column(Integer)
    source_type: Mapped[str] = mapped_column(Text)
    role_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    inclusion_reason: Mapped[str] = mapped_column(Text)
    score_payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class OpenAIEnhancementSet(Base):
    __tablename__ = "openai_enhancement_sets"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"))
    mode: Mapped[str] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    summary_payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class OpenAIEnhancementItem(Base):
    __tablename__ = "openai_enhancement_items"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    openai_enhancement_set_id: Mapped[int] = mapped_column(ForeignKey("openai_enhancement_sets.id", ondelete="CASCADE"))
    recommendation_item_id: Mapped[int | None] = mapped_column(ForeignKey("recommendation_items.id", ondelete="SET NULL"), nullable=True)
    rank: Mapped[int] = mapped_column(Integer)
    enhancement_type: Mapped[str] = mapped_column(Text)
    enhanced_explanation_text: Mapped[str] = mapped_column(Text)
    enhancement_payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
