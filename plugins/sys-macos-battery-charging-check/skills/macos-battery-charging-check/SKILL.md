---
name: macos-battery-charging-check
description: Check whether a Mac laptop is charging, identify reported adapter wattage, and inspect live power events from Terminal. Use this when charging seems slow, when validating a new charger/cable/dock, when confirming expected wattage (for example 67W, 96W, or 140W), or when troubleshooting intermittent charging behavior. This skill provides quick read-only commands and interpretation notes so you can tell whether external power is detected and whether charging is active.
---

# macOS Battery Charging Check

Use these commands to confirm adapter wattage and active charging state.

## 1) Check detected adapter wattage

```bash
system_profiler SPPowerDataType | grep "Wattage"
```

This reports the wattage currently detected by macOS for the connected power source.

## 2) Check live charging state transitions

```bash
pmset -g rawlog | awk -F ";" '/AC/ {print $2, $3, $7}'
```

Look for lines indicating external power (`AC`) and whether charging is active.

## Notes

- These commands are read-only and safe to run repeatedly.
- If wattage looks low, verify cable type, charger rating, and dock limitations.
- For Apple Silicon laptops, charging behavior may taper near full battery by design.

## Limitations

- Reported wattage is what macOS sees from the power source, not guaranteed sustained battery charge input.
- `pmset -g rawlog` output is noisy and can require sampling over time for reliable conclusions.

## Common failures

- No `Wattage` line: adapter may be disconnected, unsupported, or reporting through a limited dock.
- `AC` present but not charging: battery may be at optimization threshold or near full.
