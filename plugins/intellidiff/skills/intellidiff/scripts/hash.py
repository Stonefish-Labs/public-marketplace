#!/usr/bin/env python3
"""Get CRC32 hash and metadata for a file."""

import argparse
import sys
import zlib
from datetime import datetime
from pathlib import Path


def is_text_file(file_path: Path, chunk_size: int = 1024) -> bool:
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(chunk_size)
            return b'\0' not in chunk
    except (OSError, IOError):
        return False


def calculate_crc32(file_path: Path, chunk_size: int = 65536) -> str:
    crc = 0
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            crc = zlib.crc32(chunk, crc)
    return f"{crc & 0xffffffff:08x}"


def format_size(size: int) -> str:
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.1f}MB"
    elif size >= 1024:
        return f"{size / 1024:.1f}KB"
    return f"{size} bytes"


def main():
    parser = argparse.ArgumentParser(description='Get CRC32 hash and metadata for a file')
    parser.add_argument('file', help='Path to the file')
    args = parser.parse_args()
    
    path = Path(args.file)
    
    if not path.exists():
        print(f"ERROR: File does not exist: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    if not path.is_file():
        print(f"ERROR: Not a file: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        stat = path.stat()
        is_text = is_text_file(path)
        crc32 = calculate_crc32(path)
        
        modified = datetime.fromtimestamp(stat.st_mtime)
        created = datetime.fromtimestamp(stat.st_ctime)
        
        print(path.name)
        print(f"crc32: {crc32}")
        print(f"size: {format_size(stat.st_size)}")
        print(f"type: {'text' if is_text else 'binary'}")
        print(f"modified: {modified.strftime('%Y-%m-%d %H:%M:%S')} ({modified.strftime('%A')})")
        print(f"created: {created.strftime('%Y-%m-%d %H:%M:%S')} ({created.strftime('%A')})")
        print(f"path: {path.resolve()}")
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
