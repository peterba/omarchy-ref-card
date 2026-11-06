# Maintaining the card

The distributed card is a curated summary of Omarchy's full-install defaults.
Personal changes belong in the ignored `personalize.tex`; this workflow audits
only the distributed card.

## Upstream binding audit

`upstream/bindings.toml` classifies every distributed binding ID exactly once.
Hyprland rows are normalized and checked as subsets of the canonical upstream
keys, allowing compact rows such as `Super+1--4` to summarize a larger range.
Tmux, Herdr, Ghostty, XCompose, and menu records also contribute to the semantic drift
lock.

Audit against the revision recorded in `upstream/omarchy.lock`:

```sh
git clone https://github.com/omacom/omarchy.git /tmp/omarchy
git -C /tmp/omarchy checkout "$(awk -F '"' '/^commit/ {print $2}' upstream/omarchy.lock)"
make check-upstream UPSTREAM_DIR=/tmp/omarchy
```

To investigate a newer checkout without changing the lock, run:

```sh
make check-upstream-reconcile UPSTREAM_DIR=/tmp/omarchy
```

Review every reported change, update the card and classifications, then record
the reviewed revision:

```sh
make update-upstream-lock UPSTREAM_DIR=/tmp/omarchy
```

Never update the lock merely to silence drift. Include the reason for any
intentional summary or omission in the change description.

## Continuous integration

Pushes and pull requests run the deterministic pinned audit and build both
paper sizes. A weekly read-only workflow checks the latest revision of the
configured upstream ref and opens one deduplicated issue when drift is found.

Before committing a content or layout change, run:

```sh
make check-upstream UPSTREAM_DIR=/path/to/pinned/omarchy
make check
make render
```

Inspect both pages of both paper formats under `build/render/`.

After a visible card change, regenerate the tracked README image with:

```sh
make preview
```

This target requires FFmpeg and composes both Letter pages into
`docs/images/omarchy-reference-card-preview.png`. Inspect the result before
committing it.

## Coding-agent support

`AGENTS.md` defines the repository's editing boundaries and verification rules.
A reusable Codex skill is version-controlled under
`codex-skill/omarchy-ref-card/`. Install it as a symlink so repository updates
take effect immediately:

```sh
make install-skill
```

The target defaults to `~/.codex/skills/omarchy-ref-card`. Installation refuses
to replace an existing file, directory, or symlink.

## Omarchy 4.5 review

The lock pins the v4.5.0 release (ac2690cd). Its canonical binding files match
those shipped by the installed 4.5.0-3 package. Updated calculator, network,
activity, dictation, and notification actions; removed the obsolete night-light
shortcut; added layout cycling, dock minimization, Quake console, monitor moves,
world clock, select all, input language switching, and full screen desktop.
Existing IDs are preserved for changed actions where possible.

The card retains compact workspace ranges and one shortcut per action rather
than listing every alias. Hardware-specific JIS and Mac brightness aliases and
transient screenshot-selection keys remain omitted to keep the card readable.
Tmux, Ghostty, and XCompose binding records did not change. The audit now reads
`o.bind_hold` for dictation; RightAlt represents the upstream modifier-independent
hold binding, whose declared chord is `ALT + Alt_R` with `ignore_mods = true`.

## Herdr-focused card

The terminal panel now uses Omarchy 4.5's `config/herdr/config.toml`, with
Herdr tabs and workspaces in place of Tmux windows and sessions. Shared pane
IDs remain stable; Tmux-specific IDs were replaced with Herdr IDs. The prefix
is Ctrl+Space; the Tmux Ctrl+B alternate is not an Omarchy Herdr alternate.
The layout helpers now use `hdl`, `hdlm`, and `hsl`, reviewed in
`default/bash/fns/herdr`. Tmux's command prompt and copy-mode selection keys
are omitted rather than assumed to work in Herdr.

Sidebar, notification target, new worktree, and workspace picker use Herdr
0.9.1 built-in defaults, verified with the installed `herdr --default-config`;
these are classified as external defaults. Other Herdr rows come from the
Omarchy seed config. Its [keys] records now contribute to the drift digest.
The upstream revision stays at v4.5.0; the digest changes because Herdr is now
included in the audit. Tmux launch/help rows remain available for users of both.

## Shell essentials and Lazygit

The shell section summarizes `default/bash/aliases` at the locked revision:
`ff`, `eff`, `cd` through Zoxide, `lt`, and `lsa`. These are manual-derived
commands. Ctrl+R comes from the fzf bindings loaded by `default/bash/init`;
ripgrep usage is an external tool default. Lazygit keys are external defaults,
reviewed against installed Lazygit 0.66.2 (`lazygit --config`) and the
[upstream key reference](https://github.com/jesseduffield/lazygit/blob/master/docs/keybindings/Keybindings_en.md).
Omarchy's seeded Lazygit config has no key overrides. Files-panel scope is
printed for staging and committing. The Ghostty section retains only scrollback
and browser-link controls; Herdr covers panes and tabs. LazyDocker is omitted
because new Omarchy 4.5 installs no longer include it. No upstream lock change
is needed for this curation pass.
