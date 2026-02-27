# public-marketplace

Public Marketplace for Stonefish Labs plugins.

## Add This Marketplace

```shell
/plugin marketplace add Stonefish-Labs/public-marketplace
```

## Install Plugins

```shell
/plugin install <plugin-name>@public-marketplace
```

## Available Plugins

| Plugin | Description | Category |
|---|---|---|
| `mp-dev` | Plugin development tools: scaffold skills, agents, hooks, MCP servers, commands, and plugins | developer-tools |
| `mp-admin` | Marketplace management skills: init, add, remove, sync, publish, and version bump | developer-tools |
| `mp-fastmcp-dev` | FastMCP development toolkit with server creation, upgrades, safety, and testing skills | developer-tools |
| `project-management` | Project management skills | productivity |
| `local-llm-prompt-evaluator` | Evaluate prompts and agent workflows for local LLM quality with scored findings and rewrite guidance | developer-tools |
| `dev-snippets-linux-bash` | Linux and Bash snippet workflows for resilient downloads and ELF dependency packaging | developer-tools |
| `dev-snippets-python-utilities` | Python utility snippets for keyring secrets, HTML conversion, and sync/async interoperability | developer-tools |
| `dev-snippets-lowlevel-security` | Defensive low-level forensics snippets with deny-by-default safety and review agents | security |
| `sandals-mcp` | Sandals and Beaches MCP server for resort discovery, availability checks, and optional price watch alerts | automation |

## Beta Channel

```shell
/plugin marketplace add Stonefish-Labs/public-marketplace --ref channels/beta
```
