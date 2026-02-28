#!/usr/bin/env python3
"""
publish_marketplace.py - Stage, commit, and push a marketplace repository to GitHub.

Usage:
    python3 publish_marketplace.py --target <dir> --detect-only
    python3 publish_marketplace.py --target <dir> --message "<msg>" [--org <org>] [--repo-name <name>] [--visibility public|private]

Output: JSON to stdout with status information.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


GITIGNORE_TEMPLATE = Path(__file__).parent.parent / "assets" / "gitignore-template.txt"


def run(cmd, cwd=None, capture=True):
    """Run a shell command. Returns (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd, shell=True, capture_output=capture, text=True, cwd=cwd
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def gh_available():
    code, _, _ = run("gh --version")
    return code == 0


def detect_state(target: Path):
    """Detect the git and remote state of the marketplace directory."""
    state = {
        "has_git": False,
        "has_remote": False,
        "remote_url": None,
        "staged": 0,
        "unstaged": 0,
        "untracked": 0,
        "ahead": 0,
        "errors": []
    }

    # Check git repo
    code, _, _ = run("git rev-parse --git-dir", cwd=target)
    if code != 0:
        return state
    state["has_git"] = True

    # Check remote
    code, remote_url, _ = run("git remote get-url origin 2>/dev/null", cwd=target)
    if code == 0 and remote_url:
        state["has_remote"] = True
        state["remote_url"] = remote_url

    # Count changes
    code, status_out, _ = run("git status --porcelain", cwd=target)
    if code == 0:
        for line in status_out.splitlines():
            if not line.strip():
                continue
            xy = line[:2]
            if xy[0] != " " and xy[0] != "?":
                state["staged"] += 1
            if xy[1] not in (" ", "?"):
                state["unstaged"] += 1
            if xy == "??":
                state["untracked"] += 1

    # Check ahead of remote
    if state["has_remote"]:
        code, ahead_str, _ = run(
            "git rev-list --count @{u}..HEAD 2>/dev/null", cwd=target
        )
        if code == 0 and ahead_str.isdigit():
            state["ahead"] = int(ahead_str)

    return state


def ensure_gitignore(target: Path):
    """Add .gitignore if not present."""
    gitignore_path = target / ".gitignore"
    if not gitignore_path.exists() and GITIGNORE_TEMPLATE.exists():
        shutil.copy(GITIGNORE_TEMPLATE, gitignore_path)
        return True
    return False


def get_remote_github_repo(target: Path):
    """Extract owner/repo from the git remote URL."""
    code, remote_url, _ = run("git remote get-url origin", cwd=target)
    if code != 0:
        return None
    # Parse github.com URLs: https://github.com/owner/repo or git@github.com:owner/repo
    url = remote_url.rstrip(".git")
    if "github.com/" in url:
        parts = url.split("github.com/")[-1].split("/")
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
    if "github.com:" in url:
        parts = url.split("github.com:")[-1].split("/")
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
    return None


def main():
    parser = argparse.ArgumentParser(description="Publish a marketplace repository to GitHub.")
    parser.add_argument("--target", required=True, help="Path to marketplace directory")
    parser.add_argument("--detect-only", action="store_true", help="Only detect state, do not publish")
    parser.add_argument("--message", help="Commit message")
    parser.add_argument("--org", help="GitHub org or username (for new repos)")
    parser.add_argument("--repo-name", help="GitHub repository name (for new repos)")
    parser.add_argument("--visibility", choices=["public", "private"], default="public",
                        help="Repository visibility (for new repos)")
    args = parser.parse_args()

    target = Path(args.target).resolve()

    # Validate marketplace
    marketplace_json = target / ".claude-plugin" / "marketplace.json"
    if not marketplace_json.exists():
        print(json.dumps({"error": f"marketplace.json not found at {marketplace_json}"}))
        sys.exit(1)

    try:
        with open(marketplace_json) as f:
            catalog = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(json.dumps({"error": f"Cannot parse marketplace.json: {e}"}))
        sys.exit(1)

    marketplace_name = catalog.get("name", target.name)

    if not gh_available():
        print(json.dumps({
            "error": "gh CLI is not installed or not in PATH.",
            "install": "https://cli.github.com"
        }))
        sys.exit(1)

    # Check gh auth
    code, _, _ = run("gh auth status 2>/dev/null")
    if code != 0:
        print(json.dumps({
            "error": "gh CLI is not authenticated. Run 'gh auth login' first."
        }))
        sys.exit(1)

    state = detect_state(target)

    if args.detect_only:
        total_changes = state["staged"] + state["unstaged"] + state["untracked"]
        print(json.dumps({
            "marketplace": marketplace_name,
            "has_git": state["has_git"],
            "has_remote": state["has_remote"],
            "remote_url": state["remote_url"],
            "staged": state["staged"],
            "unstaged": state["unstaged"],
            "untracked": state["untracked"],
            "ahead": state["ahead"],
            "total_pending_changes": total_changes
        }, indent=2))
        return

    # Publish flow
    if not args.message:
        print(json.dumps({"error": "Commit message required for publish (--message)"}))
        sys.exit(1)

    output = {"marketplace": marketplace_name, "steps": []}

    # Initialize git if needed
    if not state["has_git"]:
        code, _, err = run("git init", cwd=target)
        if code != 0:
            print(json.dumps({"error": f"git init failed: {err}"}))
            sys.exit(1)
        output["steps"].append("Initialized git repository")

    # Ensure .gitignore
    added_gitignore = ensure_gitignore(target)
    if added_gitignore:
        output["steps"].append("Added .gitignore from template")

    # Stage all
    code, _, err = run("git add -A", cwd=target)
    if code != 0:
        print(json.dumps({"error": f"git add failed: {err}"}))
        sys.exit(1)

    # Commit
    safe_msg = args.message.replace("'", "'\\''")
    code, _, err = run(f"git commit -m '{safe_msg}'", cwd=target)
    if code != 0:
        if "nothing to commit" in err or "nothing to commit" in _:
            output["steps"].append("Nothing to commit — skipped commit")
        else:
            print(json.dumps({"error": f"git commit failed: {err}"}))
            sys.exit(1)
    else:
        code2, sha, _ = run("git rev-parse --short HEAD", cwd=target)
        output["commit_sha"] = sha if code2 == 0 else "unknown"
        output["steps"].append(f"Committed changes: {output['commit_sha']}")

    # Push or create remote repo
    if not state["has_remote"]:
        # Create new GitHub repo
        if not args.org or not args.repo_name:
            print(json.dumps({
                "error": "No remote configured. Provide --org and --repo-name to create a new GitHub repo."
            }))
            sys.exit(1)

        visibility_flag = f"--{args.visibility}"
        cmd = (
            f"gh repo create {args.org}/{args.repo_name} "
            f"{visibility_flag} --source=. --push "
            f"--description '{marketplace_name} marketplace'"
        )
        code, out, err = run(cmd, cwd=target)
        if code != 0:
            print(json.dumps({"error": f"gh repo create failed: {err}"}))
            sys.exit(1)
        output["steps"].append(f"Created GitHub repo: {args.org}/{args.repo_name}")
        github_repo = f"{args.org}/{args.repo_name}"
    else:
        # Push to existing remote
        code, out, err = run("git push", cwd=target)
        if code != 0:
            print(json.dumps({
                "error": f"git push failed: {err}",
                "hint": "Try running 'git pull' first to sync with remote changes."
            }))
            sys.exit(1)
        output["steps"].append("Pushed to remote")
        github_repo = get_remote_github_repo(target)

    # Apply claude-marketplace topic
    if github_repo:
        code, _, _ = run(f"gh repo edit {github_repo} --add-topic claude-marketplace 2>/dev/null")
        output["steps"].append("Applied 'claude-marketplace' topic")
        output["github_url"] = f"https://github.com/{github_repo}"
        output["install_command"] = f"/plugin marketplace add {github_repo}"

        # Check for beta channel
        beta_path = target / "channels" / "beta" / ".claude-plugin" / "marketplace.json"
        if beta_path.exists():
            output["beta_install_command"] = f"/plugin marketplace add {github_repo} --ref channels/beta"

    output["status"] = "success"
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
