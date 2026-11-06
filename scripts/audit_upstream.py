#!/usr/bin/env python3
"""Audit the distributed card against a checked-out Omarchy tree."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BINDING_RE = re.compile(r"^\\DeclareBinding\{([^}]+)\}\{([^}]*)\}\{([^}]*)\}$")
CALL_RE = re.compile(r"o\.(bind(?:_toggle|_hold)?)\s*\(")


def split_lua_args(text: str) -> list[str]:
    parts, start, depth, quote, escaped = [], 0, 0, None, False
    for index, char in enumerate(text):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char in "({[":
            depth += 1
        elif char in ")}]":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(text[start:index].strip())
            start = index + 1
    parts.append(text[start:].strip())
    return parts


def lua_calls(text: str) -> list[tuple[str, str]]:
    bindings = []
    for match in CALL_RE.finditer(text):
        index, depth, quote, escaped = match.end(), 1, None, False
        while index < len(text) and depth:
            char = text[index]
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = None
            elif char in "\"'":
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            index += 1
        if depth:
            raise ValueError("unterminated o.bind call")
        args = split_lua_args(text[match.end():index - 1])
        if len(args) < 2 or not re.fullmatch(r'"(?:[^"\\]|\\.)*"', args[0]):
            continue
        key = bytes(args[0][1:-1], "utf-8").decode("unicode_escape")
        description = ""
        if re.fullmatch(r'"(?:[^"\\]|\\.)*"', args[1]):
            description = bytes(args[1][1:-1], "utf-8").decode("unicode_escape")
        bindings.append((key, description))
    return bindings


def extract_hyprland(upstream: Path) -> list[tuple[str, str]]:
    directory = upstream / "default/hypr/bindings"
    if not directory.is_dir():
        raise ValueError(f"missing Omarchy binding directory: {directory}")
    result = []
    combined = ""
    for path in sorted(directory.glob("*.lua")):
        text = path.read_text(encoding="utf-8")
        combined += text
        result.extend(lua_calls(text))

    # These stock loops generate bindings whose first arguments are expressions.
    if re.search(r"for workspace = 1, 10 do", combined):
        for workspace in range(1, 11):
            code = workspace + 9
            result.extend([
                (f"SUPER + code:{code}", f"Switch to workspace {workspace}"),
                (f"SUPER + SHIFT + code:{code}", f"Move window to workspace {workspace}"),
                (f"SUPER + SHIFT + ALT + code:{code}", f"Move window silently to workspace {workspace}"),
            ])
    if re.search(r"for index = 1, 5 do", combined):
        result.extend((f"SUPER + ALT + code:{index + 9}", f"Switch to group window {index}") for index in range(1, 6))
    if re.search(r"for panel = 1, 9 do", combined):
        result.extend((f"SUPER + CTRL + code:{panel + 9}", f"Bar panel {panel}") for panel in range(1, 10))
    return sorted(set(result))


def extract_config_records(upstream: Path) -> list[tuple[str, str]]:
    """Extract binding-bearing lines from other canonical Omarchy configs."""
    specs = [
        ("tmux", upstream / "config/tmux/tmux.conf", re.compile(r"^bind(?:-key)?\s")),
        ("ghostty", upstream / "config/ghostty/config", re.compile(r"^keybind\s*=")),
        ("xcompose", upstream / "default/xcompose", re.compile(r"^<")),
        ("menu", upstream / "bin/omarchy-menu-keybindings", re.compile(r"^\s*echo \".*(?:Web App|keybindings)")),
    ]
    # Only the seed config's [keys] table defines Omarchy overrides.
    herdr = upstream / "config/herdr/config.toml"
    if not herdr.is_file():
        raise ValueError(f"missing canonical Omarchy config: {herdr}")
    records = []
    in_keys = False
    for line in herdr.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("["):
            in_keys = stripped == "[keys]"
        elif in_keys and stripped and not stripped.startswith("#"):
            records.append(("herdr", re.sub(r"\s+", " ", stripped)))
    for label, path, pattern in specs:
        if not path.is_file():
            raise ValueError(f"missing canonical Omarchy config: {path}")
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if pattern.search(line):
                records.append((label, re.sub(r"\s+", " ", stripped)))
    return sorted(set(records))


def canonical_token(token: str) -> str:
    token = token.strip().upper()
    aliases = {
        "SH": "SHIFT", "DEL": "DELETE", "PRINTSCREEN": "PRINT",
        "LEFTMOUSE": "MOUSE:272", "RIGHTMOUSE": "MOUSE:273",
        "SCROLLUP": "MOUSE_UP", "SCROLLDOWN": "MOUSE_DOWN",
        "BRIGHTUP": "XF86MONBRIGHTNESSUP", "BRIGHTDOWN": "XF86MONBRIGHTNESSDOWN",
        "VOLUMEUP": "XF86AUDIORAISEVOLUME", "VOLUMEDOWN": "XF86AUDIOLOWERVOLUME",
        "KEYBRIGHTUP": "XF86KBDBRIGHTNESSUP", "KEYBRIGHTDOWN": "XF86KBDBRIGHTNESSDOWN",
        "KEYBACKLIGHT": "XF86KBDLIGHTONOFF", "PLAY": "XF86AUDIOPLAY",
        "MUTE": "XF86AUDIOMUTE", "[": "CODE:34", "]": "CODE:35",
        "-": "CODE:20", "=": "CODE:21", "/": "SLASH", ",": "COMMA",
        ".": "PERIOD",
    }
    if token.startswith("CODE:"):
        code = int(token[5:])
        if 10 <= code <= 18:
            return str(code - 9)
        if code == 19:
            return "0"
    return aliases.get(token, token)


def normalize_chord(chord: str) -> str:
    parts = [canonical_token(part) for part in chord.split("+")]
    modifiers = [part for part in parts[:-1] if part]
    order = {"SUPER": 0, "CTRL": 1, "ALT": 2, "SHIFT": 3}
    modifiers.sort(key=lambda item: (order.get(item, 99), item))
    return "+".join(modifiers + parts[-1:])


def expand_card_key(value: str) -> set[str]:
    value = value.replace("\\%", "%")
    if value == "RightAlt":
        return {normalize_chord("ALT + Alt_R")}
    mods, token = value.rsplit("+", 1) if "+" in value else ("", value)
    prefix = f"{mods}+" if mods else ""
    alternatives: list[str]
    range_match = re.fullmatch(r"(\d)--(\d)", token)
    if range_match:
        alternatives = [str(number) for number in range(int(range_match[1]), int(range_match[2]) + 1)]
    elif token == "Arrow":
        alternatives = ["Left", "Right", "Up", "Down"]
    elif token == "Scroll":
        alternatives = ["ScrollUp", "ScrollDown"]
    elif token == "Left/Right":
        alternatives = ["Left", "Right"]
    elif token == "Up/Down":
        alternatives = ["Up", "Down"]
    elif token in {"BrightUp/Down", "VolumeUp/Down", "KeyBrightUp/Down"}:
        stem = token.removesuffix("Up/Down")
        alternatives = [stem + "Up", stem + "Down"]
    elif token in {"/", ",", "."}:
        alternatives = [token]
    elif "/" in token:
        alternatives = token.split("/")
    else:
        alternatives = [token]
    return {normalize_chord(prefix + item) for item in alternatives}


def read_card(path: Path) -> dict[str, str]:
    rows = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.startswith("\\DeclareBinding"):
            continue
        match = BINDING_RE.fullmatch(line)
        if not match:
            raise ValueError(f"unsupported binding syntax at {path}:{number}")
        binding_id, key, _description = match.groups()
        if binding_id in rows:
            raise ValueError(f"duplicate binding id: {binding_id}")
        rows[binding_id] = key
    return rows


def read_toml_subset(path: Path) -> dict:
    """Read the strings, integers, and string arrays used by our two TOML files."""
    result: dict = {}
    target = result
    lines = path.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].split("#", 1)[0].strip()
        index += 1
        if not line:
            continue
        section = re.fullmatch(r"\[([A-Za-z0-9_-]+)\]", line)
        if section:
            target = result.setdefault(section[1], {})
            continue
        match = re.match(r"([A-Za-z0-9_-]+)\s*=\s*(.*)", line)
        if not match:
            raise ValueError(f"unsupported TOML syntax in {path}: {line}")
        key, value = match.groups()
        while value.count("[") > value.count("]") and index < len(lines):
            value += "\n" + lines[index].split("#", 1)[0]
            index += 1
        try:
            target[key] = ast.literal_eval(value.rstrip().rstrip(","))
        except (SyntaxError, ValueError) as error:
            raise ValueError(f"unsupported TOML value for {key} in {path}") from error
    return result


def read_classifications(path: Path) -> tuple[dict[str, str], dict]:
    data = read_toml_subset(path)
    result = {}
    for category, ids in data["classifications"].items():
        for binding_id in ids:
            if binding_id in result:
                raise ValueError(f"{binding_id} is classified more than once")
            result[binding_id] = category
    return result, data


def digest_bindings(bindings: list[tuple[str, str]], config_records: list[tuple[str, str]]) -> str:
    payload = json.dumps(
        {"hyprland": bindings, "configs": config_records},
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def git_commit(upstream: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(upstream), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def audit(upstream: Path, require_lock: bool = True, require_commit: bool = False) -> dict:
    card = read_card(ROOT / "defaults/bindings.tex")
    classes, manifest = read_classifications(ROOT / "upstream/bindings.toml")
    errors = []
    missing = sorted(set(card) - set(classes))
    extra = sorted(set(classes) - set(card))
    if missing:
        errors.append("unclassified card ids: " + ", ".join(missing))
    if extra:
        errors.append("classified ids absent from card: " + ", ".join(extra))

    bindings = extract_hyprland(upstream)
    config_records = extract_config_records(upstream)
    upstream_keys = {normalize_chord(key) for key, _ in bindings}
    for binding_id, category in sorted(classes.items()):
        if category != "upstream_hyprland" or binding_id not in card:
            continue
        expected = expand_card_key(card[binding_id])
        absent = expected - upstream_keys
        if absent:
            errors.append(f"{binding_id}: not found upstream: {', '.join(sorted(absent))}")

    lock = read_toml_subset(ROOT / "upstream/omarchy.lock")
    digest = digest_bindings(bindings, config_records)
    commit = git_commit(upstream)
    if require_commit and commit != lock["commit"]:
        errors.append(f"upstream commit is {commit}, expected locked commit {lock['commit']}")
    if require_lock and digest != lock["binding_digest"]:
        errors.append(
            f"upstream binding digest changed: locked {lock['binding_digest']}, current {digest} ({commit})"
        )
    return {
        "ok": not errors,
        "profile": manifest["profile"],
        "commit": commit,
        "binding_digest": digest,
        "upstream_binding_count": len(bindings),
        "upstream_config_record_count": len(config_records),
        "card_binding_count": len(card),
        "classification_counts": {
            category: sum(value == category for value in classes.values())
            for category in sorted(set(classes.values()))
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path, required=True, help="checked-out Omarchy repository")
    parser.add_argument("--skip-lock", action="store_true", help="reconcile against a new upstream checkout")
    parser.add_argument("--require-commit", action="store_true", help="also require the exact locked Git commit")
    parser.add_argument("--write-lock", action="store_true", help="update the lock after reviewed reconciliation")
    parser.add_argument("--json", type=Path, help="also write a JSON report")
    args = parser.parse_args()
    try:
        report = audit(
            args.upstream.resolve(),
            require_lock=not (args.skip_lock or args.write_lock),
            require_commit=args.require_commit,
        )
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        report = {"ok": False, "errors": [str(error)]}
    if args.write_lock and report.get("ok"):
        old_lock = read_toml_subset(ROOT / "upstream/omarchy.lock")
        (ROOT / "upstream/omarchy.lock").write_text(
            "schema = 1\n"
            f"repository = \"{old_lock['repository']}\"\n"
            f"ref = \"{old_lock['ref']}\"\n"
            f"commit = \"{report['commit']}\"\n"
            f"binding_digest = \"{report['binding_digest']}\"\n",
            encoding="utf-8",
        )
    if args.json:
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"# Omarchy upstream audit\n")
    if "profile" in report:
        print(f"- Profile: {report['profile']}")
        print(f"- Commit: `{report['commit']}`")
        print(f"- Canonical Hyprland bindings: {report['upstream_binding_count']}")
        print(f"- Canonical config binding records: {report['upstream_config_record_count']}")
        print(f"- Distributed card rows: {report['card_binding_count']}")
    if report["errors"]:
        print("\n## Problems\n")
        for error in report["errors"]:
            print(f"- {error}")
    else:
        print("\nAudit passed.")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
