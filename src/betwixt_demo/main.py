"""Typer entry point for the Betwixt demonstrations."""

import types
from enum import StrEnum
from typing import Annotated

import snick
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm

from betwixt_demo.helpers import get_demo_functions, run_demo


class Feature(StrEnum):
    """Select one demonstration."""

    basics = "basics"
    constructs = "constructs"
    composition = "composition"
    pydantic = "pydantic"
    sqlalchemy = "sqlalchemy"
    combined = "combined"


def start(
    feature: Annotated[Feature | None, typer.Option(help="Feature to run")] = None,
    non_interactive: Annotated[bool, typer.Option("--non-interactive")] = False,
) -> None:
    """
    Run one named feature or all features.

    The interactive mode presents the selected demonstrations before running them. Use `--non-interactive` for
    unattended execution.
    """
    features = [feature] if feature is not None else list(Feature)
    feature_map: dict[Feature, list[types.FunctionType]] = {
        selected_feature: get_demo_functions(selected_feature.value) for selected_feature in features
    }
    features = [selected_feature for selected_feature in features if feature_map[selected_feature]]

    console = Console()
    greeting_lines = [
        "You are viewing the `betwixt` demo!",
        "",
        "This program shows Betwixt's declarative mapping features and what it is like to use them.",
        "",
        "The following features will be included:",
    ]
    for selected_feature in features:
        greeting_lines.append(f"- `{selected_feature}()`")
        for demo in feature_map[selected_feature]:
            greeting_lines.append(f"  - `{demo.__name__}()`")

    console.clear()
    console.print(
        Panel(
            Markdown(snick.conjoin(*greeting_lines)),
            padding=1,
            title="[green]Welcome to betwixt![/green]",
            title_align="left",
            subtitle="[blue]https://github.com/dusktreader/betwixt[/blue]",
            subtitle_align="left",
        )
    )
    console.print()
    console.print()
    if not non_interactive and not Confirm.ask("Would you like to continue?", default=True):
        return
    successful = True
    for selected_feature, functions in feature_map.items():
        for function in functions:
            result = run_demo(
                function, console, override_label=f"{selected_feature.value}()", interactive=not non_interactive
            )
            if not result:
                if non_interactive:
                    successful = False
                else:
                    return
    if not successful:
        raise typer.Exit(code=1)

    console.clear()
    console.print(
        Panel(
            Markdown(
                snick.dedent(
                    """
                    Thanks for checking out `betwixt`!

                    If you would like to learn more, please check out the
                    [documentation site](https://dusktreader.github.io/betwixt/).
                    """
                )
            ),
            padding=1,
            title="[green]Thanks![/green]",
            title_align="left",
            subtitle="[blue]https://github.com/dusktreader/betwixt[/blue]",
            subtitle_align="left",
        )
    )
    console.print()
    console.print()


def main() -> None:
    """Start the Typer command."""
    typer.run(start)


if __name__ == "__main__":
    main()
