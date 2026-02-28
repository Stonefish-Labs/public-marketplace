---
name: marketplace-publish
description: Stage, commit, and push a marketplace repository to GitHub. Applies the claude-marketplace GitHub topic. Use when the user wants to "publish", "push", "ship", or "deploy" a marketplace to GitHub.
disable-model-invocation: true
argument-hint: [marketplace-dir]
---

# Publish Marketplace

Stage, commit, and push a marketplace repository to GitHub.

## Input

`$ARGUMENTS` is the path to the marketplace directory (default: current directory).

## Steps

### 1. Resolve and Validate

- Use `$ARGUMENTS` as the marketplace path, or default to current directory
- Confirm `.claude-plugin/marketplace.json` exists — this must be a marketplace directory, not a plugin directory
- If `plugin.json` exists but `marketplace.json` does not, stop and tell the user to use the `mp-dev` publish skill instead

### 2. Detect Git and Remote State

Run:
```bash
python3 scripts/publish_marketplace.py --target <marketplace-dir> --detect-only
```

The script reports:
- Whether a git repo is initialized
- The configured remote URL (if any)
- Number of uncommitted changes (staged, unstaged, untracked)
- Whether local branch is ahead of remote

If no git repo exists:
- Offer to initialize: "No git repository found. Initialize one now?"
- If yes: `git init && git add -A && git commit -m "chore: initialize marketplace"`
- If no: stop

If no remote is configured:
- Ask: "Which GitHub org or username should this be published under?"
- Ask: "Repository name?" (suggest the marketplace name from `marketplace.json`)
- Ask: "Public or private?" (default: public)
- The publish step will create the remote repo

### 3. Check for Changes

If no changes pending and remote is up to date:
- Report: "Nothing to publish. Marketplace is already up to date."
- Show the current GitHub URL
- Remind: "Users can refresh with `/plugin marketplace update`"
- Stop

### 4. Show Change Summary and Ask for Commit Message

Show what will be committed (output of `git status --short`).

Ask: "Commit message for these changes:"

Suggest a default based on what changed:
- Added entries → `"feat: add <plugin-name> to catalog"`
- Removed entries → `"chore: remove <plugin-name> from catalog"`
- Mixed → `"chore: update marketplace catalog"`

### 5. Execute Publish

Run:
```bash
python3 scripts/publish_marketplace.py \
  --target <marketplace-dir> \
  --message "<commit-message>" \
  [--org <org>] \
  [--repo-name <name>] \
  [--visibility public|private]
```

The script:
1. Ensures `.gitignore` exists (copies bundled template if not present)
2. `git add -A`
3. `git commit -m "<message>"`
4. If no remote: `gh repo create <org>/<name> --<visibility> --source=. --push`
5. If remote exists: `git push`
6. `gh repo edit --add-topic claude-marketplace` (idempotent — safe to run repeatedly)

### 6. Report Results

Output:
- Commit SHA
- GitHub repository URL
- User-facing install command:
  ```
  /plugin marketplace add <org>/<repo>
  ```
- Beta channel command (if `channels/beta/` exists):
  ```
  /plugin marketplace add <org>/<repo> --ref channels/beta
  ```

## Notes

- If `gh` is not installed or authenticated, the script exits with a clear error
- If `git push` fails (e.g., non-fast-forward), report the error and suggest `git pull` first
- The `claude-marketplace` topic is applied idempotently — safe to run even if already set
- Private repos require `GITHUB_TOKEN` in the environment for background Claude Code auto-updates
