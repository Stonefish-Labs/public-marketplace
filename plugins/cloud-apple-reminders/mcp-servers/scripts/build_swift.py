#!/usr/bin/env python3
"""Build script for EventKitCLI Swift binary."""

import os
import subprocess
import sys
from pathlib import Path


def main():
    print("Building Swift binary for Apple Reminders MCP Server...")

    if sys.platform != "darwin":
        print("Error: This project requires macOS to compile Swift binaries.")
        sys.exit(1)

    try:
        subprocess.run(["which", "swiftc"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Error: Swift compiler (swiftc) not found.")
        print("Please install Xcode or Xcode Command Line Tools: xcode-select --install")
        sys.exit(1)

    project_root = Path(__file__).parent.parent
    swift_dir = project_root / "swift"
    source_file = swift_dir / "EventKitCLI.swift"
    info_plist_file = swift_dir / "Info.plist"
    bin_dir = project_root / "src" / "apple_reminders" / "bin"
    output_file = bin_dir / "EventKitCLI"

    if not source_file.exists():
        print(f"Error: Source file not found: {source_file}")
        sys.exit(1)

    if not info_plist_file.exists():
        print(f"Error: Info.plist not found: {info_plist_file}")
        print("Info.plist is required for EventKit permissions to work properly.")
        sys.exit(1)

    bin_dir.mkdir(parents=True, exist_ok=True)

    compile_command = [
        "swiftc",
        "-o", str(output_file),
        str(source_file),
        "-framework", "EventKit",
        "-framework", "Foundation",
        "-Xlinker", "-sectcreate",
        "-Xlinker", "__TEXT",
        "-Xlinker", "__info_plist",
        "-Xlinker", str(info_plist_file),
    ]

    print(f"Compiling {source_file}...")

    try:
        result = subprocess.run(compile_command, capture_output=True, text=True)
        if result.stderr:
            print(f"Swift compiler warnings:\n{result.stderr}")
        if result.stdout:
            print(result.stdout)

        print(f"Compilation successful! Binary saved to {output_file}")

        output_file.chmod(0o755)
        print("Binary is now executable.")
        print("Swift binary build complete!")
    except subprocess.CalledProcessError as e:
        print("Compilation failed!")
        print(e.stderr if e.stderr else str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
