# Content review — 6 November 2026

Shell essentials and Lazygit basics are now included; overlapping Ghostty
splits/tabs and LazyDocker have been removed. The other suggestions below
remain candidates for a future edit.
Community discussion is qualitative evidence, not representative usage data.

| Candidate | Recommendation | Evidence and tradeoff |
| --- | --- | --- |
| Shell essentials | Highest priority: add Ctrl+R history search, ff, cd with Zoxide, rg, lt/lsa | [Official shell tools](https://omarchy.org/manual/shell-tools/) documents these shipped defaults; useful across terminals and editors. |
| Lazygit | Add a compact launch/help/navigation row or two | Repeated recommendations in the [favorite TUIs discussion](https://www.reddit.com/r/omarchy/comments/1rn70m1/what_are_your_favorite_tuis_on_omarchy/); verify current keys before adding. |
| Yazi | Consider an explicitly optional small section | Also repeatedly recommended in the TUI discussion. It should not replace the stock GUI file-manager rows without choosing that scope. |
| Workspace plugins | Mention discovery/customization in documentation, not fixed global shortcuts | [Spaces](https://github.com/tornikegomareli/omarchy-spaces) drew substantial [community attention](https://www.reddit.com/r/omarchy/comments/1wsfsw4/introducing_spaces/). [Plugin users](https://www.reddit.com/r/omarchy/comments/1xcnv97/which_omarchy_plugins_from_the_repo_are_you/) also name Omission, Mirador, notification tools, Pocket, and appearance tools. Installed plugins and bindings vary. Attention does not establish an adoption ranking. |
| Ghostty | Reduce to a few terminal-specific essentials | Foot is the [documented default terminal](https://omarchy.org/manual/terminal/); Herdr already covers splits and tabs independently of the terminal. Ghostty remains an option. |
| Web-app launchers | Trim X, X Compose, Google Photos/Maps, and duplicate messenger rows first | Editorial judgment: many service-specific rows consume space that broadly useful shell tools could occupy. No reliable usage figures justify singling out a service as unpopular. |
| Emoji compose | Compress the full alphabet to a few examples plus the compose pattern | Editorial judgment: this is a large block compared with missing shell tools. |
| LazyDocker | Mark optional or remove in a fresh-install edition | The [4.5 release notes](https://omarchy.org/news/2026/11/omarchy-4-5/) explicitly remove it from new installs while preserving existing installations. |
| New 4.5 applications | Mention in documentation rather than allocate shortcut rows yet | The same release notes introduce Hype, Signed, Disktree, Monologue, and Gliff. Being new defaults is not evidence of established popularity, and most lack global shortcuts. |

Suggested next pass: replace some Ghostty split/tab rows and service-specific
launchers with a small shell-tools section and Lazygit basics. Keep core window
management, capture/OCR, dictation, notifications, and the new Herdr panel.

Herdr now replaces the detailed Tmux panel at the user's request. Omarchy ships
both; the official terminal manual still documents Tmux. The available sources
do not establish that the community as a whole has abandoned it.
