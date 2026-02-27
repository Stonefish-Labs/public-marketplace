#!/usr/bin/env python3
import os
import sys

VALID_COMMAND_DIR_NAMES = {"commands", "slash-commands", "slash_commands"}


def validate_command(file_path):
    if not os.path.exists(file_path):
        return False, f"Command file not found: {file_path}"

    if not file_path.endswith(".md"):
        return False, f"Command file must be a Markdown (.md) file: {file_path}"

    parent_name = os.path.basename(os.path.dirname(file_path))
    if parent_name.lower() not in VALID_COMMAND_DIR_NAMES:
        return False, (
            f"Command file must be inside a 'commands/', 'slash-commands/', or "
            f"'slash_commands/' directory (got '{parent_name}/'): {file_path}"
        )

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                return False, f"Command file is empty: {file_path}"
    except Exception as e:
        return False, f"Error reading command file: {e}"

    return True, f"Command valid: {file_path}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_command.py <path_to_command.md>")
        sys.exit(1)

    success, message = validate_command(sys.argv[1])
    print(message)
    sys.exit(0 if success else 1)
