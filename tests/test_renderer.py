from rich.console import Console

from toefl_rpg.cli.renderer import Renderer
from toefl_rpg.engine.state import TurnResult


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


def test_renderer_keeps_vocabulary_explanation_lines_in_result_panel() -> None:
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
    assert "English Feedback" not in output
    assert "fungus: A living growth such as mold or mushrooms." in output
    assert "Example: A fungus can recycle nutrients in a forest." in output
    assert "Memory hint: Connect fungus with forest mushrooms." in output
