# CHORD Real-Data Smoke Test Inputs

Branch: `testing/github-preinstall-checker`

This directory is reserved for temporary real-data smoke test inputs.

Do not commit personal playlist exports to `main`.

## Preferred input layout

Use this layout when both a Top 25 export and playlist exports are available:

```text
tests/real_data/top25_real.txt
tests/real_data/playlists/playlist_real_1.txt
tests/real_data/playlists/playlist_real_2.txt
```

## Single-file fallback

For the first real-data execution test, a single uploaded playlist can be placed at:

```text
tests/real_data/playlist_real.txt
```

When `CHORD_REALDATA_ALLOW_SINGLE_FILE_AS_TOP25=1`, the real-data smoke script will use that file as both the Top 25 input and the playlist input. This fallback proves real-file import and result generation, but it is not as representative as using a true Top 25 export plus one or more playlists.

## Quiz answers

Use:

```text
tests/real_data/quiz_answers.json
```

The required keys are:

```json
{
  "project_type": "generation_soundtrack",
  "recommendation_mistake": "same_artist",
  "recommendation_goal": "tasteful_surprises",
  "belonging_rule": "same_kind_of_person",
  "balance_preference": "balanced",
  "avoid_false_positive": "technically_similar_but_wrong"
}
```

Replace the values with the user's real quiz answers before running the real-data smoke test.

## Privacy note

Files in this directory may contain personal music-library information. Keep them on the isolated testing branch unless the user explicitly approves promotion.
