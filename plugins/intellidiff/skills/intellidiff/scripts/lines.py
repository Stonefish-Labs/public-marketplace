#!/usr/bin/env python3
"""Read specific line ranges from a text file."""

import argparse
import sys
from pathlib import Path


def is_text_file(file_path: Path, chunk_size: int = 1024) -> bool:
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(chunk_size)
            return b'\0' not in chunk
    except (OSError, IOError):
        return False


def main():
    parser = argparse.ArgumentParser(description='Read specific line ranges from a text file')
    parser.add_argument('file', help='Path to the text file')
    parser.add_argument('--start', type=int, default=1, help='Starting line number (1-based, default: 1)')
    parser.add_argument('--end', type=int, default=None, help='Ending line number (default: end of file)')
    parser.add_argument('--context', type=int, default=0, help='Additional context lines before/after range (default: 0)')
    args = parser.parse_args()
    
    path = Path(args.file)
    
    if not path.exists():
        print(f"ERROR: File does not exist: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    if not path.is_file():
        print(f"ERROR: Not a file: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    if not is_text_file(path):
        print(f"ERROR: Not a text file: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.read().splitlines()
        
        total_lines = len(lines)
        
        start = max(1, args.start)
        end = total_lines if args.end is None else min(args.end, total_lines)
        
        actual_start = max(1, start - args.context)
        actual_end = min(total_lines, end + args.context)
        
        for i in range(actual_start - 1, actual_end):
            line_num = i + 1
            prefix = ">>> " if start <= line_num <= end else "    "
            print(f"{prefix}{line_num:4d}| {lines[i]}")
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
