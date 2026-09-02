# Add the GitHub repository link to the docs header

The Zensical documentation header now links directly to the Betwixt GitHub repository with an accessible repository
label and GitHub branding.


## Intent

Expose the source repository from every generated documentation page without changing the existing site branding,
palette, navigation, or deployment URL.


## Changes

- Added the repository URL and accessible repository name to `docs/zensical.toml`.
- Configured the repository icon as `fontawesome/brands/github`.
- Added focused configuration and generated-output assertions to the integration tests.


## Verification

The focused integration tests passed with 8 tests. A clean Zensical 0.0.13 build succeeded, and `docs/site/index.html`
contains the repository href, `dusktreader/betwixt` label, and bundled GitHub SVG path. `git diff --check` also passed.


## Limitations

The link relies on Zensical 0.0.13's built-in repository-link rendering and bundled icon set. It does not add a custom
header component or alter the source documentation pages.
