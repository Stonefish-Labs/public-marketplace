#!/usr/bin/env python3
"""
Shared CLI for deterministic PM file operations.

Subcommands:
    add-worklog       Append entries to a PROJECT.md work log
    update-milestone  Update a milestone row in a PROJECT.md
    update-frontmatter  Update YAML frontmatter fields in any .md file
    move-project      Move a project folder to the correct lifecycle folder
    validate          Run validation checks against a PROJECT/PROPOSAL/RETRO .md

All output is JSON for agent consumption. Stdlib only.
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FM_DELIM = "---"

STATUS_FOLDER_MAP = {
    "proposed": "Proposed",
    "on-deck": "On-Deck",
    "active": "Active",
    "waiting": "Paused",
    "stalled": "Paused",
    "parked": "Paused",
    "completed": "Archive",
    "cancelled": "Archive",
}

VALID_STATUSES = set(STATUS_FOLDER_MAP.keys())
VALID_MILESTONE_STATUSES = {"pending", "in-progress", "done", "skipped"}


def _find_workspace_root(start: Path) -> Path:
    """Walk up from *start* looking for the PM workspace root (contains lifecycle folders)."""
    cur = start.resolve()
    lifecycle = {"Proposed", "On-Deck", "Active", "Paused", "Archive"}
    while cur != cur.parent:
        if any((cur / d).is_dir() for d in lifecycle):
            return cur
        cur = cur.parent
    return start.resolve()


def _read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _split_frontmatter(text: str):
    """Return (frontmatter_str, body_str) or (None, text) if no frontmatter."""
    if not text.startswith(FM_DELIM):
        return None, text
    parts = text.split(FM_DELIM, 2)
    if len(parts) < 3:
        return None, text
    return parts[1], parts[2]


def _join_frontmatter(fm: str, body: str) -> str:
    return f"{FM_DELIM}{fm}{FM_DELIM}{body}"


def _parse_fm_simple(fm_str: str) -> dict:
    """Minimal YAML-ish parser good enough for flat PM frontmatter."""
    result = {}
    current_key = None
    list_key = None
    nested_key = None
    nested_dict = {}

    for raw_line in fm_str.split("\n"):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip())

        if indent >= 2 and list_key:
            if stripped.startswith("- "):
                result.setdefault(list_key, []).append(stripped[2:].strip().strip('"').strip("'"))
                continue

        if indent >= 2 and nested_key:
            m = re.match(r"^(\w[\w_-]*):\s*(.*)$", stripped)
            if m:
                v = m.group(2).strip().strip('"').strip("'")
                if v in ("true", "True"):
                    v = True
                elif v in ("false", "False"):
                    v = False
                nested_dict[m.group(1)] = v
                result[nested_key] = dict(nested_dict)
                continue

        list_key = None
        nested_key = None
        nested_dict = {}

        m = re.match(r"^([\w][\w_-]*):\s*(.*)$", stripped)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()

        if val == "" or val is None:
            current_key = key
            list_key = key
            nested_key = key
            result[key] = ""
            continue

        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            if inner:
                result[key] = [v.strip().strip('"').strip("'") for v in inner.split(",")]
            else:
                result[key] = []
            continue

        if val == "":
            list_key = key
            result[key] = []
            continue

        if val in ("true", "True"):
            result[key] = True
        elif val in ("false", "False"):
            result[key] = False
        else:
            result[key] = val.strip('"').strip("'")

    return result


def _set_fm_value(fm_str: str, key: str, value) -> str:
    """Set a single key in frontmatter string, preserving order and formatting."""
    if isinstance(value, bool):
        val_str = "true" if value else "false"
    elif isinstance(value, list):
        if value:
            val_str = "[" + ", ".join(str(v) for v in value) + "]"
        else:
            val_str = "[]"
    elif value is None or value == "":
        val_str = ""
    else:
        val_str = str(value)
        if " " in val_str or ":" in val_str or "," in val_str:
            val_str = f'"{val_str}"'

    pattern = re.compile(r"^(" + re.escape(key) + r"):\s*(.*)$", re.MULTILINE)
    if pattern.search(fm_str):
        return pattern.sub(f"{key}: {val_str}", fm_str)
    else:
        return fm_str.rstrip() + f"\n{key}: {val_str}\n"


def _today() -> str:
    return date.today().strftime("%Y-%m-%d")


def _result(ok: bool, **kwargs):
    out = {"ok": ok}
    out.update(kwargs)
    return out


def _die(msg: str):
    print(json.dumps(_result(False, error=msg)), file=sys.stdout)
    sys.exit(1)


def _output(data: dict):
    print(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# add-worklog
# ---------------------------------------------------------------------------

def cmd_add_worklog(args):
    path = Path(args.file).resolve()
    if not path.exists():
        _die(f"File not found: {path}")

    content = _read_file(path)
    fm_str, body = _split_frontmatter(content)
    if fm_str is None:
        _die("No YAML frontmatter found")

    entry_date = args.date or _today()

    lines = []
    if args.status_change:
        lines.append(f"- *Status: {args.status_change}*")
    if args.milestone_complete:
        lines.append(f"- *{args.milestone_complete}*")
    for e in (args.entry or []):
        lines.append(f"- {e}")

    if not lines:
        _die("No entries provided. Use --entry, --status-change, or --milestone-complete.")

    date_header = f"### {entry_date}"
    entry_block = "\n".join(lines)

    wl_match = re.search(r"^## Work Log\s*$", body, re.MULTILINE)
    if not wl_match:
        _die("No '## Work Log' section found in file")

    wl_start = wl_match.end()
    after_wl = body[wl_start:]

    existing_header = re.search(
        r"^### " + re.escape(entry_date) + r"\s*$", after_wl, re.MULTILINE
    )

    if existing_header:
        insert_pos = wl_start + existing_header.end()
        new_body = body[:insert_pos] + "\n" + entry_block + body[insert_pos:]
    else:
        new_body = body[:wl_start] + "\n\n" + date_header + "\n" + entry_block + body[wl_start:]

    fm_str = _set_fm_value(fm_str, "last_updated", args.date or _today())
    new_content = _join_frontmatter(fm_str, new_body)
    _write_file(path, new_content)

    _output(_result(True, file=str(path), date=entry_date, entries_added=len(lines)))


# ---------------------------------------------------------------------------
# update-milestone
# ---------------------------------------------------------------------------

def cmd_update_milestone(args):
    path = Path(args.file).resolve()
    if not path.exists():
        _die(f"File not found: {path}")

    if args.status not in VALID_MILESTONE_STATUSES:
        _die(f"Invalid milestone status '{args.status}'. Must be one of: {', '.join(sorted(VALID_MILESTONE_STATUSES))}")

    content = _read_file(path)
    fm_str, body = _split_frontmatter(content)
    if fm_str is None:
        _die("No YAML frontmatter found")

    table_pattern = re.compile(
        r"^(\|[\s]*#[\s]*\|.*\n\|[-| ]+\n(?:\|.*\n?)*)", re.MULTILINE
    )
    table_match = table_pattern.search(body)
    if not table_match:
        _die("No milestone table found")

    table_text = table_match.group(0)
    table_lines = table_text.strip().split("\n")

    header = table_lines[0]
    separator = table_lines[1]
    rows = table_lines[2:]

    updated = False
    new_rows = []
    for row in rows:
        cols = [c.strip() for c in row.split("|")]
        cols = [c for c in cols if c != ""]
        if not cols:
            new_rows.append(row)
            continue

        try:
            row_num = int(cols[0].strip())
        except (ValueError, IndexError):
            new_rows.append(row)
            continue

        if row_num == args.num:
            while len(cols) < 5:
                cols.append("")
            cols[3] = args.status
            if args.status == "done":
                cols[4] = args.completed or _today()
            elif args.completed:
                cols[4] = args.completed
            new_row = "| " + " | ".join(cols) + " |"
            new_rows.append(new_row)
            updated = True
        else:
            new_rows.append(row)

    if not updated:
        _die(f"Milestone #{args.num} not found in table")

    new_table = "\n".join([header, separator] + new_rows)
    if table_text.endswith("\n"):
        new_table += "\n"

    new_body = body[:table_match.start()] + new_table + body[table_match.end():]

    fm_str = _set_fm_value(fm_str, "last_updated", _today())
    new_content = _join_frontmatter(fm_str, new_body)
    _write_file(path, new_content)

    _output(_result(True, file=str(path), milestone=args.num, status=args.status))


# ---------------------------------------------------------------------------
# update-frontmatter
# ---------------------------------------------------------------------------

def cmd_update_frontmatter(args):
    path = Path(args.file).resolve()
    if not path.exists():
        _die(f"File not found: {path}")

    content = _read_file(path)
    fm_str, body = _split_frontmatter(content)
    if fm_str is None:
        _die("No YAML frontmatter found")

    updates = {}
    for pair in (args.set or []):
        if "=" not in pair:
            _die(f"Invalid --set format: '{pair}'. Expected key=value.")
        key, val = pair.split("=", 1)
        if val.lower() == "true":
            val = True
        elif val.lower() == "false":
            val = False
        updates[key] = val

    if not updates:
        _die("No --set arguments provided.")

    if "status" in updates:
        new_status = updates["status"]
        if new_status in ("completed", "cancelled") and "date_completed" not in updates:
            updates["date_completed"] = _today()

    if "last_updated" not in updates:
        updates["last_updated"] = _today()

    for key, val in updates.items():
        fm_str = _set_fm_value(fm_str, key, val)

    new_content = _join_frontmatter(fm_str, body)
    _write_file(path, new_content)

    _output(_result(True, file=str(path), updated_fields=list(updates.keys())))


# ---------------------------------------------------------------------------
# move-project
# ---------------------------------------------------------------------------

def cmd_move_project(args):
    folder = Path(args.folder).resolve()
    if not folder.is_dir():
        _die(f"Not a directory: {folder}")

    status = args.to_status
    if status not in STATUS_FOLDER_MAP:
        _die(f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}")

    target_parent_name = STATUS_FOLDER_MAP[status]
    root = _find_workspace_root(folder)
    target_parent = root / target_parent_name

    if not target_parent.exists():
        target_parent.mkdir(parents=True)

    dest = target_parent / folder.name
    if dest.exists():
        _die(f"Destination already exists: {dest}")

    project_md = folder / "PROJECT.md"
    if project_md.exists():
        content = _read_file(project_md)
        fm_str, body = _split_frontmatter(content)
        if fm_str:
            fm_str = _set_fm_value(fm_str, "status", status)
            fm_str = _set_fm_value(fm_str, "last_updated", _today())
            if status in ("completed", "cancelled"):
                fm_str = _set_fm_value(fm_str, "date_completed", _today())
            _write_file(project_md, _join_frontmatter(fm_str, body))

    shutil.move(str(folder), str(dest))

    _output(_result(True, moved_from=str(folder), moved_to=str(dest), status=status))


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

def cmd_validate(args):
    path = Path(args.file).resolve()
    if not path.exists():
        _die(f"File not found: {path}")

    content = _read_file(path)
    fm_str, body = _split_frontmatter(content)
    if fm_str is None:
        _die("No YAML frontmatter found")

    fm = _parse_fm_simple(fm_str)
    checks = []
    file_type = args.type

    folder_name = path.parent.name

    if file_type == "proposal":
        _validate_proposal(fm, body, folder_name, checks)
    elif file_type == "project":
        _validate_project(fm, body, folder_name, path, checks)
    elif file_type == "retro":
        _validate_retro(fm, body, checks)
    else:
        _die(f"Unknown type '{file_type}'. Must be project, proposal, or retro.")

    passed = sum(1 for c in checks if c["pass"])
    total = len(checks)
    _output(_result(True, file=str(path), type=file_type,
                    passed=passed, total=total, checks=checks))


def _check(checks: list, name: str, ok: bool, detail: str = ""):
    checks.append({"check": name, "pass": ok, "detail": detail})


def _validate_proposal(fm, body, folder_name, checks):
    pid = fm.get("project_id", "")
    _check(checks, "project_id_present", bool(pid))
    _check(checks, "project_id_kebab", bool(re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", pid)) if pid else False)
    _check(checks, "project_id_matches_folder", pid == folder_name, f"id={pid}, folder={folder_name}")

    _check(checks, "date_proposed_present", bool(fm.get("date_proposed")))
    _check(checks, "review_by_present", bool(fm.get("review_by")))

    readiness = fm.get("readiness", {})
    gates = ["problem_defined", "outcome_clear", "effort_estimated", "motivation_justified", "alternatives_considered"]
    if isinstance(readiness, dict):
        _check(checks, "readiness_has_all_gates", all(g in readiness for g in gates))
    else:
        _check(checks, "readiness_has_all_gates", False, "readiness is not a dict")

    for section in ["Problem", "Desired Outcome", "Why This, Why Now?", "What If I Don't?",
                     "Rough Effort", "Open Questions", "Readiness Assessment"]:
        _check(checks, f"section_{section.lower().replace(' ', '_').replace('?', '').replace(',', '')}",
               f"## {section}" in body)


def _validate_project(fm, body, folder_name, path, checks):
    pid = fm.get("project_id", "")
    _check(checks, "project_id_present", bool(pid))
    _check(checks, "project_id_kebab", bool(re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", pid)) if pid else False)
    _check(checks, "project_id_matches_folder", pid == folder_name, f"id={pid}, folder={folder_name}")

    valid_statuses = {"on-deck", "active", "waiting", "stalled", "parked", "completed", "cancelled"}
    status = fm.get("status", "")
    _check(checks, "status_valid", status in valid_statuses, f"status={status}")

    _check(checks, "importance_valid", fm.get("importance") in ("low", "moderate", "high"))
    _check(checks, "importance_reason_present", bool(fm.get("importance_reason")))

    urgent = fm.get("urgent")
    _check(checks, "urgent_is_boolean", isinstance(urgent, bool))
    if urgent:
        _check(checks, "urgency_reason_present", bool(fm.get("urgency_reason")))

    _check(checks, "date_created_present", bool(fm.get("date_created")))

    if status in ("completed", "cancelled"):
        _check(checks, "date_completed_set", bool(fm.get("date_completed")))
    else:
        _check(checks, "date_completed_not_set", not bool(fm.get("date_completed")))

    for section in ["Goal", "Done When", "Milestones"]:
        _check(checks, f"section_{section.lower().replace(' ', '_')}",
               f"## {section}" in body)
    _check(checks, "section_work_log", "## Work Log" in body)

    proposal_exists = (path.parent / "PROPOSAL.md").exists()
    _check(checks, "proposal_md_exists", proposal_exists)


def _validate_retro(fm, body, checks):
    _check(checks, "project_id_present", bool(fm.get("project_id")))
    _check(checks, "retro_date_present", bool(fm.get("retro_date")))
    _check(checks, "outcome_valid", fm.get("outcome") in ("completed", "cancelled"))

    for section in ["Summary", "What Went Right", "What Went Wrong", "Lessons Learned",
                     "What Would I Change?"]:
        _check(checks, f"section_{section.lower().replace(' ', '_').replace('?', '')}",
               f"## {section}" in body)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="pm",
        description="Shared CLI for deterministic PM file operations."
    )
    sub = parser.add_subparsers(dest="command")

    # add-worklog
    wl = sub.add_parser("add-worklog", help="Append entries to a PROJECT.md work log")
    wl.add_argument("file", help="Path to PROJECT.md")
    wl.add_argument("--date", help="Entry date (YYYY-MM-DD). Defaults to today.")
    wl.add_argument("--entry", action="append", help="Plain work log entry (repeatable)")
    wl.add_argument("--status-change", help='Status transition, e.g. "on-deck -> active"')
    wl.add_argument("--milestone-complete", help='Milestone completion, e.g. \'Milestone 3 completed: "Build prototype"\'')

    # update-milestone
    ms = sub.add_parser("update-milestone", help="Update a milestone row")
    ms.add_argument("file", help="Path to PROJECT.md")
    ms.add_argument("--num", type=int, required=True, help="Milestone number")
    ms.add_argument("--status", required=True, help="New status (pending|in-progress|done|skipped)")
    ms.add_argument("--completed", help="Completed date (YYYY-MM-DD). Auto-set to today for done.")

    # update-frontmatter
    fm = sub.add_parser("update-frontmatter", help="Update YAML frontmatter fields")
    fm.add_argument("file", help="Path to .md file")
    fm.add_argument("--set", action="append", help='Key=value pair (repeatable), e.g. --set status=active')

    # move-project
    mv = sub.add_parser("move-project", help="Move a project folder to the correct lifecycle folder")
    mv.add_argument("folder", help="Path to the project folder")
    mv.add_argument("--to-status", required=True, help="Target status (determines destination folder)")

    # validate
    vl = sub.add_parser("validate", help="Run validation checks on a .md file")
    vl.add_argument("file", help="Path to .md file")
    vl.add_argument("--type", required=True, choices=["project", "proposal", "retro"],
                    help="Document type to validate against")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "add-worklog": cmd_add_worklog,
        "update-milestone": cmd_update_milestone,
        "update-frontmatter": cmd_update_frontmatter,
        "move-project": cmd_move_project,
        "validate": cmd_validate,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
