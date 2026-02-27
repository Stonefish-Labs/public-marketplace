#!/usr/bin/env python3
"""
sync_marketplace.py - Audit a marketplace catalog entry for source existence,
version consistency, metadata completeness, and staleness.

Usage:
    python3 sync_marketplace.py --marketplace <dir> --plugin '<entry-json>'
    python3 sync_marketplace.py --marketplace <dir> --all

Output: JSON to stdout with structure:
{
  "plugin": "<name>",
  "status": "healthy" | "warning" | "error",
  "issues": [
    {"level": "ERROR"|"WARN"|"INFO", "code": "<code>", "message": "<msg>", "fix": "<suggestion>"}
  ]
}
"""

import argparse
import base64
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run(cmd, capture=True):
    """Run a shell command. Returns (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd, shell=True, capture_output=capture, text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def gh_available():
    code, _, _ = run("gh --version")
    return code == 0


def check_skill_paths(plugin_dir: Path, plugin_manifest: dict):
    """Validate declared skill paths inside plugin.json."""
    issues = []
    declared_skills = []

    legacy_skill = plugin_dir / "SKILL.md"
    if legacy_skill.exists():
        issues.append({
            "level": "ERROR",
            "code": "LEGACY_SKILL_LOCATION",
            "message": "Top-level SKILL.md is not allowed; skills must live under skills/",
            "fix": "Move SKILL.md to skills/<skill-name>/SKILL.md and update plugin.json"
        })

    skills = plugin_manifest.get("skills")
    if isinstance(skills, list):
        declared_skills.extend(skills)

    components = plugin_manifest.get("components")
    if isinstance(components, dict):
        component_skills = components.get("skills")
        if isinstance(component_skills, list):
            declared_skills.extend(component_skills)

    if declared_skills:
        if (plugin_dir / "scripts").is_dir():
            issues.append({
                "level": "ERROR",
                "code": "LEGACY_SCRIPTS_LOCATION",
                "message": "Top-level scripts/ is not allowed for skill plugins; move scripts under skills/",
                "fix": "Move scripts to skills/<skill-name>/scripts/ and update SKILL.md references"
            })
        if (plugin_dir / "references").is_dir():
            issues.append({
                "level": "ERROR",
                "code": "LEGACY_REFERENCES_LOCATION",
                "message": "Top-level references/ is not allowed for skill plugins; move references under skills/",
                "fix": "Move references to skills/<skill-name>/references/ and update SKILL.md references"
            })

    for skill_path in declared_skills:
        if not isinstance(skill_path, str) or not skill_path.strip():
            issues.append({
                "level": "ERROR",
                "code": "SKILL_PATH_INVALID",
                "message": "Skill path must be a non-empty string",
                "fix": "Use skill paths like 'skills/<skill-name>/SKILL.md'"
            })
            continue

        normalized = skill_path.replace("\\", "/")
        if not normalized.startswith("skills/"):
            issues.append({
                "level": "ERROR",
                "code": "SKILL_PATH_OUTSIDE_SKILLS_DIR",
                "message": f"Skill path must be under skills/: {skill_path}",
                "fix": f"Move the skill to skills/<skill-name>/SKILL.md and update path '{skill_path}'"
            })

        skill_file = (plugin_dir / skill_path).resolve()
        if not skill_file.exists():
            issues.append({
                "level": "ERROR",
                "code": "SKILL_FILE_MISSING",
                "message": f"Declared skill file not found: {skill_path}",
                "fix": f"Create {skill_path} or remove it from plugin.json"
            })

    return issues


def check_relative_source(marketplace_dir: Path, source_path: str, catalog_version: str):
    """Check a relative-path plugin source."""
    issues = []

    # Resolve path relative to marketplace root
    plugin_dir = (marketplace_dir / source_path).resolve()
    plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"

    if not plugin_dir.exists():
        issues.append({
            "level": "ERROR",
            "code": "SOURCE_NOT_FOUND",
            "message": f"Source directory not found: {source_path}",
            "fix": f"Remove this entry or restore the directory at {source_path}"
        })
        return issues

    if not plugin_json_path.exists():
        issues.append({
            "level": "ERROR",
            "code": "PLUGIN_JSON_MISSING",
            "message": f"No .claude-plugin/plugin.json found at {source_path}",
            "fix": "Restore plugin.json or remove this entry"
        })
        return issues

    try:
        with open(plugin_json_path) as f:
            plugin_manifest = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        issues.append({
            "level": "ERROR",
            "code": "PLUGIN_JSON_INVALID",
            "message": f"Cannot parse plugin.json at {source_path}: {e}",
            "fix": "Fix the plugin.json syntax"
        })
        return issues

    source_version = plugin_manifest.get("version")
    if catalog_version and source_version and catalog_version != source_version:
        issues.append({
            "level": "WARN",
            "code": "VERSION_MISMATCH",
            "message": f"Version mismatch: catalog={catalog_version}, source={source_version}",
            "fix": f"Update catalog entry version to {source_version}"
        })

    issues.extend(check_skill_paths(plugin_dir, plugin_manifest))

    return issues


def check_github_source(source_obj: dict, catalog_version: str):
    """Check a GitHub plugin source."""
    issues = []
    repo = source_obj.get("repo", "")

    if not repo:
        issues.append({
            "level": "ERROR",
            "code": "MISSING_REPO",
            "message": "GitHub source is missing 'repo' field",
            "fix": "Add 'repo': 'owner/repo' to the source object"
        })
        return issues

    # Check repo existence
    code, out, _ = run(f"gh repo view {repo} --json name 2>/dev/null")
    if code != 0:
        issues.append({
            "level": "ERROR",
            "code": "REPO_UNREACHABLE",
            "message": f"GitHub repo unreachable: {repo}",
            "fix": "Verify the repo exists and you have access, or remove this entry"
        })
        return issues

    # Check staleness
    code, pushed_at_raw, _ = run(f"gh api repos/{repo} --jq '.pushed_at'")
    if code == 0 and pushed_at_raw:
        try:
            pushed_at = datetime.fromisoformat(pushed_at_raw.rstrip("Z")).replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            age_days = (now - pushed_at).days
            if age_days > 180:
                months = age_days // 30
                issues.append({
                    "level": "WARN",
                    "code": "STALE_REPO",
                    "message": f"Last updated {months} months ago ({pushed_at.strftime('%Y-%m-%d')})",
                    "fix": "Check if the plugin is still actively maintained"
                })
        except (ValueError, TypeError):
            pass

    # Version consistency
    ref = source_obj.get("ref", "")
    ref_param = f"?ref={ref}" if ref else ""
    code, content_raw, _ = run(
        f"gh api repos/{repo}/contents/.claude-plugin/plugin.json{ref_param} --jq '.content' 2>/dev/null"
    )
    if code == 0 and content_raw:
        try:
            decoded = base64.b64decode(content_raw.replace("\\n", "")).decode("utf-8")
            plugin_manifest = json.loads(decoded)
            source_version = plugin_manifest.get("version")
            if catalog_version and source_version and catalog_version != source_version:
                issues.append({
                    "level": "WARN",
                    "code": "VERSION_MISMATCH",
                    "message": f"Version mismatch: catalog={catalog_version}, source={source_version}",
                    "fix": f"Update catalog entry version to {source_version}"
                })
        except Exception:
            pass  # Best-effort version check

    return issues


def check_url_source(source_obj: dict):
    """Check a git URL plugin source."""
    issues = []
    url = source_obj.get("url", "")

    if not url:
        issues.append({
            "level": "ERROR",
            "code": "MISSING_URL",
            "message": "URL source is missing 'url' field",
            "fix": "Add 'url' field to the source object"
        })
        return issues

    code, _, _ = run(f"git ls-remote {url} HEAD 2>/dev/null")
    if code != 0:
        issues.append({
            "level": "ERROR",
            "code": "REPO_UNREACHABLE",
            "message": f"Git URL unreachable: {url}",
            "fix": "Verify the URL is accessible or remove this entry"
        })

    return issues


def check_metadata(entry: dict):
    """Check entry for missing optional-but-recommended metadata."""
    issues = []
    for field in ["description", "version", "author", "keywords"]:
        if not entry.get(field):
            issues.append({
                "level": "INFO",
                "code": f"MISSING_{field.upper()}",
                "message": f"Missing field: {field}",
                "fix": f"Add '{field}' to this catalog entry"
            })
    return issues


def check_entry(marketplace_dir: Path, entry: dict):
    """Run all checks for a single catalog entry."""
    issues = []
    name = entry.get("name", "<unnamed>")
    source = entry.get("source")
    catalog_version = entry.get("version", "")

    if not source:
        issues.append({
            "level": "ERROR",
            "code": "MISSING_SOURCE",
            "message": "Entry has no 'source' field",
            "fix": "Add a 'source' field to this entry"
        })
    elif isinstance(source, str):
        # Relative path
        issues.extend(check_relative_source(marketplace_dir, source, catalog_version))
    elif isinstance(source, dict):
        source_type = source.get("source", "")
        if source_type == "github":
            issues.extend(check_github_source(source, catalog_version))
        elif source_type == "url":
            issues.extend(check_url_source(source))
        elif source_type in ("npm", "pip"):
            issues.append({
                "level": "INFO",
                "code": "UNVERIFIED_SOURCE",
                "message": f"{source_type} sources cannot be verified by this tool",
                "fix": None
            })
        else:
            issues.append({
                "level": "WARN",
                "code": "UNKNOWN_SOURCE_TYPE",
                "message": f"Unknown source type: '{source_type}'",
                "fix": "Use 'github', 'url', 'npm', or 'pip' as the source type"
            })

    issues.extend(check_metadata(entry))

    # Determine overall status
    levels = [i["level"] for i in issues]
    if "ERROR" in levels:
        status = "error"
    elif "WARN" in levels:
        status = "warning"
    elif issues:
        status = "info"
    else:
        status = "healthy"

    return {"plugin": name, "status": status, "issues": issues}


def main():
    parser = argparse.ArgumentParser(description="Audit a marketplace catalog entry.")
    parser.add_argument("--marketplace", required=True, help="Path to marketplace directory")
    parser.add_argument("--plugin", help="JSON string of a single plugin entry to check")
    parser.add_argument("--all", action="store_true", help="Check all entries in marketplace.json")
    args = parser.parse_args()

    marketplace_dir = Path(args.marketplace).resolve()
    marketplace_json = marketplace_dir / ".claude-plugin" / "marketplace.json"

    if not marketplace_json.exists():
        print(json.dumps({
            "error": f"marketplace.json not found at {marketplace_json}"
        }))
        sys.exit(1)

    try:
        with open(marketplace_json) as f:
            catalog = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(json.dumps({"error": f"Cannot parse marketplace.json: {e}"}))
        sys.exit(1)

    if not gh_available():
        print(json.dumps({
            "error": "gh CLI is not installed or not in PATH. GitHub source checks will not work.",
            "install": "https://cli.github.com"
        }))
        sys.exit(1)

    if args.plugin:
        try:
            entry = json.loads(args.plugin)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid plugin JSON: {e}"}))
            sys.exit(1)
        result = check_entry(marketplace_dir, entry)
        print(json.dumps(result, indent=2))

    elif args.all:
        plugins = catalog.get("plugins", [])
        results = [check_entry(marketplace_dir, entry) for entry in plugins]
        summary = {
            "marketplace": catalog.get("name", "unknown"),
            "total": len(results),
            "healthy": sum(1 for r in results if r["status"] == "healthy"),
            "warnings": sum(1 for r in results if r["status"] in ("warning", "info")),
            "errors": sum(1 for r in results if r["status"] == "error"),
            "results": results
        }
        print(json.dumps(summary, indent=2))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
