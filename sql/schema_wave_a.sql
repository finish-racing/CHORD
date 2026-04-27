CREATE TABLE IF NOT EXISTS runs (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL,
    mode TEXT NOT NULL DEFAULT 'analysis',
    debug_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS uploads (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    source_kind TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    stored_path TEXT,
    file_size_bytes BIGINT,
    sha256 TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS playlists (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    upload_id BIGINT REFERENCES uploads(id) ON DELETE SET NULL,
    playlist_name TEXT NOT NULL,
    playlist_kind TEXT NOT NULL,
    source_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tracks (
    id BIGSERIAL PRIMARY KEY,
    playlist_id BIGINT NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
    source_row_number INTEGER NOT NULL,
    title TEXT,
    artist TEXT,
    album TEXT,
    genre TEXT,
    year INTEGER,
    rating INTEGER,
    play_count INTEGER,
    skip_count INTEGER,
    date_added TEXT,
    media_kind TEXT,
    raw_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS canonical_tracks (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    canonical_title TEXT NOT NULL,
    canonical_artist TEXT NOT NULL,
    display_title TEXT,
    display_artist TEXT,
    sample_album TEXT,
    sample_genre TEXT,
    sample_year INTEGER,
    top25_anchor BOOLEAN NOT NULL DEFAULT FALSE,
    playlist_occurrences INTEGER NOT NULL DEFAULT 0,
    total_play_count INTEGER NOT NULL DEFAULT 0,
    total_skip_count INTEGER NOT NULL DEFAULT 0,
    rating_max INTEGER,
    first_seen_playlist_kind TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_canonical_tracks_run_title_artist
ON canonical_tracks(run_id, canonical_title, canonical_artist);

CREATE TABLE IF NOT EXISTS playlist_track_links (
    id BIGSERIAL PRIMARY KEY,
    canonical_track_id BIGINT NOT NULL REFERENCES canonical_tracks(id) ON DELETE CASCADE,
    track_id BIGINT NOT NULL REFERENCES tracks(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS quiz_answers (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    quiz_version TEXT NOT NULL,
    question_key TEXT NOT NULL,
    answer_value TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS curator_profiles (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL UNIQUE REFERENCES runs(id) ON DELETE CASCADE,
    quiz_version TEXT,
    profile_seed JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS debug_artifacts (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT REFERENCES runs(id) ON DELETE CASCADE,
    artifact_type TEXT NOT NULL,
    artifact_path TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS run_aggregates (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL UNIQUE REFERENCES runs(id) ON DELETE CASCADE,
    aggregate_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    intake_quality_score DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS canonical_track_aggregates (
    id BIGSERIAL PRIMARY KEY,
    canonical_track_id BIGINT NOT NULL UNIQUE REFERENCES canonical_tracks(id) ON DELETE CASCADE,
    aggregate_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS track_enrichments (
    id BIGSERIAL PRIMARY KEY,
    canonical_track_id BIGINT NOT NULL REFERENCES canonical_tracks(id) ON DELETE CASCADE,
    source_name TEXT NOT NULL,
    source_key TEXT,
    status TEXT NOT NULL,
    confidence_score DOUBLE PRECISION,
    provenance_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    data_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS run_enrichment_summaries (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL UNIQUE REFERENCES runs(id) ON DELETE CASCADE,
    summary_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS identity_profiles (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL UNIQUE REFERENCES runs(id) ON DELETE CASCADE,
    profile_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS canonical_track_identity (
    id BIGSERIAL PRIMARY KEY,
    canonical_track_id BIGINT NOT NULL UNIQUE REFERENCES canonical_tracks(id) ON DELETE CASCADE,
    identity_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS recommendation_sets (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    mode TEXT NOT NULL,
    summary_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS recommendation_items (
    id BIGSERIAL PRIMARY KEY,
    recommendation_set_id BIGINT NOT NULL REFERENCES recommendation_sets(id) ON DELETE CASCADE,
    canonical_track_id BIGINT NOT NULL REFERENCES canonical_tracks(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL,
    final_score DOUBLE PRECISION NOT NULL,
    confidence_score DOUBLE PRECISION NOT NULL,
    mode TEXT NOT NULL,
    score_breakdown JSONB NOT NULL DEFAULT '{}'::jsonb,
    explanation_text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS curated_playlist_sets (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    mode TEXT NOT NULL,
    requested_length INTEGER NOT NULL,
    summary_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS curated_playlist_items (
    id BIGSERIAL PRIMARY KEY,
    curated_playlist_set_id BIGINT NOT NULL REFERENCES curated_playlist_sets(id) ON DELETE CASCADE,
    canonical_track_id BIGINT NOT NULL REFERENCES canonical_tracks(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    role_label TEXT,
    inclusion_reason TEXT NOT NULL,
    score_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS openai_enhancement_sets (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    mode TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    summary_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS openai_enhancement_items (
    id BIGSERIAL PRIMARY KEY,
    openai_enhancement_set_id BIGINT NOT NULL REFERENCES openai_enhancement_sets(id) ON DELETE CASCADE,
    recommendation_item_id BIGINT REFERENCES recommendation_items(id) ON DELETE SET NULL,
    rank INTEGER NOT NULL,
    enhancement_type TEXT NOT NULL,
    enhanced_explanation_text TEXT NOT NULL,
    enhancement_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
