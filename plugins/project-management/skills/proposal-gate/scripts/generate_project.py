#!/usr/bin/env python3
"""
Generate a PROJECT.md from an existing PROPOSAL.md during promotion to On-Deck.

Reads JSON from stdin with:
    proposal_path       (str, required)  path to the PROPOSAL.md
    importance          (str, required)  low | moderate | high
    importance_reason   (str, required)
    urgent              (bool, required)
    urgency_reason      (str, optional, required if urgent)
    group               (str, optional)
    working_paths       (list[str], optional)

The script reads the PROPOSAL.md, maps sections (Problem -> Goal,
Desired Outcome -> Done When), carries forward tags and open questions,
and writes PROJECT.md into the same folder.
"""

import datetime
import json
import pathlib
import re
import sys


def parse_frontmatter(text):
    """Extract flat key-value pairs from YAML frontmatter."""
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm = {}
    for line in parts[1].strip().split("\n"):
        stripped = line.strip()
        m = re.match(r"^([\w][\w_-]*):\s*(.*)$", stripped)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            fm[key] = [v.strip().strip('"').strip("'") for v in inner.split(",")] if inner else []
        elif val.startswith('"') and val.endswith('"'):
            fm[key] = val[1:-1]
        elif val.startswith("'") and val.endswith("'"):
            fm[key] = val[1:-1]
        else:
            fm[key] = val
    return fm


def extract_section(text, heading):
    """Extract content under a ## heading, stopping at the next ## or end."""
    pattern = re.compile(r"^## " + re.escape(heading) + r"\s*$", re.MULTILINE)
    m = pattern.search(text)
    if not m:
        return ""
    start = m.end()
    next_heading = re.search(r"^## ", text[start:], re.MULTILINE)
    if next_heading:
        end = start + next_heading.start()
    else:
        end = len(text)
    return text[start:end].strip()


def main():
    data = json.load(sys.stdin)

    required = ["proposal_path", "importance", "importance_reason", "urgent"]
    missing = [f for f in required if f not in data]
    if missing:
        print(json.dumps({"ok": False, "error": f"Missing required fields: {', '.join(missing)}"}))
        sys.exit(1)

    proposal_path = pathlib.Path(data["proposal_path"]).resolve()
    if not proposal_path.exists():
        print(json.dumps({"ok": False, "error": f"PROPOSAL.md not found: {proposal_path}"}))
        sys.exit(1)

    proposal_text = proposal_path.read_text(encoding="utf-8")
    pfm = parse_frontmatter(proposal_text)

    pid = pfm.get("project_id", proposal_path.parent.name)
    title = pfm.get("title", pid)
    tags = pfm.get("tags", [])
    today = datetime.date.today().strftime("%Y-%m-%d")

    problem = extract_section(proposal_text, "Problem")
    desired_outcome = extract_section(proposal_text, "Desired Outcome")
    open_questions = extract_section(proposal_text, "Open Questions")

    importance = data["importance"]
    importance_reason = data["importance_reason"]
    urgent = data["urgent"]
    urgency_reason = data.get("urgency_reason", "")
    group = data.get("group", "")
    working_paths = data.get("working_paths", [])

    tags_str = "[" + ", ".join(tags) + "]" if tags else "[]"
    urgent_str = "true" if urgent else "false"

    wp_block = ""
    if working_paths:
        wp_block = "working_paths:\n" + "\n".join(f"  - {p}" for p in working_paths)
    else:
        wp_block = "working_paths: []"

    scope_text = ""
    raw_scope = extract_section(proposal_text, "Rough Effort")
    if raw_scope:
        scope_text = f"\n## Scope\n\nOriginal effort estimate from proposal: {raw_scope}\n"

    oq_text = open_questions if open_questions else "- None yet."

    content = f"""---
project_id: {pid}
title: "{title}"
status: on-deck
importance: {importance}
importance_reason: "{importance_reason}"
urgent: {urgent_str}
urgency_reason: "{urgency_reason}"
group: {group}
date_created: {today}
last_updated: {today}
date_completed:
tags: {tags_str}
{wp_block}
---

# {title}

## Goal

{problem}
{scope_text}
## Done When

{desired_outcome}

## Milestones

| # | Milestone | Due | Status | Completed |
|---|-----------|-----|--------|-----------|

## Open Questions

{oq_text}

---

## Work Log

### {today}
- *Status: proposed -> on-deck*
- Promoted from proposal. All readiness gates passed.
"""

    project_md = proposal_path.parent / "PROJECT.md"
    if project_md.exists():
        print(json.dumps({"ok": False, "error": f"PROJECT.md already exists: {project_md}"}))
        sys.exit(1)

    project_md.write_text(content, encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "project_md": str(project_md),
        "project_id": pid,
        "status": "on-deck",
    }))


if __name__ == "__main__":
    main()
