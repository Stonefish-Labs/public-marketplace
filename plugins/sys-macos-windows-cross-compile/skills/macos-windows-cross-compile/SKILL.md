---
name: macos-windows-cross-compile
description: Set up a macOS machine to cross-compile Windows binaries using MinGW-w64 via Homebrew. Use this when you need `.exe` output from C/C++ code on macOS, CI runners need a Windows target without a Windows host, or you need a quick local cross-compile toolchain for testing. This skill covers Homebrew setup checks, MinGW installation, PATH initialization, and basic verification that the Windows-target compiler is available.
---

# macOS Windows Cross-Compile Setup

Install MinGW-w64 and verify Windows-target compilers are available.

## Install prerequisites

```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Ensure brew is in current shell
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Persist shell setup by adding the `brew shellenv` line to `~/.zshrc` (or your shell profile).

## Install MinGW-w64

```bash
brew install mingw-w64
```

## Verify toolchain

```bash
which x86_64-w64-mingw32-gcc
x86_64-w64-mingw32-gcc --version
```

If both commands succeed, cross-compiling to Windows is ready.

## Limitations

- This sets up C/C++ cross-compilers only; it does not package installers or Windows runtime dependencies.
- Tool names/paths can vary between Intel and Apple Silicon Homebrew installations.

## Common failures

- `command not found` for `x86_64-w64-mingw32-gcc`: shell profile does not load Homebrew PATH.
- Link errors at build time: required Windows libraries or target architecture flags are missing.
