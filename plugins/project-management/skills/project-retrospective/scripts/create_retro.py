#!/usr/bin/env python3
"""
Generate a RETRO.md from collected interview data.

Reads JSON from stdin with:
    project_folder  (str, required)  path to the project folder
    project_id      (str, required)
    retro_date      (str, optional)  YYYY-MM-DD, defaults to today
    outcome         (str, required)  "completed" or "cancelled"
    summary         (str, required)  narrative paragraph
    went_right      (list[str], required)  bullet points
    went_wrong      (list[str], required)  bullet points
    lessons         (list[str], required)  bullet points
    would_change    (list[str], required)  bullet points

Writes RETRO.md into the project folder.
"""

import datetime
import json
import pathlib
import re
import sys


def main():
    data = json.load(sys.stdin)

    required = ["project_folder", "project_id", "outcome", "summary",
                "went_right", "went_wrong", "lessons", "would_change"]
    missing = [f for f in required if f not in data or not data[f]]
    if missing:
        print(json.dumps({"ok": False, "error": f"Missing required fields: {', '.join(missing)}"}))
        sys.exit(1)

    project_folder = pathlib.Path(data["project_folder"]).resolve()
    if not project_folder.is_dir():
        print(json.dumps({"ok": False, "error": f"Not a directory: {project_folder}"}))
        sys.exit(1)

    retro_path = project_folder / "RETRO.md"
    if retro_path.exists():
        print(json.dumps({"ok": False, "error": f"RETRO.md already exists: {retro_path}"}))
        sys.exit(1)

    pid = data["project_id"]
    retro_date = data.get("retro_date") or datetime.date.today().strftime("%Y-%m-%d")
    outcome = data["outcome"]

    title = pid.replace("-", " ").title()
    project_md = project_folder / "PROJECT.md"
    if project_md.exists():
        text = project_md.read_text(encoding="utf-8")
        m = re.search(r'^title:\s*"?(.+?)"?\s*$', text, re.MULTILINE)
        if m:
            title = m.group(1)

    def bullets(items):
        return "\n".join(f"- {item}" for item in items)

    content = f"""---
project_id: {pid}
retro_date: {retro_date}
outcome: {outcome}
---

# Retrospective: {title}

## Summary

{data["summary"]}

## What Went Right

{bullets(data["went_right"])}

## What Went Wrong

{bullets(data["went_wrong"])}

## Lessons Learned

{bullets(data["lessons"])}

## What Would I Change?

{bullets(data["would_change"])}
"""

    retro_path.write_text(content, encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "retro_md": str(retro_path),
        "project_id": pid,
    }))


if __name__ == "__main__":
    main()
