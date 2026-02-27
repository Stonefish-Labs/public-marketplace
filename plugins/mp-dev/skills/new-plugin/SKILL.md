---
name: new-plugin
description: Act as a Packager to take a list of independent components (skills, agents, hooks, MCP servers) and assemble them into a strictly-formatted Anthropic plugin bundle. Use this skill when the user asks to "package a plugin", "bundle these components", "create a plugin.json", or "deploy a plugin". It collects the target components and an output directory, then generates the `.claude-plugin/` structure and `plugin.json` manifest. Do not use this to create new components from scratch.
disable-model-invocation: true
argument-hint: <plugin-name>
---

# Package a New Plugin Bundle

Act as a "Packager" to take a list of independent, standalone components (Skills, Agents, Hooks, MCP Servers) and bundle them into an Anthropic plugin.

## Input

`$ARGUMENTS` is the name for the new plugin bundle (kebab-case). If not provided, ask the user.

## Steps

0. **Analyze Best Practices**: Read the reference documents in your local `references/` folder to understand complex plugin manifests, monorepo layout patterns, and the official schema before beginning.
1. **Evaluate Project Layout**: Before asking for parameters, evaluate the current repository structure and suggest the best layout pattern to the user:
   - **Monolithic Pattern**: Best for simple, single-purpose plugins. The plugin and its `.claude-plugin` directory are created directly in the root directory (`--output="."`).
   - **Modular/Bundle Pattern**: Best for complex projects creating a library of reusable components. The plugin is packaged into a dedicated deployments folder (e.g., `--output="deployments/<plugin-name>"`), keeping it separate from the standalone library components.
   Ask the user which pattern they prefer, or suggest one based on what's already in the workspace.
2. **Get Plugin Name**: Validate the name is kebab-case.
3. **Get Components**: Ask the user: "Which components do you want to include? (e.g., `../library/skills/format-code.md` or `./my-skill`)". Accept a comma-separated list of paths to the standalone components.
4. **Resolve MCP Server strategy** (only if the plugin includes or references MCP servers): Ask the user whether each MCP server should be bundled into the plugin or hosted separately on GitHub and referenced by URL. See `references/monorepo-dependency-pattern.md` for the tradeoffs. If hosted separately, ask for the GitHub URL and preferred pin (commit hash, tag, or branch) and generate the appropriate `.mcp.json` entry rather than copying the server files.
5. **Get Output Directory**: Derived from their layout choice in Step 1.
6. **Execute Packager Script**: Instruct the AI to use the new `scripts/bundle_plugin.py` script to perform the packaging, passing the plugin name, output directory, and the list of components.

Example execution:
```bash
python3 scripts/bundle_plugin.py --name <plugin-name> --output <output-dir> --components <path1> <path2> ...
```

## After Packaging

Remind the user:
1. The packaged plugin is available at the requested output directory.
2. The standalone components remain untouched in their original locations.
3. To test the plugin, use `claude --plugin-dir <output-dir>`.
4. Validate the packaged plugin with `/mp-dev:validate <output-dir>`.
