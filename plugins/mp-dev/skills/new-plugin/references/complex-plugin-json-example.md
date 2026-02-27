# Complex plugin.json Example

This reference document illustrates a fully-populated `plugin.json` manifest for a hypothetical `mp-bug-filing` plugin, demonstrating all supported metadata and component path fields.

```json
{
  "name": "mp-bug-filing",
  "version": "1.2.0",
  "description": "An advanced bug filing assistant that integrates with GUS, assesses severity, and categorizes vulnerabilities.",
  "author": {
    "name": "Stonefish Labs",
    "email": "hello@stonefishlabs.com",
    "url": "https://github.com/Stonefish-Labs"
  },
  "homepage": "https://github.com/Stonefish-Labs/mp-bug-filing",
  "repository": "https://github.com/Stonefish-Labs/mp-bug-filing.git",
  "license": "MIT",
  "keywords": ["bug", "filing", "gus", "severity", "vulnerability"],
  "skills": "./skills/",
  "agents": "./agents/",
  "commands": ["./commands/file-bug.md", "./commands/triage.md"],
  "hooks": "./config/hooks.json",
  "mcpServers": "./mcp-config.json",
  "strict": true
}
```

### Field Notes

- **`name`**: The only required field. Must be kebab-case. Used for namespacing all components (e.g., skills appear as `mp-bug-filing:skill-name`).
- **`author`**: Must be an object with at least a `name` key. `email` and `url` are optional.
- **`keywords`**: Used for discovery and searchability.
- **`skills` / `agents` / `commands`**: Custom paths supplement the default auto-discovered directories — they do not replace them. All paths must be relative and start with `./`.
- **`strict`**: When `true`, `plugin.json` is the authority for component definitions. Defaults to `true`.

### What plugin.json Does NOT Support

The following fields are **not** part of the official `plugin.json` schema and should not be used:

- `dependencies` — there is no inter-plugin dependency mechanism in `plugin.json`
- `category` — a marketplace-only field (belongs in `marketplace.json`, not `plugin.json`)
- `tags` — a marketplace-only field (belongs in `marketplace.json`, not `plugin.json`)

For the full schema reference, see the [official plugins reference](https://docs.anthropic.com/en/plugins-reference#plugin-manifest-schema).
