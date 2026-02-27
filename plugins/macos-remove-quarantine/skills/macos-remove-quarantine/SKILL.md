---
name: macos-remove-quarantine
description: Check, inspect, and remove macOS quarantine attributes from trusted files that fail to open. Use this when Gatekeeper shows messages like "cannot be opened" or "unidentified developer," when apps are copied from zip archives, or when a directory full of binaries/scripts is blocked after download. This skill covers both verification (`xattr`) and safe removal (single file or recursive directory), plus post-change validation so you can confirm the quarantine flag is actually gone.
---

# macOS Remove Quarantine

## When to use this skill

Use when:
- A downloaded file won't open due to Gatekeeper
- User sees "unverified developer" or "can't be opened" warnings
- User wants to check if a file is quarantined

## Check quarantine status first

```bash
xattr -l /path/to/file | grep quarantine
```

If there is no output, that file does not currently have the quarantine attribute.

## Remove quarantine

```bash
xattr -d com.apple.quarantine /path/to/file
```

For directories (recursive):

```bash
xattr -dr com.apple.quarantine /path/to/directory
```

## Verify removal

```bash
xattr -l /path/to/file | grep quarantine
```

Expected result after removal: no output.

## Notes

- Only works on macOS (`xattr` is built in).
- Remove quarantine only for files you trust; this bypasses one Gatekeeper protection layer.
- `sudo` is usually unnecessary for files you own.
- Quarantine key: `com.apple.quarantine`.

## Limitations

- This only removes the quarantine attribute; it does not fix code signing or notarization issues.
- Apps may still be blocked by policy controls (MDM, endpoint security, corporate Gatekeeper settings).

## Common failures

- `No such xattr`: file was never quarantined or path is incorrect.
- `Operation not permitted`: file ownership or system policy prevents modification.
