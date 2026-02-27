#!/usr/bin/env python3
"""
Import a project into the PM system from collected interview data.

Reads JSON from stdin. Operates in two modes based on target_status:

Proposal mode (target_status = "proposed"):
    Creates Proposed/{project_id}/PROPOSAL.md + subdirectories.

Project mode (target_status = anything else):
    Creates {StatusFolder}/{project_id}/PROJECT.md + PROPOSAL.md (retroactive stub)
    + subdirectories.

All output is JSON for agent consumption. Stdlib only.
"""

import datetime
import json
import pathlib
import sys

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


def bool_str(v):
    return "true" if v else "false"


def fmt_tags(tags):
    if tags:
        return "[" + ", ".join(str(t) for t in tags) + "]"
    return "[]"


def fmt_working_paths(paths):
    if not paths:
        return "working_paths: []"
    lines = ["working_paths:"] + [f"  - {p}" for p in paths]
    return "\n".join(lines)


def build_proposal_md(data, today, review_by):
    pid = data["project_id"]
    title = data["title"]
    tags = data.get("tags", [])
    source_path = data.get("source_path", "")

    readiness = data.get("readiness", {})
    gates = ["problem_defined", "outcome_clear", "effort_estimated",
             "motivation_justified", "alternatives_considered"]
    for g in gates:
        if g not in readiness:
            readiness[g] = False

    open_q = data.get("open_questions", [])
    open_q_str = "\n".join(f"- {q}" for q in open_q) if open_q else "- None yet."

    source_note = ""
    if source_path:
        source_note = f"\n\n*Imported from `{source_path}` on {today}.*"

    return f"""---
project_id: {pid}
title: "{title}"
date_proposed: {today}
last_updated: {today}
review_by: {review_by}
tags: {fmt_tags(tags)}
readiness:
  problem_defined: {bool_str(readiness["problem_defined"])}
  outcome_clear: {bool_str(readiness["outcome_clear"])}
  effort_estimated: {bool_str(readiness["effort_estimated"])}
  motivation_justified: {bool_str(readiness["motivation_justified"])}
  alternatives_considered: {bool_str(readiness["alternatives_considered"])}
---

# {title}

## Problem

{data.get("problem", "Not yet defined.")}

## Desired Outcome

{data.get("desired_outcome", "Not yet defined.")}

## Why This, Why Now?

{data.get("why_now", "Not yet assessed.")}

## What If I Don't?

{data.get("what_if_not", "Not yet assessed.")}

## Rough Effort

{data.get("effort", "Not yet estimated.")}

## Open Questions

{open_q_str}

## Readiness Assessment

{data.get("readiness_assessment", "Imported proposal -- readiness not yet assessed.")}{source_note}
"""


def build_retroactive_proposal_md(data, today):
    """Minimal PROPOSAL.md stub for projects that bypass the proposal stage."""
    pid = data["project_id"]
    title = data["title"]
    tags = data.get("tags", [])
    source_path = data.get("source_path", "")
    goal = data.get("goal", "See PROJECT.md.")
    done_when = data.get("done_when", "See PROJECT.md.")

    return f"""---
project_id: {pid}
title: "{title}"
date_proposed: {today}
last_updated: {today}
review_by: {today}
tags: {fmt_tags(tags)}
readiness:
  problem_defined: true
  outcome_clear: true
  effort_estimated: true
  motivation_justified: true
  alternatives_considered: true
---

# {title}

## Problem

{goal}

## Desired Outcome

{done_when}

## Why This, Why Now?

Imported from previous project management system. Bypassed standard proposal gate.

## What If I Don't?

N/A -- project was already in progress or completed at time of import.

## Rough Effort

See PROJECT.md milestones and scope.

## Open Questions

- None captured at import time.

## Readiness Assessment

All gates marked true. This proposal was generated retroactively during import from `{source_path}` on {today}. The project had already progressed past the proposal stage in its original system.
"""


def build_milestone_table(milestones):
    if not milestones:
        return ("| # | Milestone | Due | Status | Completed |\n"
                "|---|-----------|-----|--------|-----------|")

    rows = []
    for m in milestones:
        num = m.get("num", "")
        name = m.get("name", "")
        due = m.get("due", "")
        status = m.get("status", "pending")
        completed = m.get("completed", "")
        rows.append(f"| {num} | {name} | {due} | {status} | {completed} |")

    header = "| # | Milestone | Due | Status | Completed |"
    sep = "|---|-----------|-----|--------|-----------|"
    return "\n".join([header, sep] + rows)


def build_work_log(data, today):
    """Build the work log section with import entry + any historical entries."""
    target_status = data["target_status"]
    source_path = data.get("source_path", "unknown source")

    import_lines = [f"- *Status: imported as {target_status}*"]
    context_parts = [f"Imported from `{source_path}`."]

    if target_status in ("waiting", "stalled", "parked"):
        reason = data.get("pause_reason", "")
        if reason:
            context_parts.append(f"Originally {target_status} because: {reason}")
    elif target_status == "cancelled":
        reason = data.get("cancel_reason", "")
        if reason:
            context_parts.append(f"Cancelled because: {reason}")

    import_lines.append(f"- {' '.join(context_parts)}")

    entries = []
    entries.append({"date": today, "lines": import_lines})

    for entry in data.get("work_log_entries", []):
        edate = entry.get("date", today)
        elines = [f"- {e}" for e in entry.get("entries", [])]
        if elines:
            entries.append({"date": edate, "lines": elines})

    entries.sort(key=lambda e: e["date"], reverse=True)

    merged = {}
    for entry in entries:
        d = entry["date"]
        if d not in merged:
            merged[d] = []
        merged[d].extend(entry["lines"])

    sorted_dates = sorted(merged.keys(), reverse=True)
    sections = []
    for d in sorted_dates:
        sections.append(f"### {d}")
        sections.extend(merged[d])
        sections.append("")

    return "\n".join(sections).rstrip()


def build_project_md(data, today):
    pid = data["project_id"]
    title = data["title"]
    status = data["target_status"]
    importance = data.get("importance", "moderate")
    importance_reason = data.get("importance_reason", "Imported -- assess after import")
    urgent = data.get("urgent", False)
    urgency_reason = data.get("urgency_reason", "")
    group = data.get("group", "")
    tags = data.get("tags", [])
    date_created = data.get("date_created", today)
    date_completed = data.get("date_completed", "")

    if status in ("completed", "cancelled") and not date_completed:
        date_completed = today

    working_paths = list(data.get("working_paths", []))
    source_path = data.get("source_path", "")
    if source_path and source_path not in working_paths:
        working_paths.insert(0, source_path)

    goal = data.get("goal", "Imported project -- goal not yet documented.")
    done_when = data.get("done_when", "Imported project -- completion criteria not yet documented.")
    scope = data.get("scope", "")
    obstacles = data.get("obstacles", "")
    milestones = data.get("milestones", [])
    open_questions = data.get("open_questions", [])

    oq_str = "\n".join(f"- {q}" for q in open_questions) if open_questions else "- None captured at import time."

    scope_section = ""
    if scope:
        scope_section = f"\n## Scope\n\n{scope}\n"

    obstacles_section = ""
    if obstacles:
        obstacles_section = f"\n## Obstacles\n\n{obstacles}\n"

    work_log = build_work_log(data, today)
    milestone_table = build_milestone_table(milestones)

    dc_field = date_completed if date_completed else ""
    ir_quoted = f'"{importance_reason}"' if importance_reason else '""'
    ur_quoted = f'"{urgency_reason}"' if urgency_reason else '""'

    return f"""---
project_id: {pid}
title: "{title}"
status: {status}
importance: {importance}
importance_reason: {ir_quoted}
urgent: {bool_str(urgent)}
urgency_reason: {ur_quoted}
group: {group}
date_created: {date_created}
last_updated: {today}
date_completed: {dc_field}
tags: {fmt_tags(tags)}
{fmt_working_paths(working_paths)}
---

# {title}

## Goal

{goal}
{scope_section}
## Done When

{done_when}
{obstacles_section}
## Milestones

{milestone_table}

## Open Questions

{oq_str}

---

## Work Log

{work_log}
"""


def main():
    data = json.load(sys.stdin)

    required_common = ["project_id", "title", "target_status", "source_path"]
    missing = [f for f in required_common if f not in data or not data[f]]
    if missing:
        print(json.dumps({"ok": False, "error": f"Missing required fields: {', '.join(missing)}"}))
        sys.exit(1)

    pid = data["project_id"]
    target_status = data["target_status"]

    if target_status not in STATUS_FOLDER_MAP:
        print(json.dumps({"ok": False,
                          "error": f"Invalid target_status '{target_status}'. "
                                   f"Must be one of: {', '.join(sorted(STATUS_FOLDER_MAP))}"}))
        sys.exit(1)

    today = datetime.date.today().strftime("%Y-%m-%d")
    review_by = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")

    script_dir = pathlib.Path(__file__).resolve().parent
    workspace_root = script_dir.parents[3]
    target_folder_name = STATUS_FOLDER_MAP[target_status]
    target_parent = workspace_root / target_folder_name
    project_dir = target_parent / pid

    if project_dir.exists():
        print(json.dumps({"ok": False, "error": f"Folder already exists: {project_dir}"}))
        sys.exit(1)

    project_dir.mkdir(parents=True)

    created_files = []

    if target_status == "proposed":
        required_proposal = ["problem", "desired_outcome", "why_now",
                             "what_if_not", "effort", "readiness", "readiness_assessment"]
        missing = [f for f in required_proposal if f not in data or not data[f]]
        if missing:
            project_dir.rmdir()
            print(json.dumps({"ok": False, "error": f"Missing proposal fields: {', '.join(missing)}"}))
            sys.exit(1)

        content = build_proposal_md(data, today, review_by)
        proposal_path = project_dir / "PROPOSAL.md"
        proposal_path.write_text(content, encoding="utf-8")
        created_files.append(str(proposal_path))

        readiness = data.get("readiness", {})
        gates = ["problem_defined", "outcome_clear", "effort_estimated",
                 "motivation_justified", "alternatives_considered"]
        gates_passed = sum(1 for g in gates if readiness.get(g))

        print(json.dumps({
            "ok": True,
            "mode": "proposal",
            "folder": str(project_dir),
            "files": created_files,
            "target_status": target_status,
            "gates_passed": gates_passed,
            "gates_total": len(gates),
        }))

    else:
        required_project = ["goal", "done_when", "importance", "importance_reason"]
        missing = [f for f in required_project if f not in data or not data[f]]
        if missing:
            import shutil
            shutil.rmtree(project_dir)
            print(json.dumps({"ok": False, "error": f"Missing project fields: {', '.join(missing)}"}))
            sys.exit(1)

        project_content = build_project_md(data, today)
        project_path = project_dir / "PROJECT.md"
        project_path.write_text(project_content, encoding="utf-8")
        created_files.append(str(project_path))

        proposal_content = build_retroactive_proposal_md(data, today)
        proposal_path = project_dir / "PROPOSAL.md"
        proposal_path.write_text(proposal_content, encoding="utf-8")
        created_files.append(str(proposal_path))

        print(json.dumps({
            "ok": True,
            "mode": "project",
            "folder": str(project_dir),
            "files": created_files,
            "target_status": target_status,
        }))


if __name__ == "__main__":
    main()
