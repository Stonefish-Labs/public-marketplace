---
name: macos-wine-setup
description: Install Wine on macOS for running Windows executables and preparing compatibility dependencies with Winetricks. Use this when testing Windows-only tools on a Mac, reproducing user issues involving `.exe` apps, or setting up a local compatibility environment without a Windows VM. This skill includes required graphics support (`xquartz`), Wine installation via Homebrew, optional channel choices, and quick validation commands to confirm the runtime is working.
---

# macOS Wine Setup

Install XQuartz, Wine, and Winetricks for running Windows applications on macOS.

## Install dependencies

```bash
brew install --cask xquartz
brew install wine-stable
brew install winetricks
```

You can substitute `wine-devel` or `wine-staging` if you specifically need those builds.

## Verify installation

```bash
wine --version
winetricks --version
```

## First-run notes

- Launching Wine apps may create an initial Wine prefix on first use.
- Some apps require extra components via Winetricks (for example .NET, VC runtimes).
- XQuartz may require logout/login or restart before GUI apps render correctly.

## Limitations

- Wine is a compatibility layer, not a full Windows VM; some apps will not run correctly.
- Performance and rendering behavior vary by app, Wine channel, and macOS graphics stack.

## Common failures

- GUI app does not open: verify XQuartz installation and restart session.
- Missing DLL/runtime errors: install required components with Winetricks.
