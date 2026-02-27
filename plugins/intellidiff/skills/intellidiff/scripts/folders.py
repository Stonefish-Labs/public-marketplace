#!/usr/bin/env python3
"""Compare folders and find duplicate files."""

import argparse
import sys
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


def format_size(size: int) -> str:
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.1f}MB"
    elif size >= 1024:
        return f"{size / 1024:.1f}KB"
    return f"{size} bytes"


def scan_directory(root_path: Path, max_depth: int, include_binary: bool, current_depth: int = 0) -> dict:
    files = {}
    dirs = {}
    
    if current_depth >= max_depth:
        return {"files": files, "dirs": dirs}
    
    try:
        for item in root_path.iterdir():
            if item.name.startswith('.'):
                continue
            
            relative_path = item.relative_to(root_path)
            
            if item.is_file():
                try:
                    is_text = is_text_file(item)
                    if include_binary or is_text:
                        crc32 = calculate_crc32(item)
                        stat = item.stat()
                        files[str(relative_path)] = {
                            "size": stat.st_size,
                            "is_text": is_text,
                            "crc32": crc32
                        }
                except (OSError, ValueError):
                    continue
            
            elif item.is_dir() and not item.is_symlink():
                subdir_result = scan_directory(item, max_depth, include_binary, current_depth + 1)
                dirs[str(relative_path)] = subdir_result
    
    except (OSError, PermissionError):
        pass
    
    return {"files": files, "dirs": dirs}


def compare_structures(left_struct, right_struct, path_prefix: str = "") -> dict:
    results = {
        "identical_files": [],
        "different_files": [],
        "left_only": [],
        "right_only": [],
        "total_files": 0,
        "total_dirs": 0
    }
    
    left_files = left_struct.get("files", {})
    right_files = right_struct.get("files", {})
    
    all_files = set(left_files.keys()) | set(right_files.keys())
    
    for filename in all_files:
        full_path = f"{path_prefix}/{filename}" if path_prefix else filename
        results["total_files"] += 1
        
        if filename in left_files and filename in right_files:
            left_info = left_files[filename]
            right_info = right_files[filename]
            
            if left_info.get("crc32") and right_info.get("crc32"):
                if left_info["crc32"] == right_info["crc32"]:
                    results["identical_files"].append({
                        "path": full_path,
                        "size": left_info["size"],
                        "crc32": left_info["crc32"]
                    })
                else:
                    results["different_files"].append({
                        "path": full_path,
                        "left_size": left_info["size"],
                        "right_size": right_info["size"],
                        "left_crc32": left_info["crc32"],
                        "right_crc32": right_info["crc32"]
                    })
        
        elif filename in left_files:
            results["left_only"].append({
                "path": full_path,
                "size": left_files[filename]["size"]
            })
        
        else:
            results["right_only"].append({
                "path": full_path,
                "size": right_files[filename]["size"]
            })
    
    left_dirs = left_struct.get("dirs", {})
    right_dirs = right_struct.get("dirs", {})
    
    all_dirs = set(left_dirs.keys()) | set(right_dirs.keys())
    
    for dirname in all_dirs:
        full_path = f"{path_prefix}/{dirname}" if path_prefix else dirname
        results["total_dirs"] += 1
        
        if dirname in left_dirs and dirname in right_dirs:
            subdir_results = compare_structures(
                left_dirs[dirname],
                right_dirs[dirname],
                full_path
            )
            
            for key in ["identical_files", "different_files", "left_only", "right_only"]:
                results[key].extend(subdir_results[key])
            results["total_files"] += subdir_results["total_files"]
            results["total_dirs"] += subdir_results["total_dirs"]
        
        elif dirname in left_dirs:
            results["left_only"].append({
                "path": full_path,
                "type": "directory"
            })
        
        else:
            results["right_only"].append({
                "path": full_path,
                "type": "directory"
            })
    
    return results


def cmd_compare(args):
    left = Path(args.left)
    right = Path(args.right)
    
    if not left.exists():
        print(f"ERROR: Left folder does not exist: {args.left}", file=sys.stderr)
        sys.exit(1)
    if not right.exists():
        print(f"ERROR: Right folder does not exist: {args.right}", file=sys.stderr)
        sys.exit(1)
    
    if not left.is_dir():
        print(f"ERROR: Left path is not a directory: {args.left}", file=sys.stderr)
        sys.exit(1)
    if not right.is_dir():
        print(f"ERROR: Right path is not a directory: {args.right}", file=sys.stderr)
        sys.exit(1)
    
    try:
        left_struct = scan_directory(left, args.depth, args.binary)
        right_struct = scan_directory(right, args.depth, args.binary)
        
        results = compare_structures(left_struct, right_struct)
        
        print(f"COMPARE {left}/ {right}/")
        print(f"identical: {len(results['identical_files'])}")
        print(f"different: {len(results['different_files'])}")
        print(f"left_only: {len([x for x in results['left_only'] if x.get('type') != 'directory'])}")
        print(f"right_only: {len([x for x in results['right_only'] if x.get('type') != 'directory'])}")
        print(f"total_files: {results['total_files']}")
        print("")
        
        if results['identical_files']:
            print("identical_files:")
            for f in results['identical_files']:
                print(f"  - {f['path']} ({f['crc32']})")
            print("")
        
        if results['different_files']:
            print("different_files:")
            for f in results['different_files']:
                print(f"  - {f['path']} (left: {f['left_crc32']}, right: {f['right_crc32']})")
            print("")
        
        left_orphans = [x for x in results['left_only'] if x.get('type') != 'directory']
        right_orphans = [x for x in results['right_only'] if x.get('type') != 'directory']
        
        if left_orphans or right_orphans:
            print("orphans:")
            if left_orphans:
                print("  left_only:")
                for f in left_orphans:
                    print(f"    - {f['path']} ({format_size(f['size'])})")
            if right_orphans:
                print("  right_only:")
                for f in right_orphans:
                    print(f"    - {f['path']} ({format_size(f['size'])})")
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_duplicates(args):
    folder = Path(args.folder)
    
    if not folder.exists():
        print(f"ERROR: Folder does not exist: {args.folder}", file=sys.stderr)
        sys.exit(1)
    
    if not folder.is_dir():
        print(f"ERROR: Not a directory: {args.folder}", file=sys.stderr)
        sys.exit(1)
    
    try:
        file_hashes = {}
        
        def scan_for_duplicates(root_path: Path, current_depth: int = 0):
            if current_depth >= args.depth:
                return
            
            try:
                for item in root_path.iterdir():
                    if item.name.startswith('.'):
                        continue
                    
                    if item.is_file():
                        try:
                            crc32 = calculate_crc32(item)
                            relative_path = item.relative_to(folder)
                            
                            if crc32 not in file_hashes:
                                file_hashes[crc32] = []
                            
                            file_hashes[crc32].append({
                                "path": str(relative_path),
                                "size": item.stat().st_size
                            })
                        except (OSError, ValueError):
                            continue
                    
                    elif item.is_dir() and not item.is_symlink():
                        scan_for_duplicates(item, current_depth + 1)
            
            except (OSError, PermissionError):
                pass
        
        scan_for_duplicates(folder)
        
        duplicates = {k: v for k, v in file_hashes.items() if len(v) > 1}
        unique_count = len(file_hashes) - len(duplicates)
        total_files = sum(len(v) for v in file_hashes.values())
        total_duplicate_files = sum(len(v) for v in duplicates.values())
        total_wasted = sum(v[0]['size'] * (len(v) - 1) for v in duplicates.values())
        
        print(f"DUPLICATES {folder}/")
        print(f"total_files: {total_files}")
        print(f"unique_files: {unique_count}")
        print(f"duplicate_files: {total_duplicate_files}")
        print(f"duplicate_groups: {len(duplicates)}")
        print(f"wasted_bytes: {format_size(total_wasted)}")
        print("")
        
        if duplicates:
            print("duplicates:")
            for crc32, files in duplicates.items():
                print(f"  {crc32} ({format_size(files[0]['size'])} x {len(files)}):")
                for f in files:
                    print(f"    - {f['path']}")
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Compare folders and find duplicate files')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    compare_parser = subparsers.add_parser('compare', help='Compare two folder structures')
    compare_parser.add_argument('left', help='Path to first folder')
    compare_parser.add_argument('right', help='Path to second folder')
    compare_parser.add_argument('--depth', type=int, default=10, help='Maximum recursion depth (default: 10)')
    compare_parser.add_argument('--binary', action='store_true', help='Include binary files')
    
    dup_parser = subparsers.add_parser('duplicates', help='Find duplicate files in a folder')
    dup_parser.add_argument('folder', help='Path to folder')
    dup_parser.add_argument('--depth', type=int, default=10, help='Maximum recursion depth (default: 10)')
    
    args = parser.parse_args()
    
    if args.command == 'compare':
        cmd_compare(args)
    elif args.command == 'duplicates':
        cmd_duplicates(args)


if __name__ == "__main__":
    main()
