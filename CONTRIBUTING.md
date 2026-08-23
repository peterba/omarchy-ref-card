# Contributing

Thank you for helping keep the Omarchy reference card accurate and printable.

## Before changing bindings

The distributed card is a curated summary of Omarchy's full-install defaults.
Personal preferences belong in the ignored `personalize.tex`, not in
`defaults/bindings.tex`. Preserve stable binding IDs whenever possible and
classify every new distributed ID exactly once in `upstream/bindings.toml`.

Use an Omarchy checkout at the commit recorded in `upstream/omarchy.lock`:

```sh
make check-upstream UPSTREAM_DIR=/path/to/omarchy
```

When upstream moves, first run `make check-upstream-reconcile` against the newer
checkout. Review the binding changes, update the card and classifications, and
only then run `make update-upstream-lock`. Include the reason for intentional
summaries or omissions in the change description.

The complete procedure is documented in
[Maintaining the card](docs/MAINTAINING.md).

## Verify the card

Run:

```sh
make check
make render
```

Inspect all four images in `build/render/`: both sides in landscape US Letter
and landscape A4. The documents must remain exactly two pages each, with three
panels per side, no clipping, collisions, TeX errors, or overfull boxes.

Do not commit `build/`, `personalize.tex`, or local system files. By submitting
a contribution, you agree that it may be distributed under the MIT License.
