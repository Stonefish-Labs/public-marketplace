#!/usr/bin/env python3
"""Compare two files with various modes and normalization options."""

import argparse
import difflib
import sys
import unicodedata
import zlib
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


def normalize_text(text: str, args) -> str:
    if args.unicode_normalize:
        text = unicodedata.normalize('NFKC', text)
    
    if args.normalize_tabs:
        text = text.expandtabs()
    
    if args.ignore_newlines:
        text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    if args.ignore_case:
        text = text.lower()
    
    lines = text.splitlines(keepends=True)
    
    if args.ignore_whitespace:
        lines = [line.strip() + ('\n' if line.endswith(('\n', '\r\n', '\r')) else '') 
                for line in lines]
    
    if args.ignore_blank:
        lines = [line for line in lines if line.strip()]
    
    return ''.join(lines)


def format_size(size: int) -> str:
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.1f}MB"
    elif size >= 1024:
        return f"{size / 1024:.1f}KB"
    return f"{size} bytes"


def main():
    parser = argparse.ArgumentParser(description='Compare two files')
    parser.add_argument('left', help='Path to first file')
    parser.add_argument('right', help='Path to second file')
    parser.add_argument('--mode', choices=['exact', 'smart', 'binary'], default='exact',
                       help='Comparison mode: exact (CRC32), smart (text with normalization), binary (CRC32)')
    parser.add_argument('--ignore-blank', action='store_true', help='Ignore blank lines')
    parser.add_argument('--ignore-newlines', action='store_true', help='Ignore line ending differences')
    parser.add_argument('--ignore-whitespace', action='store_true', help='Ignore leading/trailing whitespace')
    parser.add_argument('--ignore-case', action='store_true', help='Case-insensitive comparison')
    parser.add_argument('--normalize-tabs', action='store_true', help='Convert tabs to spaces')
    parser.add_argument('--unicode-normalize', action='store_true', help='Apply Unicode NFKC normalization')
    args = parser.parse_args()
    
    left = Path(args.left)
    right = Path(args.right)
    
    if not left.exists():
        print(f"ERROR: Left file does not exist: {args.left}", file=sys.stderr)
        sys.exit(1)
    if not right.exists():
        print(f"ERROR: Right file does not exist: {args.right}", file=sys.stderr)
        sys.exit(1)
    
    if not left.is_file():
        print(f"ERROR: Left path is not a file: {args.left}", file=sys.stderr)
        sys.exit(1)
    if not right.is_file():
        print(f"ERROR: Right path is not a file: {args.right}", file=sys.stderr)
        sys.exit(1)
    
    try:
        left_stat = left.stat()
        right_stat = right.stat()
        left_is_text = is_text_file(left)
        right_is_text = is_text_file(right)
        
        if args.mode == 'binary' or (not left_is_text or not right_is_text):
            left_crc = calculate_crc32(left)
            right_crc = calculate_crc32(right)
            
            if left_crc == right_crc:
                print("IDENTICAL (binary)")
                print(f"left: {left.name} ({left_crc})")
                print(f"right: {right.name} ({right_crc})")
            else:
                print("DIFFERENT (binary)")
                print(f"left: {left.name} ({format_size(left_stat.st_size)}, {left_crc})")
                print(f"right: {right.name} ({format_size(right_stat.st_size)}, {right_crc})")
        
        elif args.mode == 'exact':
            left_crc = calculate_crc32(left)
            right_crc = calculate_crc32(right)
            
            if left_crc == right_crc:
                print("IDENTICAL")
                print(f"left: {left.name} ({left_crc})")
                print(f"right: {right.name} ({right_crc})")
            else:
                print("DIFFERENT")
                print(f"left: {left.name} ({format_size(left_stat.st_size)}, {left_crc})")
                print(f"right: {right.name} ({format_size(right_stat.st_size)}, {right_crc})")
        
        elif args.mode == 'smart':
            if not left_is_text or not right_is_text:
                print("ERROR: Smart mode requires both files to be text", file=sys.stderr)
                sys.exit(1)
            
            with open(left, 'r', encoding='utf-8', errors='replace') as f:
                left_content = f.read()
            with open(right, 'r', encoding='utf-8', errors='replace') as f:
                right_content = f.read()
            
            left_normalized = normalize_text(left_content, args)
            right_normalized = normalize_text(right_content, args)
            
            if left_normalized == right_normalized:
                normalizations = []
                if args.ignore_case: normalizations.append("case")
                if args.ignore_whitespace: normalizations.append("whitespace")
                if args.ignore_blank: normalizations.append("blank-lines")
                if args.ignore_newlines: normalizations.append("line-endings")
                if args.normalize_tabs: normalizations.append("tabs")
                if args.unicode_normalize: normalizations.append("unicode")
                
                norm_text = f" (normalized: {', '.join(normalizations)})" if normalizations else ""
                
                print(f"IDENTICAL{norm_text}")
                print(f"left: {left.name} ({format_size(left_stat.st_size)})")
                print(f"right: {right.name} ({format_size(right_stat.st_size)})")
            else:
                print("DIFFERENT")
                print(f"left: {left.name} ({format_size(left_stat.st_size)})")
                print(f"right: {right.name} ({format_size(right_stat.st_size)})")
                print("")
                print("diff:")
                
                left_lines = left_normalized.splitlines(keepends=True)
                right_lines = right_normalized.splitlines(keepends=True)
                
                diff_lines = list(difflib.unified_diff(
                    left_lines,
                    right_lines,
                    fromfile=str(left),
                    tofile=str(right),
                    lineterm=''
                ))
                
                for line in diff_lines:
                    print(line)
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
