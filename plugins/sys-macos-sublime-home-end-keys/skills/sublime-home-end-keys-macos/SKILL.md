---
name: sublime-home-end-keys-macos
description: Fix Home and End behavior in Sublime Text on macOS so keys move to line boundaries instead of file boundaries. Use this when Home jumps to the top of the file, End jumps to the bottom, or Shift+Home/Shift+End selection feels wrong compared with other editors. This skill provides the exact user keybindings snippet and quick verification steps to confirm line-start/line-end navigation is working as expected.
---

# Sublime Home/End Keys (macOS)

On macOS, Sublime Text defaults `home`/`end` to file-level movement.
Add user bindings to switch to line-level movement.

## Add keybindings

Open `Preferences > Key Bindings - User` and add:

```json
[
  { "keys": ["home"], "command": "move_to", "args": {"to": "bol"} },
  { "keys": ["end"], "command": "move_to", "args": {"to": "eol"} },
  { "keys": ["shift+home"], "command": "move_to", "args": {"to": "bol", "extend": true} },
  { "keys": ["shift+end"], "command": "move_to", "args": {"to": "eol", "extend": true} }
]
```

## Verify

- `Home`: cursor moves to beginning of current line.
- `End`: cursor moves to end of current line.
- `Shift+Home`: selects from cursor to line start.
- `Shift+End`: selects from cursor to line end.

## Limitations

- This changes Sublime behavior only; terminal, shell, and other editors keep their own key mappings.
- Existing custom keymaps can override these bindings depending on rule order and scope.

## Common failures

- JSON parse error in key bindings: ensure the snippet is inside a valid array with commas.
- No behavior change: check for conflicting package or user key bindings for `home`/`end`.
