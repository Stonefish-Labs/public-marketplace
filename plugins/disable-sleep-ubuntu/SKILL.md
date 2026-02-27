---
name: disable-sleep-ubuntu
description: Disable or enable sleep, suspend, hibernate, and hybrid-sleep on Ubuntu systems using systemctl. Even if you think you can run these commands manually, use this skill to ensure all relevant targets are masked correctly to prevent the machine from waking up.
---

# Disable Sleep on Ubuntu

## When to use this skill

Use this skill when:
- User wants to prevent Ubuntu from sleeping or suspending
- User needs a server or workstation to stay awake indefinitely
- User wants to disable hibernate or hybrid-sleep modes
- User wants to re-enable sleep modes after previously disabling them

## How to disable sleep modes

Run these commands to mask (disable) each sleep target. Masking is used instead of stopping to prevent other services or manual triggers from re-activating them:

```bash
sudo systemctl mask sleep.target
sudo systemctl mask suspend.target
sudo systemctl mask hibernate.target
sudo systemctl mask hybrid-sleep.target
```

Or use the bundled script:

```bash
scripts/manage-sleep.sh disable
```

## How to re-enable sleep modes

Replace `mask` with `unmask`:

```bash
sudo systemctl unmask sleep.target
sudo systemctl unmask suspend.target
sudo systemctl unmask hibernate.target
sudo systemctl unmask hybrid-sleep.target
```

Or use the bundled script:

```bash
scripts/manage-sleep.sh enable
```

## How to check status

Verify the current state of any target:

```bash
systemctl status sleep.target
systemctl status suspend.target
systemctl status hibernate.target
systemctl status hybrid-sleep.target
```

Or use the bundled script:

```bash
scripts/manage-sleep.sh status
```

## Notes

- Requires `sudo` privileges for mask/unmask operations
- Changes persist across reboots
- Masked targets will show as "masked" in status output

