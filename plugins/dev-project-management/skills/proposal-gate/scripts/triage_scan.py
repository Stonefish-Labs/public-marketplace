#!/usr/bin/env python3
"""
Scan Proposed/ and produce a JSON summary of all proposals for triage.

Usage:
    python3 triage_scan.py [workspace_root]

If workspace_root is omitted, walks up from the script location to find it.

Output (JSON):
    {
      "ok": true,
      "proposals": [
        {
          "project_id": "...",
          "title": "...",
          "date_proposed": "YYYY-MM-DD",
          "age_days": N,
          "review_by": "YYYY-MM-DD",
          "is_overdue": true/false,
          "gates_passed": N,
          "gates_total": 5
        },
        ...
      ]
    }
"""

import datetime
import json
import os
import pathlib
import re
import sys


READINESS_GATES = [
    "problem_defined", "outcome_clear", "effort_estimated",
    "motivation_justified", "alternatives_considered",
]


def find_workspace_root(start):
    cur = pathlib.Path(start).resolve()
    lifecycle = {"Proposed", "On-Deck", "Active", "Paused", "Archive"}
    while cur != cur.parent:
        if any((cur / d).is_dir() for d in lifecycle):
            return cur
        cur = cur.parent
    return pathlib.Path(start).resolve()


def parse_frontmatter(text):
    """Extract key-value pairs from YAML frontmatter, including nested readiness block."""
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm = {}
    in_readiness = False
    for line in parts[1].strip().split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        indent = len(line) - len(line.lstrip())
        if indent >= 2 and in_readiness:
            m = re.match(r"^(\w[\w_]*):\s*(.+)$", stripped)
            if m:
                fm.setdefault("readiness", {})[m.group(1)] = m.group(2).strip().lower() == "true"
                continue
        in_readiness = False
        m = re.match(r"^([\w][\w_-]*):\s*(.*)$", stripped)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip().strip('"').strip("'")
        if key == "readiness":
            in_readiness = True
            fm["readiness"] = {}
            continue
        fm[key] = val
    return fm


def scan(root):
    """Scan all proposal folders and return summary data."""
    proposed = pathlib.Path(root) / "Proposed"
    if not proposed.is_dir():
        return []

    today = datetime.date.today()
    results = []

    for entry in sorted(proposed.iterdir()):
        if not entry.is_dir():
            continue
        proposal_md = entry / "PROPOSAL.md"
        if not proposal_md.exists():
            continue

        text = proposal_md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)

        pid = fm.get("project_id", entry.name)
        title = fm.get("title", pid)
        date_proposed = fm.get("date_proposed", "")
        review_by = fm.get("review_by", "")

        age_days = 0
        if date_proposed:
            try:
                proposed_date = datetime.datetime.strptime(date_proposed, "%Y-%m-%d").date()
                age_days = (today - proposed_date).days
            except ValueError:
                pass

        is_overdue = False
        if review_by:
            try:
                rb_date = datetime.datetime.strptime(review_by, "%Y-%m-%d").date()
                is_overdue = today > rb_date
            except ValueError:
                pass

        readiness = fm.get("readiness", {})
        gates_passed = sum(1 for g in READINESS_GATES if readiness.get(g, False))

        results.append({
            "project_id": pid,
            "title": title,
            "date_proposed": date_proposed,
            "age_days": age_days,
            "review_by": review_by,
            "is_overdue": is_overdue,
            "gates_passed": gates_passed,
            "gates_total": len(READINESS_GATES),
        })

    return results


def main():
    if len(sys.argv) > 1:
        root = pathlib.Path(sys.argv[1]).resolve()
    else:
        root = find_workspace_root(pathlib.Path(__file__).resolve().parent)

    proposals = scan(root)
    print(json.dumps({"ok": True, "proposals": proposals}, indent=2))


if __name__ == "__main__":
    main()
