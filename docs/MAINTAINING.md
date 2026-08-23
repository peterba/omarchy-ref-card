# Maintaining the card

The distributed card is a curated summary of Omarchy's full-install defaults.
Personal changes belong in the ignored `personalize.tex`; this workflow audits
only the distributed card.

## Upstream binding audit

`upstream/bindings.toml` classifies every distributed binding ID exactly once.
Hyprland rows are normalized and checked as subsets of the canonical upstream
keys, allowing compact rows such as `Super+1--4` to summarize a larger range.
Tmux, Ghostty, XCompose, and menu records also contribute to the semantic drift
lock.

Audit against the revision recorded in `upstream/omarchy.lock`:

```sh
git clone https://github.com/basecamp/omarchy.git /tmp/omarchy
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
