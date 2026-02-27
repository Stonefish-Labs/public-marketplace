---
name: publish
description: Publish a local plugin, plugin bundle, or standalone component directory to a GitHub repository. Handles git initialization, topic tagging, and marketplace entry generation. Use when the user wants to "publish", "push to GitHub", "release", or "upload" a plugin, skill, agent, hook, MCP server, or command to a remote repository.
disable-model-invocation: true
argument-hint: <target-directory>
---

# Publish to GitHub

Publish a local component or plugin directory to GitHub with proper topic tagging, git initialization if needed, and optional marketplace entry generation.

## Input

`$ARGUMENTS` is the path to the directory to publish. If not provided, use the current directory.

## Steps

0. **Read References**: Read `references/classification-taxonomy.md` to understand how assets are detected and classified before prompting the user.

1. **Resolve Target**: Confirm `$ARGUMENTS` is a valid directory. If not provided, use `.` (current directory). Resolve to an absolute path.

2. **Detect Asset Types**: Run the detection phase of the publish script to understand what's in the directory:
   ```bash
   python3 scripts/publish_repo.py --target <target-dir> --detect-only
   ```
   Report what was found (plugin, standalone skills, agents, hooks, MCP servers, commands, detected languages).

3. **Marketplace Eligibility Notice**: Based on detection output:
   - If a `.claude-plugin/plugin.json` is present → the component is **marketplace-eligible**. Inform the user.
   - If only standalone components are present → inform the user: "Standalone skills/agents/hooks/MCPs/commands cannot be listed in a plugin marketplace directly. They need to be bundled into a plugin first (see `/mp-dev:new-plugin`). The repository will still be published to GitHub for direct use."

4. **Collect Parameters**: Ask the user for the following if not already provided via arguments:

   - **GitHub organization or username**: "Which GitHub org or username should this be published under?" (no default — always ask)
   - **Repository name**: Suggest the plugin name (from `plugin.json`) or the directory name. Confirm with user.
   - **Visibility**: "Should this repository be public or private?" (default: public)
   - **Marketplace entry** (only if marketplace-eligible): "Would you like me to generate a marketplace.json entry for this plugin?" (yes/no)

5. **Execute Publish Script**:
   ```bash
   python3 scripts/publish_repo.py \
     --target <target-dir> \
     --org <org-or-username> \
     --repo-name <repo-name> \
     --visibility public|private \
     [--marketplace-entry]
   ```

6. **Report Results**: Display the script's output including:
   - GitHub repository URL
   - Topics applied
   - Whether git was initialized
   - Marketplace entry JSON (if requested) — present it as a copyable block

## Notes

- The script will `git init` and make an initial commit automatically if the directory is not already a git repo
- A `.gitignore` is added automatically if one does not exist (using the bundled template)
- Never run `--marketplace-entry` without the user explicitly requesting it
- If `gh` is not installed or not authenticated, the script will report a clear error and stop
