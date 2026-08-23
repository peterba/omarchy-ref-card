# Customizing the card

The project follows Omarchy's defaults-plus-user-overrides model:

- `defaults/bindings.tex` contains the curated distributed bindings.
- `personalize.tex` contains your changes and is not tracked by Git.
- `omarchy-card.sty` contains the layout, typography, and customization API.
- `omarchy-reference-card.tex` contains the six-panel card content.

The default card builds without personal settings. Create a customization file
from the documented example with:

```sh
make personalize
```

This command preserves an existing `personalize.tex`. Project updates will not
overwrite it.

## Binding IDs

Every displayed shortcut has a stable ID. List them with:

```sh
make list-bindings
```

IDs are checked during the build. A misspelled override or personal binding
that reuses an existing ID stops with an error instead of silently producing
the wrong card.

## Override distributed bindings

Change a key and description together:

```tex
\SetBinding{notes}{Super+Shift+J}{notes -- Joplin}
```

Change only one field:

```tex
\SetBindingKey{close-window}{Super+Q}
\SetBindingDescription{email}{email -- Fastmail}
```

Hide a distributed row, or restore it later:

```tex
\RemoveBinding{photos}
\EnableBinding{photos}
```

## Add a personal row

Add a row to the Personal bindings section on side two:

```tex
\AddPersonalBinding{rss}{Super+Shift+R}{RSS -- NewsFlash}
```

Choose a new ID and keep the text short enough to fit the physical card.

## Fonts and titles

The defaults are Latin Modern Roman and Latin Modern Mono, preserving the
old-school Computer Modern appearance. Select installed fonts with:

```tex
\SetCardFonts{Libertinus Serif}{IBM Plex Mono}
```

Titles and source information can also be personalized:

```tex
\SetCardTitle{PAUL'S OMARCHY}
\SetCardEdition{Omarchy}
\SetCardSubtitle{Personal Reference Card}
\SetCardSourceDate{23 August 2026}
```

Descriptions and keys are TeX text. Escape special characters when they should
print literally; for example, write `\%`, `\_`, `\&`, and `\#`.

## Verify the result

Run:

```sh
make check
make render
```

The strict check verifies that both Letter and A4 documents remain exactly two
pages and contain no TeX errors or overfull boxes. Long key chords may wrap
after `+` or `/` to remain inside the key column.

Inspect all four images under `build/render/` for clipping, collisions,
inconsistent spacing, and legibility.
