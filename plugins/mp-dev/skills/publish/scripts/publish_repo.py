#!/usr/bin/env python3
"""
publish_repo.py — Publish a local component or plugin directory to GitHub.

Handles:
  - Asset detection and classification
  - git init + initial commit if not already a repo
  - .gitignore injection from bundled template
  - GitHub repo creation or update via gh CLI
  - Topic tagging
  - Marketplace entry generation (optional)
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ASSET_TOPIC_MAP = {
    "skill": "skill",
    "agent": "subagent",
    "hook": "hook",
    "mcp": "mcp-server",
    "command": "command",
}

LANGUAGE_PATTERNS = {
    "python": [r"\.py$"],
    "bash": [r"\.sh$"],
    "javascript": [r"\.js$"],
    "typescript": [r"\.ts$"],
}

GITIGNORE_TEMPLATE = os.path.join(
    os.path.dirname(__file__), "..", "assets", "gitignore-template.txt"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(cmd, check=True, capture=False):
    """Run a shell command. Returns CompletedProcess."""
    result = subprocess.run(
        cmd,
        shell=True,
        check=False,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        text=True,
    )
    if check and result.returncode != 0:
        err = result.stderr.strip() if capture and result.stderr else ""
        print(f"Error running: {cmd}")
        if err:
            print(err)
        sys.exit(1)
    return result


def check_gh():
    """Verify gh CLI is installed and authenticated."""
    if not shutil.which("gh"):
        print("Error: 'gh' CLI is not installed. Install it from https://cli.github.com/")
        sys.exit(1)
    result = run("gh auth status", check=False, capture=True)
    if result.returncode != 0:
        print("Error: Not authenticated with gh. Run 'gh auth login' first.")
        sys.exit(1)


def is_git_repo(path):
    result = subprocess.run(
        ["git", "-C", path, "rev-parse", "--is-inside-work-tree"],
        capture_output=True, text=True
    )
    return result.returncode == 0


def has_commits(path):
    result = subprocess.run(
        ["git", "-C", path, "log", "--oneline", "-1"],
        capture_output=True, text=True
    )
    return bool(result.stdout.strip())


def inject_gitignore(target):
    """Copy the bundled .gitignore template if one doesn't exist."""
    dest = os.path.join(target, ".gitignore")
    if os.path.exists(dest):
        return False
    if os.path.exists(GITIGNORE_TEMPLATE):
        shutil.copy(GITIGNORE_TEMPLATE, dest)
        print("Added .gitignore from template.")
        return True
    # Minimal fallback if template is missing
    with open(dest, "w") as f:
        f.write("__pycache__/\n*.pyc\n*.pyo\n.env\n.DS_Store\n")
    print("Added minimal .gitignore (template not found).")
    return True


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def detect_assets(target):
    """
    Scan target directory and return a dict describing what was found.

    Returns:
        {
            "is_plugin": bool,
            "plugin_name": str | None,
            "plugin_version": str | None,
            "plugin_description": str | None,
            "assets": list[str],   # e.g. ["skill", "hook", "mcp"]
            "languages": list[str],
        }
    """
    info = {
        "is_plugin": False,
        "plugin_name": None,
        "plugin_version": None,
        "plugin_description": None,
        "assets": [],
        "languages": [],
    }

    # Plugin manifest
    manifest_path = os.path.join(target, ".claude-plugin", "plugin.json")
    if os.path.exists(manifest_path):
        info["is_plugin"] = True
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
            info["plugin_name"] = manifest.get("name")
            info["plugin_version"] = manifest.get("version")
            info["plugin_description"] = manifest.get("description")
        except (json.JSONDecodeError, OSError):
            pass

    # Skills
    skills_dir = os.path.join(target, "skills")
    if os.path.isdir(skills_dir):
        for root, _, files in os.walk(skills_dir):
            if "SKILL.md" in files:
                info["assets"].append("skill")
                break

    # Agents
    agents_dir = os.path.join(target, "agents")
    if os.path.isdir(agents_dir):
        for root, _, files in os.walk(agents_dir):
            for fname in files:
                if fname.endswith(".md"):
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath) as f:
                            content = f.read(200)
                        if content.startswith("---"):
                            info["assets"].append("agent")
                            break
                    except OSError:
                        pass
            else:
                continue
            break

    # Hooks
    hook_paths = [
        os.path.join(target, ".claude-plugin", "hooks.json"),
        os.path.join(target, "hooks", "hooks.json"),
        os.path.join(target, ".hooks.json"),
    ]
    if any(os.path.exists(p) for p in hook_paths):
        info["assets"].append("hook")

    # MCP servers
    mcp_paths = [
        os.path.join(target, ".mcp.json"),
        os.path.join(target, "mcp-servers"),
    ]
    if any(os.path.exists(p) for p in mcp_paths):
        info["assets"].append("mcp")

    # Commands
    commands_dir = os.path.join(target, "commands")
    if os.path.isdir(commands_dir):
        for root, _, files in os.walk(commands_dir):
            if any(f.endswith(".md") for f in files):
                info["assets"].append("command")
                break

    # Deduplicate assets
    info["assets"] = list(dict.fromkeys(info["assets"]))

    # Language detection — walk all files
    found_langs = set()
    for root, dirs, files in os.walk(target):
        # Skip .git
        dirs[:] = [d for d in dirs if d != ".git"]
        for fname in files:
            for lang, patterns in LANGUAGE_PATTERNS.items():
                if any(re.search(p, fname) for p in patterns):
                    found_langs.add(lang)
    info["languages"] = sorted(found_langs)

    return info


def print_detection(info, target):
    """Print a human-readable detection summary."""
    print(f"\n=== Detection: {os.path.abspath(target)} ===")
    if info["is_plugin"]:
        print(f"  Type       : Plugin")
        if info["plugin_name"]:
            print(f"  Name       : {info['plugin_name']}")
        if info["plugin_version"]:
            print(f"  Version    : {info['plugin_version']}")
        if info["plugin_description"]:
            print(f"  Description: {info['plugin_description']}")
        print(f"  Marketplace eligible: YES")
    else:
        print(f"  Type       : Standalone component(s)")
        print(f"  Marketplace eligible: NO (no .claude-plugin/plugin.json found)")
        print(f"  Note: Standalone components can't be listed in a plugin marketplace.")
        print(f"        Bundle into a plugin first (see /mp-dev:new-plugin), or publish")
        print(f"        as-is for direct GitHub use via --plugin-dir or git clone.")

    if info["assets"]:
        print(f"  Assets     : {', '.join(info['assets'])}")
    else:
        print(f"  Assets     : (none detected)")

    if info["languages"]:
        print(f"  Languages  : {', '.join(info['languages'])}")
    print()


# ---------------------------------------------------------------------------
# Topic building
# ---------------------------------------------------------------------------

def build_topics(info, is_marketplace_eligible):
    """
    Build GitHub topic list following taxonomy budget rules:
      1. agent-marketplace (if marketplace eligible)
      2. One tag per asset type
      3. Language tags (only when detected)
    Max 20 GitHub topics total (well within budget here).
    """
    topics = []

    if is_marketplace_eligible:
        topics.append("agent-marketplace")

    for asset in info["assets"]:
        tag = ASSET_TOPIC_MAP.get(asset)
        if tag and tag not in topics:
            topics.append(tag)

    for lang in info["languages"]:
        if lang not in topics:
            topics.append(lang)

    return topics


# ---------------------------------------------------------------------------
# Git operations
# ---------------------------------------------------------------------------

def ensure_git_repo(target):
    """Initialize git repo and make an initial commit if needed."""
    initialized = False

    if not is_git_repo(target):
        print("Initializing git repository...")
        run(f'git -C "{target}" init')
        initialized = True

    inject_gitignore(target)

    if not has_commits(target):
        print("Creating initial commit...")
        run(f'git -C "{target}" add -A')
        run(f'git -C "{target}" commit -m "Initial commit"')
        print("Initial commit created.")
    else:
        # Stage any new changes
        result = run(f'git -C "{target}" status --porcelain', capture=True, check=False)
        if result.stdout.strip():
            print("Staging changes...")
            run(f'git -C "{target}" add -A')

    return initialized


# ---------------------------------------------------------------------------
# GitHub operations
# ---------------------------------------------------------------------------

def repo_exists(org, repo_name):
    result = run(f'gh repo view "{org}/{repo_name}" --json name', check=False, capture=True)
    return result.returncode == 0


def create_or_update_repo(target, org, repo_name, visibility, description):
    full_name = f"{org}/{repo_name}"
    vis_flag = "--public" if visibility == "public" else "--private"
    desc_flag = f'--description "{description}"' if description else ""

    if repo_exists(org, repo_name):
        print(f"Repository {full_name} already exists — pushing update...")
        run(f'git -C "{target}" remote set-url origin "https://github.com/{full_name}.git" 2>/dev/null || git -C "{target}" remote add origin "https://github.com/{full_name}.git"')

        # Check for uncommitted changes and commit them
        result = run(f'git -C "{target}" status --porcelain', capture=True, check=False)
        if result.stdout.strip():
            run(f'git -C "{target}" commit -m "Update"')

        run(f'git -C "{target}" push -u origin HEAD')
    else:
        print(f"Creating new repository {full_name}...")
        desc_arg = f'--description "{description}"' if description else ""
        run(
            f'gh repo create "{full_name}" {vis_flag} {desc_arg} --source="{target}" --push'
        )

    return f"https://github.com/{full_name}"


def apply_topics(org, repo_name, topics):
    if not topics:
        return
    topic_flags = " ".join(f"--add-topic {t}" for t in topics)
    run(f'gh repo edit "{org}/{repo_name}" {topic_flags}')
    print(f"Topics applied: {', '.join(topics)}")


# ---------------------------------------------------------------------------
# Marketplace entry
# ---------------------------------------------------------------------------

def generate_marketplace_entry(org, repo_name, info):
    entry = {
        "name": repo_name,
        "source": {
            "source": "github",
            "repo": f"{org}/{repo_name}",
        },
        "description": info.get("plugin_description") or "",
    }
    if info.get("plugin_version"):
        entry["version"] = info["plugin_version"]
    if info["assets"]:
        entry["keywords"] = [ASSET_TOPIC_MAP[a] for a in info["assets"] if a in ASSET_TOPIC_MAP]
    return entry


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Publish a component or plugin to GitHub.")
    parser.add_argument("--target", default=".", help="Path to the directory to publish")
    parser.add_argument("--org", help="GitHub organization or username")
    parser.add_argument("--repo-name", help="Repository name on GitHub")
    parser.add_argument("--visibility", choices=["public", "private"], default="public")
    parser.add_argument("--marketplace-entry", action="store_true",
                        help="Generate and print a marketplace.json plugin entry")
    parser.add_argument("--detect-only", action="store_true",
                        help="Run detection only; do not publish")
    args = parser.parse_args()

    target = os.path.abspath(args.target)
    if not os.path.isdir(target):
        print(f"Error: '{target}' is not a valid directory.")
        sys.exit(1)

    # Detect
    info = detect_assets(target)
    print_detection(info, target)

    if args.detect_only:
        sys.exit(0)

    # Require org and repo-name for publish
    if not args.org:
        print("Error: --org is required for publishing.")
        sys.exit(1)
    if not args.repo_name:
        print("Error: --repo-name is required for publishing.")
        sys.exit(1)

    # Validate repo name (GitHub: alphanumeric, hyphens, underscores, dots)
    if not re.match(r'^[a-zA-Z0-9._-]+$', args.repo_name):
        print(f"Error: Repository name '{args.repo_name}' contains invalid characters.")
        sys.exit(1)

    check_gh()

    # Git setup
    ensure_git_repo(target)

    # GitHub
    description = info.get("plugin_description") or ""
    repo_url = create_or_update_repo(
        target, args.org, args.repo_name, args.visibility, description
    )

    # Topics
    topics = build_topics(info, info["is_plugin"])
    apply_topics(args.org, args.repo_name, topics)

    # Marketplace entry
    if args.marketplace_entry:
        if not info["is_plugin"]:
            print("\nNote: Marketplace entries are for plugins only. Skipping entry generation.")
            print("To make this component marketplace-eligible, bundle it into a plugin first.")
        else:
            entry = generate_marketplace_entry(args.org, args.repo_name, info)
            print("\n=== Marketplace Entry ===")
            print("Add this to your marketplace.json plugins array:\n")
            print(json.dumps(entry, indent=2))
            print()

    # Summary
    print("=== Publish Complete ===")
    print(f"  Repository : {repo_url}")
    print(f"  Visibility : {args.visibility}")
    if topics:
        print(f"  Topics     : {', '.join(topics)}")
    if info["assets"]:
        print(f"  Assets     : {', '.join(info['assets'])}")


if __name__ == "__main__":
    main()
