import tempfile
import unittest
from pathlib import Path

from scripts.audit_upstream import (
    expand_card_key,
    extract_config_records,
    extract_hyprland,
    lua_calls,
    normalize_chord,
)


class LuaExtractionTests(unittest.TestCase):
    def test_literal_calls_and_multiline_options(self):
        source = '''
o.bind("SUPER + W", "Close window", action())
o.bind_toggle(
  "SUPER + CTRL + N",
  "Toggle nightlight",
  "nightlight"
)
o.bind_hold("ALT + Alt_R", "Push to talk", "start", "Stop", "stop")
o.bind("SUPER + " .. key, "Generated " .. index, action())
'''
        self.assertEqual(
            lua_calls(source),
            [("SUPER + W", "Close window"), ("SUPER + CTRL + N", "Toggle nightlight"), ("ALT + Alt_R", "Push to talk")],
        )

    def test_stock_generated_ranges(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "default/hypr/bindings"
            directory.mkdir(parents=True)
            (directory / "tiling.lua").write_text('''
for workspace = 1, 10 do
  o.bind("SUPER + " .. key, "Switch to workspace " .. workspace, action())
end
for index = 1, 5 do
  o.bind("SUPER + ALT + code:" .. tostring(index + 9), "Switch to group window " .. index, action())
end
''')
            (directory / "utilities.lua").write_text('''
for panel = 1, 9 do
  o.bind("SUPER + CTRL + code:" .. tostring(panel + 9), "Bar panel " .. panel, action())
end
''')
            bindings = extract_hyprland(Path(temporary))
            self.assertIn(("SUPER + code:10", "Switch to workspace 1"), bindings)
            self.assertIn(("SUPER + ALT + code:14", "Switch to group window 5"), bindings)
            self.assertIn(("SUPER + CTRL + code:18", "Bar panel 9"), bindings)


class NormalizationTests(unittest.TestCase):
    def test_modifier_order_and_hardware_alias(self):
        self.assertEqual(normalize_chord("SHIFT + SUPER + XF86AudioMute"), "SUPER+SHIFT+XF86AUDIOMUTE")
        self.assertEqual(expand_card_key("Super+Sh+Mute"), {"SUPER+SHIFT+XF86AUDIOMUTE"})

    def test_ranges_directions_and_physical_codes(self):
        self.assertEqual(expand_card_key("RightAlt"), {"ALT+ALT_R"})
        self.assertEqual(expand_card_key("Super+1--4"), {"SUPER+1", "SUPER+2", "SUPER+3", "SUPER+4"})
        self.assertEqual(
            expand_card_key("Super+Arrow"),
            {"SUPER+LEFT", "SUPER+RIGHT", "SUPER+UP", "SUPER+DOWN"},
        )
        self.assertEqual(expand_card_key("Super+-/="), {"SUPER+CODE:20", "SUPER+CODE:21"})


class ConfigFixtureTests(unittest.TestCase):
    def test_tmux_herdr_ghostty_xcompose_and_menu_records(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixtures = {
                "config/tmux/tmux.conf": 'bind -N "Create window" c new-window\nset -g mouse on\n',
                "config/herdr/config.toml": '[keys]\nprefix = "ctrl+space"\n[ui]\naccent = "blue"\n',
                "config/ghostty/config": "keybind = control+insert=copy_to_clipboard\nfont-size = 9\n",
                "default/xcompose": '<Multi_key> <space> <space> : "—"\n# comment\n',
                "bin/omarchy-menu-keybindings": '  echo "SHIFT ALT,L,Copy URL from Web App,sendshortcut,SHIFT ALT,L,"\n',
            }
            for relative, content in fixtures.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            records = extract_config_records(root)
            self.assertEqual([line for label, line in records if label == "herdr"], ['prefix = "ctrl+space"'])
            self.assertEqual({label for label, _ in records}, {"tmux", "herdr", "ghostty", "xcompose", "menu"})


if __name__ == "__main__":
    unittest.main()
