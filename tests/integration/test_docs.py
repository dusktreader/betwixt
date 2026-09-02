"""Integration checks for the built Zensical site."""

import inspect
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
DOCS = ROOT / "docs" / "source"


@pytest.mark.integration
def test_zensical_builds_the_documented_api() -> None:
    """Build the site and verify that mkdocstrings rendered the public API."""
    subprocess.run(["make", "docs/build"], cwd=ROOT, check=True, capture_output=True, text=True)
    assert (ROOT / "docs/site/index.html").is_file()
    index = (ROOT / "docs/site/index.html").read_text()
    assert 'href="stylesheets/extra.css"' in index
    assert '<img src="static/icon.png" alt="logo">' in index
    assert '<link rel="icon" href="static/icon.png">' in index
    assert 'aria-label="Switch to dark mode"' in index
    assert 'aria-label="Switch to light mode"' in index
    assert (ROOT / "docs/site/static/icon.png").is_file()
    stylesheet = (ROOT / "docs/site/stylesheets/extra.css").read_text()
    assert '[data-md-color-scheme="default"]' in stylesheet
    assert '[data-md-color-scheme="slate"]' in stylesheet
    assert stylesheet.count("--md-primary-fg-color: #17233f;") == 2
    assert stylesheet.count("--md-primary-bg-color: #ffffff;") == 2
    assert '[data-md-color-scheme="slate"] .md-nav__item--section > .md-nav__link' in stylesheet
    for color in ("#17233f", "#6d28d9", "#8b5cf6", "#047857", "#34d399"):
        assert color in stylesheet
    not_found = (ROOT / "docs/site/404.html").read_text()
    assert 'href="/betwixt/stylesheets/extra.css"' in not_found
    assert 'src="/betwixt/static/icon.png"' in not_found
    api = (ROOT / "docs/site/api-reference/index.html").read_text()
    assert "Betwixt" in api
    assert "field_refs" in api
    from betwixt.constructs import (
        disable_implicit_leftward,
        disable_implicit_pairwise,
        disable_implicit_rightward,
        expand_leftward,
        expand_rightward,
        map_leftward,
        map_pairwise,
        map_rightward,
        nested_leftward,
        nested_pairwise,
        nested_rightward,
        project_leftward,
        project_rightward,
        reduce_leftward,
        reduce_rightward,
    )

    constructs = (
        map_pairwise,
        map_rightward,
        map_leftward,
        expand_rightward,
        expand_leftward,
        reduce_rightward,
        reduce_leftward,
        project_rightward,
        project_leftward,
        nested_pairwise,
        nested_rightward,
        nested_leftward,
        disable_implicit_pairwise,
        disable_implicit_rightward,
        disable_implicit_leftward,
    )

    for construct in constructs:
        assert construct.__name__ in api
        signature = inspect.signature(construct)
        assert all(parameter in api for parameter in signature.parameters)


@pytest.mark.integration
def test_documentation_navigation_pages_are_complete() -> None:
    """Require every conceptual page to contain a runnable fenced example."""
    pages = [
        "index.md",
        "quickstart.md",
        "concepts.md",
        "features.md",
        "examples.md",
        "cases/index.md",
        "cases/user.md",
        "cases/payment.md",
        "cases/order.md",
        "adapters.md",
        "comparison.md",
        "api-reference.md",
    ]
    for page in pages:
        content = (DOCS / page).read_text()
        assert content.startswith("# "), page
        if page not in ("api-reference.md", "cases/index.md"):
            assert "```" in content, page

    combined = " ".join("\n".join((DOCS / page).read_text() for page in pages).split())
    for phrase in ("rightward_partial", "explain_rightward", "UnmappedFieldError", "canonical", "persistence"):
        assert phrase in combined
    for stale_name in ('"amount"', '"lines"', "orm_user", "user_mapping.rightward"):
        assert stale_name not in combined


@pytest.mark.integration
def test_guided_construct_documentation_example_executes() -> None:
    """Keep the guided core construct example executable."""
    from betwixt_demo.features.constructs import demo_expansion_constructs

    demo_expansion_constructs()


@pytest.mark.integration
def test_documentation_contains_the_complete_semantic_contract() -> None:
    """Require the conceptual pages to describe behavior, not merely contain code fences."""
    concepts = " ".join((DOCS / "concepts.md").read_text().split())
    features = " ".join((DOCS / "features.md").read_text().split())
    user = (DOCS / "cases/user.md").read_text()
    order = (DOCS / "cases/order.md").read_text()

    for family in ("Maps", "Reductions", "Projections", "Nested", "Controls"):
        assert f"| {family}" in concepts
    assert concepts.count("| `") >= 6
    assert "exactly seventeen factories" in concepts
    assert "Pydantic aliases" in concepts
    assert "does not validate or coerce" in concepts
    for construct in (
        "expand_rightward",
        "expand_leftward",
        "map_pairwise",
        "map_rightward",
        "map_leftward",
        "reduce_rightward",
        "reduce_leftward",
        "project_rightward",
        "project_leftward",
        "nested_pairwise",
        "nested_rightward",
        "nested_leftward",
        "disable_implicit_pairwise",
        "disable_implicit_rightward",
        "disable_implicit_leftward",
    ):
        assert construct in concepts
    for phrase in ("canonical", "reference order", "class-body order", "keyword-only", "ctx=", "CurrencyContext"):
        assert phrase in concepts
    for phrase in (
        "optional",
        "variadic tuple",
        "fixed tuple",
        "dictionary",
        "set",
        "Empty containers",
        "container path",
        "present `None`",
        "UnmappedFieldError",
    ):
        assert phrase in features
    assert "required default" not in user
    assert "canonical Python attribute" in user
    assert "contains an `identifier`" in order
    assert "does not contain a customer field" in order
    assert "context derivation" in order

    from betwixt_demo.features.basics import demo_builtin_mapping

    demo_builtin_mapping()
