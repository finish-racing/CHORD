# CHORD Known Risks for Final Ubuntu Test

## Environment risks
- PostgreSQL connection string mismatch
- missing OS package dependency
- systemd service path mismatch
- Nginx reverse proxy config not enabled

## Data and pipeline risks
- edge-case iTunes/Apple TXT formatting
- incomplete or sparse playlist metadata
- external API rate limits or connectivity issues
- missing OpenAI key when enhancement is enabled

## UX and operability risks
- dashboard may be dense with raw JSON in some panels
- very large playlists may create slower runs before later optimization
- debug mode may generate many artifacts if left enabled continuously

## Recovery risks
- operator may need rollback if a later deployment modifies runtime behavior
- soft/hard reset use should be deliberate to avoid clearing desired state
