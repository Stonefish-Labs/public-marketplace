#!/usr/bin/env python3
"""
Create a PROPOSAL.md and folder structure from collected interview data.

Reads JSON from stdin with the following fields:
    project_id          (str, required) kebab-case identifier
    title               (str, required)
    tags                (list[str], optional)
    problem             (str, required)
    desired_outcome     (str, required)
    why_now             (str, required)
    what_if_not         (str, required)
    effort              (str, required)
    open_questions      (list[str], optional)
    readiness           (dict, required) keys: problem_defined, outcome_clear,
                        effort_estimated, motivation_justified, alternatives_considered
    readiness_assessment (str, required) agent-written summary

Creates:
    Proposed/{project_id}/
        PROPOSAL.md
"""

import datetime
import json
import pathlib
import sys


def main():
    data = json.load(sys.stdin)

    required = ["project_id", "title", "problem", "desired_outcome",
                "why_now", "what_if_not", "effort", "readiness", "readiness_assessment"]
    missing = [f for f in required if f not in data or not data[f]]
    if missing:
        print(json.dumps({"ok": False, "error": f"Missing required fields: {', '.join(missing)}"}))
        sys.exit(1)

    pid = data["project_id"]
    title = data["title"]
    tags = data.get("tags", [])
    today = datetime.date.today().strftime("%Y-%m-%d")
    review_by = data.get("review_by") or (
        datetime.date.today() + datetime.timedelta(days=30)
    ).strftime("%Y-%m-%d")

    readiness = data["readiness"]
    gates = ["problem_defined", "outcome_clear", "effort_estimated",
             "motivation_justified", "alternatives_considered"]
    for g in gates:
        if g not in readiness:
            readiness[g] = False

    tags_str = "[" + ", ".join(tags) + "]" if tags else "[]"

    def bool_str(v):
        return "true" if v else "false"

    open_q = data.get("open_questions", [])
    open_q_str = "\n".join(f"- {q}" for q in open_q) if open_q else "- None yet."

    content = f"""---
project_id: {pid}
title: "{title}"
date_proposed: {today}
last_updated: {today}
review_by: {review_by}
tags: {tags_str}
readiness:
  problem_defined: {bool_str(readiness["problem_defined"])}
  outcome_clear: {bool_str(readiness["outcome_clear"])}
  effort_estimated: {bool_str(readiness["effort_estimated"])}
  motivation_justified: {bool_str(readiness["motivation_justified"])}
  alternatives_considered: {bool_str(readiness["alternatives_considered"])}
---

# {title}

## Problem

{data["problem"]}

## Desired Outcome

{data["desired_outcome"]}

## Why This, Why Now?

{data["why_now"]}

## What If I Don't?

{data["what_if_not"]}

## Rough Effort

{data["effort"]}

## Open Questions

{open_q_str}

## Readiness Assessment

{data["readiness_assessment"]}
"""

    script_dir = pathlib.Path(__file__).resolve().parent
    workspace_root = script_dir.parents[3]
    proposed_dir = workspace_root / "Proposed"
    project_dir = proposed_dir / pid

    if project_dir.exists():
        print(json.dumps({"ok": False, "error": f"Folder already exists: {project_dir}"}))
        sys.exit(1)

    project_dir.mkdir(parents=True)

    proposal_path = project_dir / "PROPOSAL.md"
    proposal_path.write_text(content, encoding="utf-8")

    gates_passed = sum(1 for g in gates if readiness.get(g))
    print(json.dumps({
        "ok": True,
        "folder": str(project_dir),
        "proposal": str(proposal_path),
        "gates_passed": gates_passed,
        "gates_total": len(gates),
    }))


if __name__ == "__main__":
    main()
