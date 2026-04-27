from chord.constants import QUIZ_VERSION

QUIZ_QUESTIONS = [
    {
        "key": "project_type",
        "question": "What best describes this playlist project?",
        "options": ["life_map", "generation_soundtrack", "reliable_songs", "moods_memories_styles"],
    },
    {
        "key": "recommendation_mistake",
        "question": "Which recommendation mistake bothers you most?",
        "options": ["same_artist", "one_era", "similar_but_wrong", "too_obvious"],
    },
    {
        "key": "recommendation_goal",
        "question": "Which kind of recommendation do you want most?",
        "options": ["missing_essentials", "different_artist_right", "cross_era_same_role", "tasteful_surprises"],
    },
    {
        "key": "belonging_rule",
        "question": "What matters most when very different songs still belong together?",
        "options": ["same_mood", "same_era", "same_familiarity", "same_kind_of_person"],
    },
    {
        "key": "balance_preference",
        "question": "Which balance do you prefer?",
        "options": ["mostly_familiar", "familiar_some_discovery", "balanced", "adventurous_but_fits"],
    },
    {
        "key": "avoid_false_positive",
        "question": "What type of false positive should the tool avoid most?",
        "options": ["too_heavy", "too_obvious", "technically_similar_but_wrong", "repeat_of_existing"],
    },
]

def get_quiz_definition():
    return {"version": QUIZ_VERSION, "questions": QUIZ_QUESTIONS}

def build_profile_seed(answers: dict[str, str]) -> dict:
    return {
        "quiz_version": QUIZ_VERSION,
        "answers": answers,
        "curator_identity_weight": "high",
        "top25_anchor_weight": "high",
        "boundary_model_enabled": True,
        "portable_profile_ready": True,
    }
