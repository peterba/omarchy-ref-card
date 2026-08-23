---
name: omarchy-ref-card
description: Maintain, customize, validate, and build the user's two-sided Omarchy reference card. Use when changing personal or distributed bindings, reorganizing card content, adjusting its TeX layout, or checking the rendered PDF.
---

# Omarchy Reference Card

Locate the `omarchy-ref-card` repository and read its `AGENTS.md`. Treat those
repository-local instructions as authoritative because they define the current
customization API, source-file boundaries, and validation commands.

Before editing, classify the request:

- Put user-specific bindings, titles, and fonts in the ignored
  `personalize.tex`.
- Change `defaults/bindings.tex` only for distributed defaults.
- Change `omarchy-reference-card.tex` for content organization.
- Change `omarchy-card.sty` for typography, layout, or API behavior.

Do not change the user's live Omarchy configuration unless explicitly asked.
Do not commit `personalize.tex` or generated build artifacts.

For distributed binding work, classify every id in `upstream/bindings.toml`
and run `make check-upstream UPSTREAM_DIR=/path/to/omarchy` against the commit
in `upstream/omarchy.lock`. Use the reconciliation target for a newer checkout
of the locked upstream ref, and update the lock only after reviewing every
reported change.

After content or layout changes, run `make check` and `make render`, then inspect
all four rendered page images. Preserve the two-page, six-panel layout in both
landscape US Letter and landscape A4 formats, and resolve any clipping,
collisions, TeX errors, or overfull boxes before completing the task.
