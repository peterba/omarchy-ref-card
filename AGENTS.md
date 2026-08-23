# Agent instructions

This repository builds a customizable, two-sided Omarchy reference card. Read
`docs/CUSTOMIZING.md` before changing binding content or the customization API,
and `docs/MAINTAINING.md` before changing the upstream audit.

## Choose the correct editing surface

- For the user's private bindings, titles, or fonts, edit `personalize.tex`.
  Create it with `make personalize` when absent. It is intentionally ignored by
  Git and must not be committed.
- To update the defaults distributed by this project, edit
  `defaults/bindings.tex` while preserving existing stable IDs where possible.
- To change section membership, ordering, wording outside binding rows, or
  panel placement, edit `omarchy-reference-card.tex`.
- To change typography, geometry, rendering macros, or the customization API,
  edit `omarchy-card.sty`.
- To change upstream classifications or the reviewed Omarchy revision, edit
  files under `upstream/` through the workflow in `docs/MAINTAINING.md`.
- Never edit files under `build/`.

Do not treat a personal preference as a new distributed default without an
explicit request. Do not modify the user's live Omarchy configuration unless
the user separately asks for that change.

## Binding customization

Use the public commands documented in `docs/CUSTOMIZING.md`:

- `\SetBinding` changes a key and description together.
- `\SetBindingKey` or `\SetBindingDescription` changes one field.
- `\RemoveBinding` and `\EnableBinding` control an existing row.
- `\AddPersonalBinding` adds a private row to the personal section on side two.

Use `make list-bindings` to inspect valid distributed IDs. Do not bypass the
strict unknown-ID and duplicate-ID checks. Keep TeX special-character escaping
in mind for user-visible text.

## Verification

For any distributed binding change, run `make check-upstream` with
`UPSTREAM_DIR` set to a checkout at the commit in `upstream/omarchy.lock`.
Every distributed id must remain classified exactly once in
`upstream/bindings.toml`. Never audit `personalize.tex`, silently loosen an
upstream-backed classification, or update the lock before reviewing drift.

After changing content or layout:

1. Run `make check`.
2. Run `make render`.
3. Inspect all four page images under `build/render/` for clipping, collisions,
   inconsistent spacing, and legibility.

After a visible card change, run `make preview`, inspect the tracked README
image, and include its update in the same commit.

Both final documents must remain exactly two landscape pages, one in US Letter
and one in A4, with three panels per side, no TeX errors, and no overfull boxes.
If content no longer fits, prefer concise wording or removal of low-value rows
before making the entire card harder to read.

Commit only tracked project changes, and keep generated files and personal
settings out of version control.
