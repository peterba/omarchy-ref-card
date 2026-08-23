# Omarchy Reference Card

A customizable, two-sided TeX reference card for Omarchy 4 Quattro. Its
physical six-panel format is inspired by Stephen Gildea's classic GNU Emacs
Reference Card. Its LaTeX implementation is independent and is designed for US
Letter or A4 paper folded into thirds.

## Build the cards

Install [Tectonic](https://tectonic-typesetting.github.io/) to build the PDFs.
The check and render targets also use Poppler's `pdfinfo` and `pdftoppm` tools.
Then run:

```sh
make
```

This produces native PDFs for both supported paper sizes:

- `build/omarchy-reference-card-letter.pdf`
- `build/omarchy-reference-card-a4.pdf`

Build just one format with `make letter` or `make a4`.

Print the PDF matching your paper in landscape at 100%, double-sided, flipping
on the short edge. Do not scale the Letter PDF to A4 or the A4 PDF to Letter;
each file has geometry sized for three equal folding panels on its own paper.

## Personalize it

The project follows Omarchy's defaults-plus-user-overrides model:

- `defaults/bindings.tex` contains the curated distributed bindings shown on the card.
- `personalize.tex` contains your changes and is not tracked by Git.
- `omarchy-card.sty` contains the layout and typography.
- `omarchy-reference-card.tex` contains the six-panel card content.

The default card builds without a personal settings file. To create one from
the documented example, run:

```sh
make personalize
```

This command preserves an existing `personalize.tex`.

List the stable ids available for customization:

```sh
make list-bindings
```

Every displayed shortcut has an id. For example, change the window-close key
and replace HEY with Gmail without editing the defaults:

```tex
\SetBindingKey{close-window}{Super+Q}
\SetBinding{email}{Super+Shift+E}{email -- Gmail}
\SetBinding{new-email}{Super+Sh+Alt+E}{new email -- Gmail}
```

Change an app and its key together:

```tex
\SetBinding{notes}{Super+Shift+J}{notes -- Joplin}
```

Change only a key or only its description:

```tex
\SetBindingKey{email}{Super+Shift+G}
\SetBindingDescription{email}{email -- Fastmail}
```

Remove any official binding row:

```tex
\RemoveBinding{photos}
```

Restore a removed row with `\EnableBinding{photos}`.

Add a personal row to side two:

```tex
\AddPersonalBinding{rss}{Super+Shift+R}{RSS -- NewsFlash}
```

Binding ids are checked during the build. A misspelled override or a personal
binding that reuses an existing id stops with an error instead of silently
producing the wrong card. The available official ids are listed in
`defaults/bindings.tex`.

Descriptions and keys are TeX text. Escape TeX's special characters when they
should print literally; for example, write `\%`, `\_`, `\&`, and `\#`.

## Fonts and titles

The defaults are Latin Modern Roman and Latin Modern Mono, preserving the
old-school Computer Modern appearance. To use installed fonts instead:

```tex
\SetCardFonts{Libertinus Serif}{IBM Plex Mono}
```

You can also set a personal title:

```tex
\SetCardTitle{PAUL'S OMARCHY}
\SetCardEdition{Omarchy 4 Quattro}
\SetCardSubtitle{Personal Reference Card}
\SetCardSourceDate{22 August 2026}
```

## Check the output

Run the stricter build check after changing bindings or layout:

```sh
make check
```

It verifies that both Letter and A4 documents remain exactly two pages and
contain no TeX errors or overfull boxes. Long key chords may wrap after `+` or
`/` to remain inside the key column.

Render both pages of both paper formats as PNG files for visual inspection:

```sh
make render
```

The images are written under `build/render/`.

## AI-assisted maintenance

`AGENTS.md` explains the project's editing boundaries and verification workflow
to coding agents. A reusable Codex skill is version-controlled under
`codex-skill/omarchy-ref-card/`. Install it as a symlink so repository updates
take effect immediately:

```sh
make install-skill
```

The target defaults to `~/.codex/skills/omarchy-ref-card`. Installation refuses
to replace an existing file, directory, or symlink.

## Updating

Update the distributed defaults, layout, and document files as needed, but keep
personal changes in `personalize.tex`. This is analogous to Omarchy keeping its
own files separate from user-owned overrides in `~/.config`.

The audit profile is **Omarchy 4 Quattro full-install defaults**. It compares
the distributed card—not `personalize.tex`—with an explicit classification in
`upstream/bindings.toml`. Hyprland rows are normalized and checked as subsets of
the canonical upstream keys, so compact rows such as `Super+1--4` can
intentionally summarize a larger upstream range. Tmux, Ghostty, XCompose, and
menu binding records also contribute to the semantic drift lock.

Audit against the reviewed commit in `upstream/omarchy.lock`:

```sh
git clone https://github.com/basecamp/omarchy.git /tmp/omarchy
git -C /tmp/omarchy checkout "$(awk -F '"' '/^commit/ {print $2}' upstream/omarchy.lock)"
make check-upstream UPSTREAM_DIR=/tmp/omarchy
```

To investigate a newer Quattro checkout without changing the lock, use
`make check-upstream-reconcile UPSTREAM_DIR=/tmp/omarchy`. After reviewing and
reconciling every reported change, update the lock with
`make update-upstream-lock UPSTREAM_DIR=/tmp/omarchy` and review that diff.

Pushes and pull requests run the deterministic pinned audit and build both paper
sizes. A weekly read-only audit compares the latest `quattro` branch with the
lock and opens one deduplicated issue if drift is detected.

## License and provenance

The project is available under the [MIT License](LICENSE), matching Omarchy's
license. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for Omarchy data,
the GNU Emacs Reference Card format inspiration, and font notices. The card's
LaTeX implementation is independent; GNU Emacs reference-card TeX was not
incorporated.

Contributions are welcome; read [CONTRIBUTING.md](CONTRIBUTING.md) before
changing distributed bindings or the upstream lock.
