---
name: validate-plugin
description: Validate a plugin directory for structural correctness, manifest compliance, and component validity. Use when checking if an Anthropic plugin is ready to publish or run locally.
disable-model-invocation: true
argument-hint: <plugin-dir>
---

# Validate Plugin

Run comprehensive validation on an Anthropic plugin directory using deterministic python validators.

## Input

`$ARGUMENTS` is the path to the plugin directory (the folder containing `.claude-plugin/plugin.json`). If not provided, ask the user.

## Steps

0. **Analyze Best Practices**: Read the reference documents in your local `references/` folder to understand classification taxonomy and layout patterns before starting validation.
1. Verify that the user has provided a path to a plugin directory.
2. Execute the top-level plugin validator script, passing the target directory:
   ```bash
   python3 scripts/validate_plugin.py <plugin-dir>
   ```
3. Report the output. The script automatically runs discrete validators (`validate_skill.py`, `validate_agent.py`, etc.) for all components referenced in the plugin's manifest.

