# Theme icons hack journal

This journal records the focused documentation theme and icon follow-up completed on 2026-09-02.


## Intent

Tone the documentation header to the logo's dark navy, retain readable light and dark controls, and use the new PNG
icon for the generated site's logo and favicon.


## Changes

- Renamed `docs/source/static/icon` to `docs/source/static/icon.png` without changing the PNG bytes.
- Preserved `docs/source/static/icon.svg` and the existing landing-page `logo.png` asset.
- Updated `docs/zensical.toml` to use `static/icon.png` for both `logo` and `favicon`.
- Updated `docs/source/stylesheets/extra.css` so both schemes use `#17233f` for the primary header foreground, with
  readable primary background and dark-scheme navigation values.
- Updated focused integration assertions for the PNG logo, favicon, palette, and mode switches.


## Verification

The focused integration tests passed (`8 passed`). A clean Zensical build completed successfully. Generated pages
contain
the `static/icon.png` logo and favicon paths, both switch controls, and the navy `#17233f` header variable in the
copied stylesheet. The source PNG remains a 397x276 RGBA PNG with SHA-256
`62fcaca06debdfa617803470017daa5bc7f261aff7ed32408f401c146015a758`.

`git diff --check` completed without errors.


## Limitations

The prior theme journal remains unchanged. No visual browser review was performed.
