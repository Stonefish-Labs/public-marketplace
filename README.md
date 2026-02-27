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

## Beta Channel

```shell
/plugin marketplace add Stonefish-Labs/public-marketplace --ref channels/beta
```
