# Hack journal

This journal records the bounded documentation theme update.


## Files changed

- `docs/zensical.toml`
- `docs/source/stylesheets/extra.css`
- `tests/integration/test_project_config.py`
- `.artifacts/20260902--betwixt-theme/hack-journal.md`

The existing `docs/source/static/logo.svg` and `logo.png` assets were preserved unchanged.


## Intent

Configure Zensical's light and dark palette controls, use the project SVG as the theme logo, and apply an accessible
palette derived from the logo's navy, purple, and green colors. Set the project site URL so generated 404 asset links
work when deployed under GitHub Pages' `/betwixt/` path.


## Verification

- Ran the focused integration tests, including generated HTML, stylesheet, and project-site 404 assertions; 8 tests
  passed.
- Built the site with the pinned Zensical configuration.
- Inspected generated HTML for palette controls, the SVG logo, and the loaded extra stylesheet.
- Confirmed dark-mode link and header-text contrast ratios of 6.49:1 and 7.10:1.
- Ran `git diff --check` and inspected final status.
