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
