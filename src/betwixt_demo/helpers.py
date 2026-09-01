"""Helper functions for running demos."""

from __future__ import annotations

import ast
import importlib.util
import inspect
import io
import re
import sys
import tempfile
import textwrap
import types
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path

import snick
from rich import box
from rich.console import Console, Group, RenderableType
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm
from rich.rule import Rule


@dataclass
class Decomposed:
    """Decomposed function information for demo display."""

    module: str
    name: str
    docstring: str
    source: str


@dataclass
class Captured:
    """Captured output from running a demo function."""

    error: Exception | None = None
    stdout: str | None = None
    stderr: str | None = None
    exit_code: int | str | None = None
    settings: str | None = None


BlankLine = Rule(characters=" ")


def pseudo_clear(console: Console):
    """Clear the console by printing blank lines."""
    for _ in range(console.size.height):
        console.print(BlankLine)


def fake_input(text: str):
    """Inject fake input into stdin for testing."""
    sys.stdin.write(text)
    sys.stdin.seek(0)


def get_demo_functions(module_name: str) -> list[types.FunctionType]:
    """
    Get all demo functions from a module.

    Args:
        module_name: Name of the module to search for demo functions

    Returns:
        List of demo functions sorted by name
    """
    optional_dependencies = {
        "pydantic": ("pydantic",),
        "sqlalchemy": ("sqlalchemy",),
        "combined": ("pydantic", "sqlalchemy"),
    }.get(module_name)
    if optional_dependencies is not None and any(
        importlib.util.find_spec(dependency) is None for dependency in optional_dependencies
    ):
        return []
    demo_functions: list[types.FunctionType] = []
    module = import_module(f"betwixt_demo.features.{module_name}")
    for _, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and obj.__name__.startswith("demo"):
            demo_functions.append(obj)
    return sorted(demo_functions, key=lambda f: f.__name__)


def decompose(func: types.FunctionType) -> Decomposed:
    """
    Decompose a function into its parts for display.

    This is really hacky. Maybe improve this sometime.

    Args:
        func: The function to decompose

    Returns:
        Decomposed function information

    Raises:
        RuntimeError: If the function has no docstring or can't be decomposed
    """
    module = func.__module__.split(".")[-1]
    name = func.__name__

    if func.__doc__ is None:
        raise RuntimeError("Can't demo a function with no docstring!")
    docstring = textwrap.dedent(func.__doc__).strip()
    source_lines, _ = inspect.getsourcelines(func)
    source_text = textwrap.dedent("".join(source_lines))
    syntax_tree = ast.parse(source_text)
    function_node = syntax_tree.body[0]
    if not isinstance(function_node, (ast.FunctionDef, ast.AsyncFunctionDef)) or not function_node.body:
        raise RuntimeError("Failed to strip function declaration and docstring!")
    body = (
        function_node.body[1:]
        if isinstance(function_node.body[0], ast.Expr)
        and isinstance(function_node.body[0].value, ast.Constant)
        and isinstance(function_node.body[0].value.value, str)
        else function_node.body
    )
    if not body:
        source = "pass\n"
    else:
        source = "\n".join(ast.get_source_segment(source_text, statement) or "" for statement in body) + "\n"
    source = re.sub(r"\s+# (?:pyright|type).*", "", source)

    return Decomposed(module=module, name=name, docstring=docstring, source=source)


def capture(demo: types.FunctionType) -> Captured:
    """
    Capture the output of running a demo function.

    Args:
        demo: The demo function to run

    Returns:
        Captured output from the demo function
    """
    demo_name = demo.__name__

    cap = Captured()

    stdout_buffer = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = stdout_buffer

    stderr_buffer = io.StringIO()
    original_stderr = sys.stderr
    sys.stderr = stderr_buffer

    stdin_buffer = io.StringIO()
    original_stdin = sys.stdin
    sys.stdin = stdin_buffer

    original_argv = sys.argv
    sys.argv = [demo_name]

    with tempfile.TemporaryDirectory() as fake_home:
        fake_settings_dir = Path(fake_home) / ".local/share" / demo_name
        fake_settings_dir.mkdir(parents=True)
        fake_settings_path = fake_settings_dir / "settings.json"
        try:
            demo()
        except SystemExit as exited:
            cap.exit_code = exited.code
        except Exception as exc:  # noqa: BLE001 - capture demo failures for display
            cap.error = exc
        finally:
            if fake_settings_path.exists():
                cap.settings = fake_settings_path.read_text()
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            sys.stdin = original_stdin
            sys.argv = original_argv

    stdout_dump = stdout_buffer.getvalue()
    if stdout_dump:
        cap.stdout = stdout_dump

    stderr_dump = stderr_buffer.getvalue()
    if stderr_dump:
        cap.stderr = stderr_dump

    return cap


def run_demo(
    demo: types.FunctionType, console: Console, override_label: str | None = None, *, interactive: bool = True
) -> bool:
    """
    Run a demo function and display its output.

    Args:
        demo: The demo function to run
        console: Rich console for output
        override_label: Optional override for the demo label

    Returns:
        True if the user wants to continue, False otherwise
    """
    pseudo_clear(console)

    decomposed = decompose(demo)
    cap: Captured = capture(demo)

    parts: list[RenderableType] = [
        Markdown(decomposed.docstring),
        BlankLine,
        BlankLine,
        Panel(
            Markdown(f"```python\n{decomposed.source}\n```"),
            title=f"Here is the source code for [yellow]{decomposed.name}()[/yellow]",
            title_align="left",
            padding=1,
            expand=False,
            box=box.SIMPLE,
        ),
    ]

    if cap.stdout:
        parts.extend(
            [
                BlankLine,
                BlankLine,
                Panel(
                    Markdown(
                        snick.conjoin("```text", cap.stdout, "```"),
                    ),
                    title=f"Here is the stdout captured from [yellow]{decomposed.name}()[/yellow]",
                    title_align="left",
                    padding=1,
                    expand=False,
                    box=box.SIMPLE,
                ),
            ]
        )

    if cap.stderr:
        parts.extend(
            [
                BlankLine,
                BlankLine,
                Panel(
                    Markdown(
                        snick.conjoin("```text", cap.stderr, "```"),
                    ),
                    title=f"Here is the stderr captured from [yellow]{decomposed.name}()[/yellow]",
                    title_align="left",
                    padding=1,
                    expand=False,
                    box=box.SIMPLE,
                ),
            ]
        )

    if cap.error:
        parts.extend(
            [
                BlankLine,
                BlankLine,
                Panel(
                    f"[red]{cap.error.__class__.__name__}[/red]: [yellow]{cap.error!s}[/yellow]",
                    title=f"Here is the uncaught exception from [yellow]{decomposed.name}()[/yellow]",
                    title_align="left",
                    padding=1,
                    expand=False,
                    box=box.SIMPLE,
                ),
            ]
        )

    if cap.exit_code is not None:
        parts.extend(
            [
                BlankLine,
                BlankLine,
                Panel(
                    Markdown(
                        snick.conjoin("```text", str(cap.exit_code), "```"),
                    ),
                    title=f"Here is the exit code from [yellow]{decomposed.name}()[/yellow]",
                    title_align="left",
                    padding=1,
                    expand=False,
                    box=box.SIMPLE,
                ),
            ]
        )

    if cap.settings is not None:
        parts.extend(
            [
                BlankLine,
                BlankLine,
                Panel(
                    Markdown(
                        snick.conjoin("```json", cap.settings, "```"),
                    ),
                    title=f"Here are the final contents of the settings file from [yellow]{decomposed.name}()[/yellow]",
                    title_align="left",
                    padding=1,
                    expand=False,
                    box=box.SIMPLE,
                ),
            ]
        )

    label = override_label if override_label else f"{decomposed.module}()"
    console.print(
        Panel(
            Group(*parts),
            padding=1,
            title=f"Showing [yellow]{decomposed.name}()[/yellow] for [green]{label}[/green]",
            title_align="left",
            subtitle="[blue]https://github.com/dusktreader/betwixt[/blue]",
            subtitle_align="left",
        ),
    )
    console.print(BlankLine)
    console.print(BlankLine)
    if cap.error is not None or cap.exit_code not in (None, 0):
        return False
    if not interactive:
        return True
    further: bool = Confirm.ask("Would you like to continue?", default=True)
    return further
