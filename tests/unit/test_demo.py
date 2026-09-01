"""Unit tests for demo discovery, presentation, and selection."""

from collections.abc import Callable
from io import StringIO
from types import SimpleNamespace

import pytest

pytest.importorskip("rich")

from betwixt_demo import helpers
from betwixt_demo.features.basics import demo_builtin_mapping
from betwixt_demo.features.combined import demo_combined
from betwixt_demo.features.composition import demo_declaration_order
from betwixt_demo.features.constructs import (
    demo_expansion_constructs,
    demo_field_constructs,
    demo_nested_controls,
    demo_object_constructs,
)
from betwixt_demo.main import Feature, start
from rich.console import Console
from typer.testing import CliRunner

from betwixt import field_refs


def test_field_proxy_does_not_expose_dunder_fields() -> None:
    """Keep Python's special attribute lookup out of canonical field references."""
    with pytest.raises(AttributeError):
        dunder_name = "__demo__"
        getattr(field_refs(SimpleNamespace, SimpleNamespace)[0], dunder_name)


def test_discovery_returns_feature_demo_functions() -> None:
    """Discover only callable demo functions in stable order."""
    functions = helpers.get_demo_functions("basics")
    assert [function.__name__ for function in functions] == ["demo_builtin_mapping"]


def test_discovery_exposes_guided_feature_inventory() -> None:
    """Expose focused core demos and optional demos as separate feature groups."""
    assert [function.__name__ for function in helpers.get_demo_functions("constructs")] == [
        "demo_expansion_constructs",
        "demo_field_constructs",
        "demo_nested_controls",
        "demo_object_constructs",
    ]
    assert [function.__name__ for function in helpers.get_demo_functions("composition")] == ["demo_declaration_order"]
    assert [function.__name__ for function in helpers.get_demo_functions("pydantic")] == ["demo_pydantic"]
    assert [function.__name__ for function in helpers.get_demo_functions("sqlalchemy")] == ["demo_sqlalchemy"]
    assert [function.__name__ for function in helpers.get_demo_functions("combined")] == ["demo_combined"]


def test_discovery_skips_unavailable_optional_feature(monkeypatch: pytest.MonkeyPatch) -> None:
    """Skip an optional feature before importing its module when its extra is absent."""
    monkeypatch.setattr(helpers.importlib.util, "find_spec", lambda name: None if name == "pydantic" else object())
    assert helpers.get_demo_functions("pydantic") == []


@pytest.mark.parametrize("missing", ["pydantic", "sqlalchemy"])
def test_discovery_skips_combined_feature_when_dependency_is_unavailable(
    monkeypatch: pytest.MonkeyPatch, missing: str
) -> None:
    """Skip the combined feature unless both optional packages can be discovered."""
    monkeypatch.setattr(helpers.importlib.util, "find_spec", lambda name: None if name == missing else object())
    assert helpers.get_demo_functions("combined") == []


@pytest.mark.parametrize(
    "demo",
    [
        demo_builtin_mapping,
        demo_field_constructs,
        demo_expansion_constructs,
        demo_object_constructs,
        demo_nested_controls,
        demo_declaration_order,
        demo_combined,
    ],
)
def test_feature_demo_functions_execute_owned_scenarios(
    demo: Callable[[], None], capsys: pytest.CaptureFixture[str]
) -> None:
    """Execute each independently callable guided demo and verify meaningful output."""
    demo()
    output = capsys.readouterr().out
    assert output.strip()
    assert demo.__doc__


def test_combined_demo_uses_one_bidirectional_model_pipeline(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify both directional calls produce canonical ORM and aliased API output."""
    demo_combined()
    output = capsys.readouterr().out
    assert "'email': 'ada@example.com'" in output
    assert "'first_name': 'Ada'" in output
    assert "'last_name': 'Lovelace'" in output
    assert "'amount_cents': 12345" in output
    assert "'emailAddress': 'ada@example.com'" in output
    assert "'displayName': 'Ada Lovelace'" in output
    assert "'balanceDollars': 123.45" in output


def test_run_demo_renders_explanation_source_and_output() -> None:
    """Render the docstring, source, and captured stdout for a successful demo."""

    def demo_sample() -> None:
        """Explain the sample mapping."""
        print("sample output")

    console = Console(file=StringIO(), record=True, width=100, height=5)
    assert helpers.run_demo(demo_sample, console, interactive=False)
    output = console.export_text()
    assert "Explain the sample mapping." in output
    assert "sample output" in output
    assert "Here is the source code" in output


def test_run_demo_reports_captured_failure() -> None:
    """Stop after an exception and present its type and message."""

    def demo_failure() -> None:
        """Raise a deterministic demo failure."""
        raise ValueError("bad demo")

    console = Console(file=StringIO(), record=True, width=100, height=2)
    assert not helpers.run_demo(demo_failure, console, interactive=False)
    output = console.export_text()
    assert "ValueError" in output
    assert "bad demo" in output


def test_start_runs_named_feature_without_prompts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Select one feature and skip the interactive confirmation path."""
    seen: list[str] = []
    monkeypatch.setattr("betwixt_demo.main.get_demo_functions", lambda name: [SimpleNamespace(__name__=name)])
    monkeypatch.setattr(
        "betwixt_demo.main.run_demo", lambda function, console, **kwargs: seen.append(function.__name__) or True
    )
    start(Feature.constructs, non_interactive=True)
    assert seen == ["constructs"]


def test_start_runs_all_features_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run every registered feature when no selection is supplied."""
    seen: list[str] = []
    monkeypatch.setattr("betwixt_demo.main.get_demo_functions", lambda name: [SimpleNamespace(__name__=name)])
    monkeypatch.setattr(
        "betwixt_demo.main.run_demo", lambda function, console, **kwargs: seen.append(function.__name__) or True
    )
    start(None, non_interactive=True)
    assert seen == [feature.value for feature in Feature]


def test_start_exits_nonzero_for_captured_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return a nonzero result when a selected demo reports failure."""
    monkeypatch.setattr("betwixt_demo.main.get_demo_functions", lambda _: [SimpleNamespace(__name__="demo_failure")])
    monkeypatch.setattr("betwixt_demo.main.run_demo", lambda *args, **kwargs: False)
    import typer

    with pytest.raises(typer.Exit) as error:
        start(Feature.basics, non_interactive=True)
    assert error.value.exit_code == 1


def test_typer_rejects_invalid_feature() -> None:
    """Expose invalid feature names as a nonzero CLI result."""
    import typer

    app = typer.Typer()
    app.command()(start)
    result = CliRunner().invoke(app, ["--feature", "does-not-exist", "--non-interactive"])
    assert result.exit_code != 0
