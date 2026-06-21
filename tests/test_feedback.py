from toefl_rpg.language.feedback import evaluate_english


def test_feedback_accepts_short_commands() -> None:
    assert evaluate_english("go north") == (
        "Short command accepted. Try a full sentence for better practice."
    )


def test_feedback_corrects_missing_to_after_want() -> None:
    assert evaluate_english("I want collect the sample") == "Better English: I want to collect ..."
    assert evaluate_english("I want go north") == "Better English: I want to go ..."


def test_feedback_corrects_talk_to_pattern() -> None:
    assert evaluate_english("talk researcher") == (
        "Better English: Use 'talk to someone', for example: talk to Dr. Lin."
    )


def test_feedback_marks_full_sentence() -> None:
    assert evaluate_english("The fungus is vital for the old forest.") == (
        "Good: you used a full sentence."
    )
