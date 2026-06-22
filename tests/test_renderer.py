from rich.console import Console

import toefl_rpg.cli.renderer as renderer_module
from toefl_rpg.cli.renderer import Renderer
from toefl_rpg.engine.state import TurnResult


class RecordingPlainConsole:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def print(self, value: object = "") -> None:
        self.lines.append(str(value))


def test_renderer_shows_result_and_english_feedback_as_separate_panels() -> None:
    console = Console(record=True, width=100, color_system=None)
    renderer = Renderer(console)
    result = TurnResult(
        success=True,
        message="You collect the fungus sample.",
        english_feedback=(
            "Narration: The grove stays damp.\n"
            "Feedback: Use a clear verb after 'I want'.\n"
            "Try: I want to collect the fungus sample.\n"
            "Vocabulary: fungus means a growth that can affect an ecosystem."
        ),
    )

    renderer.show_result(result)

    output = console.export_text()
    assert "Result" in output
    assert "English Feedback" in output
    assert output.index("You collect the fungus sample.") < output.index(
        "English Feedback"
    )
    assert output.index("Narration: The grove stays damp.") > output.index(
        "English Feedback"
    )
    assert output.count("You collect the fungus sample.") == 1


def test_plain_console_result_and_feedback_keep_separate_labels(monkeypatch) -> None:
    monkeypatch.setattr(renderer_module, "Panel", None)
    console = RecordingPlainConsole()
    renderer = Renderer(console)
    result = TurnResult(
        success=False,
        message="You cannot go north from here.",
        english_feedback=(
            "Narration: AI narration for move.\n"
            "Feedback: Try a reachable direction."
        ),
    )

    renderer.show_result(result)

    assert console.lines == [
        "Result: You cannot go north from here.",
        "English Feedback: Narration: AI narration for move.\n"
        "Feedback: Try a reachable direction.",
    ]
    assert console.lines[0].startswith("Result:")
    assert console.lines[1].startswith("English Feedback:")


def test_renderer_keeps_multiple_vocabulary_notes_distinct_in_feedback() -> None:
    console = Console(record=True, width=100, color_system=None)
    renderer = Renderer(console)
    result = TurnResult(
        success=True,
        message="You collect the fungus sample.",
        english_feedback=(
            "Narration: The grove stays damp.\n"
            "Feedback: Use a clear verb after 'I want'.\n"
            "Try: I want to collect the fungus sample.\n"
            "Vocabulary: fungus: a growth that can affect an ecosystem.\n"
            "Vocabulary: vital: necessary for survival."
        ),
    )

    renderer.show_result(result)

    output = console.export_text()
    assert output.index("You collect the fungus sample.") < output.index(
        "English Feedback"
    )
    assert output.index("Vocabulary: fungus: a growth") > output.index(
        "English Feedback"
    )
    assert output.index("Vocabulary: vital: necessary") > output.index(
        "Vocabulary: fungus: a growth"
    )
    assert output.count("Vocabulary:") == 2
    assert output.count("You collect the fungus sample.") == 1


def test_renderer_keeps_parser_miss_retry_guidance_in_result_panel() -> None:
    console = Console(record=True, width=100, color_system=None)
    renderer = Renderer(console)
    result = TurnResult(
        success=False,
        message=(
            "I could not confidently turn that sentence into a game action. "
            "Try a clearer sentence for collect."
        ),
        english_feedback=(
            "Narration: AI narration for unknown.\n"
            "Feedback: AI feedback: your sentence is understandable.\n"
            "Try: Could you handle the thing for me?\n"
            "Vocabulary: Practiced: no target word."
        ),
    )

    renderer.show_result(result)

    output = console.export_text()
    assert "Result" in output
    assert "English Feedback" in output
    assert "Try a clearer sentence for" in output
    assert "collect." in output
    assert output.index("Try a clearer sentence for") < output.index(
        "English Feedback"
    )
    assert output.index("Narration: AI narration for unknown.") > output.index(
        "English Feedback"
    )
    assert output.count("Try a clearer sentence for") == 1


def test_renderer_keeps_rejected_action_result_separate_from_ai_feedback() -> None:
    console = Console(record=True, width=100, color_system=None)
    renderer = Renderer(console)
    result = TurnResult(
        success=False,
        message="You cannot go north from here.",
        english_feedback=(
            "Narration: AI narration for move.\n"
            "Feedback: AI feedback: your sentence is clear, but the path is blocked.\n"
            "Try: I go east to the microscope tent.\n"
            "Vocabulary: Practiced: no target word."
        ),
    )

    renderer.show_result(result)

    output = console.export_text()
    assert "Result" in output
    assert "English Feedback" in output
    assert output.index("You cannot go north from here.") < output.index(
        "English Feedback"
    )
    assert output.index("Narration: AI narration for move.") > output.index(
        "English Feedback"
    )
    assert output.index("Try: I go east to the microscope tent.") > output.index(
        "English Feedback"
    )
    assert output.count("You cannot go north from here.") == 1


def test_renderer_keeps_review_rejection_lines_in_result_panel() -> None:
    console = Console(record=True, width=100, color_system=None)
    renderer = Renderer(console)
    result = TurnResult(
        success=False,
        message=(
            "AI advice: The sentence names the word but does not show its meaning.\n"
            "Try: A fungus can decompose wood in a forest.\n"
            "Result: Review needs another try. No XP awarded; 'fungus' remains active for review."
        ),
        english_feedback=(
            "Narration: AI narration for unknown.\n"
            "Feedback: AI feedback: your sentence is understandable.\n"
            "Try: The word fungus appears in my sentence.\n"
            "Vocabulary: Practiced: no target word."
        ),
    )

    renderer.show_result(result)

    output = console.export_text()
    assert "Result" in output
    assert "English Feedback" in output
    assert output.index("AI advice: The sentence names the word") < output.index(
        "English Feedback"
    )
    assert output.index("Try: A fungus can decompose wood") < output.index(
        "English Feedback"
    )
    assert output.index("Result: Review needs another try.") < output.index(
        "English Feedback"
    )
    assert output.index("Narration: AI narration for unknown.") > output.index(
        "English Feedback"
    )
    assert output.count("Result: Review needs another try.") == 1


def test_renderer_keeps_vocabulary_explanation_in_result_without_feedback_panel() -> None:
    console = Console(record=True, width=100, color_system=None)
    renderer = Renderer(console)
    result = TurnResult(
        success=True,
        message=(
            "fungus: A living growth such as mold or mushrooms.\n"
            "Example: A fungus can recycle nutrients in a forest.\n"
            "Memory hint: Connect fungus with forest mushrooms."
        ),
    )

    renderer.show_result(result)

    output = console.export_text()
    assert "Result" in output
    assert output.count("English Feedback") == 0
    assert output.index("Result") < output.index(
        "fungus: A living growth such as mold or mushrooms."
    )
    assert output.index("Result") < output.index(
        "Example: A fungus can recycle nutrients in a forest."
    )
    assert output.index("Result") < output.index(
        "Memory hint: Connect fungus with forest mushrooms."
    )
    assert "fungus: A living growth such as mold or mushrooms." in output
    assert "Example: A fungus can recycle nutrients in a forest." in output
    assert "Memory hint: Connect fungus with forest mushrooms." in output
