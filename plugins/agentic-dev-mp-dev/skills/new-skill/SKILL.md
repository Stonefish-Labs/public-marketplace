---
name: new-skill
description: Scaffold a new standalone skill component by collecting parameters and executing the scaffolding script. Use this skill when the user wants to "create a new skill", "build a standalone skill", or "scaffold a skill". It handles collecting all required properties (name, description, target directory) and optional metadata (license, compatibility, author) before generating the strictly-formatted folder structure containing SKILL.md and its progressive disclosure folders (scripts/, assets/, references/). Do not use this for agents or MCP servers.
disable-model-invocation: true
argument-hint: <skill-name>
---

# Create New Standalone Skill

Generate a new standalone skill component using the deterministic python script.

## Input

`$ARGUMENTS` is the name for the new skill (kebab-case). If not provided, ask the user.

## Steps

0. **Analyze Best Practices**: Read the reference documents in your local `references/` folder to review naming conventions and design best practices before prompting the user.
1. Ask the user for the following parameters if not provided:
   - `name`: Kebab-case name of the skill.
   - `description`: Description of the skill (NO XML tags allowed).
   - `target-dir`: "Where would you like to create this component? (e.g. library/skills, or .)"
   - `hide`: Whether to set user-invocable to false (boolean).
   - Progressive Disclosure: "Your skill will be created with a standard folder structure (`scripts/`, `assets/`, `references/`) to support progressive disclosure. Do you have any templates you'd like to include in `assets/` or documentation for `references/` right now?"
   - `license`: License for the skill (optional, e.g. MIT).
   - `compatibility`: Compatibility environments (optional).
   - `author`: Author of the skill (optional).
   - `version`: Version of the skill (optional, defaults to 1.0.0).
   - `mcp-server`: Associated MCP server (optional).
   - `category`: Category (optional).
   - `tags`: Comma-separated tags (optional).
   - `python-version`: Target Python version if the skill uses Python and requires UV for dependencies (optional, e.g. ">=3.11").
   - `dependencies`: Comma-separated list of Python dependencies if the skill needs them (optional, e.g. "requests, rich").

2. Execute the python scaffolding script:
   ```bash
   python scripts/scaffold_skill.py \
     --name "<name>" \
     --description "<description>" \
     --target-dir "<target-dir>" \
     [--hide] \
     [--license "<license>"] \
     [--compatibility "<compatibility>"] \
     [--author "<author>"] \
     [--version "<version>"] \
     [--mcp-server "<mcp-server>"] \
     [--category "<category>"] \
     [--tags "<tags>"] \
     [--python-version "<python-version>"] \
     [--dependencies "<dependencies>"] \
     [--link-to-plugin]
   ```

4. Report what was created based on the script's output. Ensure no `README.md` was created inside the skill folder as this is forbidden. Do not update `plugin.json` by default.
5. Clean up any unused subfolders (`scripts/`, `assets/`, `references/`) using `find <target-dir>/<name> -type d -empty -delete`.
