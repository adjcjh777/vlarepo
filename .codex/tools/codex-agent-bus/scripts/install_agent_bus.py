#!/usr/bin/env python3
"""Install Codex Agent Bus as a user-level local Codex tool."""

from __future__ import annotations

import argparse
import os
import shutil
import stat
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEST = Path.home() / ".codex" / "tools" / "codex-agent-bus"
DEFAULT_BUS_HOME = Path.home() / ".codex" / "agent-bus"
CONFIG_BEGIN = "# BEGIN CODEX_AGENT_BUS"
CONFIG_END = "# END CODEX_AGENT_BUS"


def toml_quote(value: Path) -> str:
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def config_block(install_root: Path, bus_home: Path) -> str:
    mcp = install_root / "bin" / "agent-bus-mcp"
    hook = install_root / "bin" / "agent-bus-hook"
    tools = [
        "register_agent",
        "update_agent",
        "list_agents",
        "resolve_agent",
        "send_message",
        "reply_message",
        "get_inbox",
        "mark_read",
        "update_status",
        "bus_health",
    ]
    tool_lines = ",\n  ".join('"%s"' % item for item in tools)
    return """{begin}
[mcp_servers.agent_bus]
command = {mcp}
args = []
enabled = true
startup_timeout_sec = 10
tool_timeout_sec = 600
enabled_tools = [
  {tool_lines},
]

[[hooks.SessionStart]]
matcher = ".*"
[[hooks.SessionStart.hooks]]
type = "command"
command = {hook}

[[hooks.Stop]]
matcher = ".*"
[[hooks.Stop.hooks]]
type = "command"
command = {hook}
# CODEX_AGENT_BUS_HOME defaults to {bus_home}
{end}
""".format(
        begin=CONFIG_BEGIN,
        end=CONFIG_END,
        mcp=toml_quote(mcp),
        hook=toml_quote(hook),
        bus_home=str(bus_home),
        tool_lines=tool_lines,
    )


def should_ignore(_dir: str, names: List[str]) -> Iterable[str]:
    ignored = {
        ".git",
        ".pytest_cache",
        "__pycache__",
        ".mypy_cache",
        ".ruff_cache",
        ".DS_Store",
    }
    return [name for name in names if name in ignored or name.endswith(".pyc")]


def copy_tool(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(str(src), str(dest), dirs_exist_ok=True, ignore=should_ignore)


def write_wrapper(path: Path, module: str, install_root: Path, bus_home: Path) -> None:
    content = """#!/usr/bin/env sh
set -eu
export PYTHONPATH="{root}${{PYTHONPATH:+:$PYTHONPATH}}"
export CODEX_AGENT_BUS_HOME="${{CODEX_AGENT_BUS_HOME:-{home}}}"
exec python3 -m {module} "$@"
""".format(
        root=str(install_root),
        home=str(bus_home),
        module=module,
    )
    path.write_text(content, encoding="utf-8")
    current = path.stat().st_mode
    path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def write_wrappers(install_root: Path, bus_home: Path) -> None:
    bin_dir = install_root / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    write_wrapper(bin_dir / "agent-bus", "agent_bus.cli", install_root, bus_home)
    write_wrapper(bin_dir / "agent-bus-mcp", "agent_bus.mcp_server", install_root, bus_home)
    write_wrapper(bin_dir / "agent-bus-hook", "agent_bus.hooks", install_root, bus_home)


def remove_managed_block(text: str) -> str:
    while CONFIG_BEGIN in text and CONFIG_END in text:
        start = text.index(CONFIG_BEGIN)
        end = text.index(CONFIG_END, start) + len(CONFIG_END)
        if end < len(text) and text[end : end + 1] == "\n":
            end += 1
        text = text[:start].rstrip() + "\n\n" + text[end:].lstrip()
    return text.strip() + ("\n" if text.strip() else "")


def remove_table(text: str, header: str) -> str:
    lines = text.splitlines()
    output: List[str] = []
    skipping = False
    nested_prefix = header[:-1] + "."
    for line in lines:
        stripped = line.strip()
        if stripped == header or stripped.startswith(nested_prefix):
            skipping = True
            continue
        if skipping and stripped.startswith("[") and stripped.endswith("]"):
            if stripped == header or stripped.startswith(nested_prefix):
                continue
            skipping = False
        if not skipping:
            output.append(line)
    return "\n".join(output).strip() + ("\n" if output else "")


def ensure_feature_flags(text: str) -> str:
    return ensure_table_bools(text, "features", {"hooks": True, "multi_agent": True})


def ensure_table_bools(text: str, table: str, values: dict) -> str:
    lines = text.splitlines()
    header = "[%s]" % table
    for index, line in enumerate(lines):
        if line.strip() == header:
            end = index + 1
            while end < len(lines) and not (lines[end].strip().startswith("[") and lines[end].strip().endswith("]")):
                end += 1
            section = lines[index + 1 : end]
            for key, value in values.items():
                rendered = "%s = %s" % (key, "true" if value else "false")
                replaced = False
                for offset, section_line in enumerate(section):
                    if section_line.strip().startswith(key + " " ) or section_line.strip().startswith(key + "="):
                        section[offset] = rendered
                        replaced = True
                        break
                if not replaced:
                    section.append(rendered)
            return "\n".join(lines[: index + 1] + section + lines[end:]).strip() + "\n"
    prefix = header + "\n" + "\n".join("%s = true" % key for key in values.keys()) + "\n\n"
    return prefix + text.lstrip()


def update_user_config(config_path: Path, install_root: Path, bus_home: Path, dry_run: bool = False) -> Optional[Path]:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    block = config_block(install_root, bus_home)
    if dry_run:
        print("# Dry run: would ensure [features].hooks = true and [features].multi_agent = true")
        print("# Dry run: would replace any existing managed Codex Agent Bus block")
        print("# Dry run: would not print the existing user config")
        print(block)
        return None
    old_text = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    new_text = remove_managed_block(old_text)
    new_text = remove_table(new_text, "[mcp_servers.agent_bus]")
    new_text = ensure_feature_flags(new_text)
    if new_text and not new_text.endswith("\n"):
        new_text += "\n"
    new_text += "\n" + block
    backup = None
    if config_path.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = config_path.with_suffix(config_path.suffix + ".bak-" + stamp)
        shutil.copy2(str(config_path), str(backup))
    config_path.write_text(new_text, encoding="utf-8")
    return backup


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Codex Agent Bus for all local Codex projects.")
    parser.add_argument("--user", action="store_true", help="Install to ~/.codex/tools and update ~/.codex/config.toml")
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST, help="Installation directory")
    parser.add_argument("--bus-home", type=Path, default=DEFAULT_BUS_HOME, help="Global Agent Bus data directory")
    parser.add_argument("--config", type=Path, default=Path.home() / ".codex" / "config.toml")
    parser.add_argument("--dry-run", action="store_true", help="Print config without writing")
    args = parser.parse_args()

    install_root = args.dest.expanduser().resolve()
    bus_home = args.bus_home.expanduser().resolve()
    if not args.user:
        print(config_block(PROJECT_ROOT.resolve(), bus_home))
        print("Run with --user to copy the tool and update ~/.codex/config.toml with a backup.")
        return 0

    if not args.dry_run:
        copy_tool(PROJECT_ROOT, install_root)
        write_wrappers(install_root, bus_home)
        bus_home.mkdir(parents=True, exist_ok=True)
    backup = update_user_config(args.config.expanduser(), install_root, bus_home, dry_run=args.dry_run)
    if args.dry_run:
        return 0
    print("Installed Codex Agent Bus to %s" % install_root)
    print("Updated user config %s" % args.config.expanduser())
    if backup:
        print("Backup written to %s" % backup)
    print("Global registry: %s" % (bus_home / "registry.json"))
    print("Global messages: %s" % (bus_home / "messages.jsonl"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
