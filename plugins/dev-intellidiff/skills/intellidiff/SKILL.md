---
name: intellidiff
description: >
  Compare files and folders, detect duplicates, find differences, and read specific line ranges. Use when the user asks to compare files, find what changed between files or folders, detect duplicate files, check if files are identical or different, get file hashes/checksums, find orphan files in directories, read specific lines from a file, or analyze diffs. Triggers on keywords: compare, diff, difference, duplicate, identical, same file, what changed, hash, checksum, orphan, read lines.
---

# IntelliDiff

Compare files and folders with intelligent text normalization.

## Why This Skill

Comparing files seems simple until you hit edge cases: files that look identical but have different line endings (CRLF vs LF), whitespace differences, or case variations. This skill handles those edge cases with normalization options while providing fast byte-level comparison when you need exactness.

Use this instead of shelling out to `diff` or reading files manually — the scripts handle edge cases, provide structured output, and work without external dependencies.

## Quick Start

```bash
# Compare two files
python3 scripts/compare.py file1.txt file2.txt

# Find duplicates in a folder
python3 scripts/folders.py duplicates ./src

# Compare folder structures
python3 scripts/folders.py compare ./v1 ./v2

# Get file hash and metadata
python3 scripts/hash.py myfile.txt

# Read specific lines from a file
python3 scripts/lines.py myfile.txt --start 10 --end 20 --context 2
```

## Scripts

### hash.py - Get file hash and metadata

```bash
python3 scripts/hash.py <file>
```

Output:
```
filename.ext
crc32: abcd1234
size: 1.5KB
type: text
modified: 2024-01-15 14:30:00 (Monday)
created: 2024-01-10 09:00:00 (Wednesday)
path: /full/path/to/file
```

### compare.py - Compare two files

```bash
python3 scripts/compare.py <left> <right> [--mode MODE] [options]
```

**When to use each mode:**

| Mode | Use When | Speed |
|------|----------|-------|
| `exact` | You need byte-identical verification; any difference matters | Fastest |
| `smart` | Content matters more than formatting; ignore whitespace/case/etc | Medium |
| `binary` | Comparing non-text files; force hash comparison | Fast |

**Normalization options (smart mode only):**

| Option | Effect | Use When |
|--------|--------|----------|
| `--ignore-blank` | Skip blank lines | Formatting differs in spacing |
| `--ignore-whitespace` | Strip leading/trailing whitespace | Indentation varies |
| `--ignore-case` | Lowercase everything | Case shouldn't matter |
| `--ignore-newlines` | Normalize CRLF/LF/CR to LF | Cross-platform files |
| `--normalize-tabs` | Convert tabs to spaces | Mixed tab/space indentation |
| `--unicode-normalize` | Apply NFKC normalization | Unicode varies by source |

**Output:**
- `IDENTICAL` or `DIFFERENT` status line
- File paths and hashes
- Unified diff (if different in smart mode)

### folders.py - Folder operations

```bash
# Compare two folder structures
python3 scripts/folders.py compare <left> <right> [--depth N] [--binary]

# Find duplicate files
python3 scripts/folders.py duplicates <folder> [--depth N]
```

**Options:**
- `--depth N` - Maximum recursion depth (default: 10)
- `--binary` - Include binary files in comparison (skipped by default)

**Compare output:**
- Summary counts (identical, different, left_only, right_only)
- Lists of files in each category
- Orphan files (exist in only one folder)

**Duplicates output:**
- Total/unique/duplicate file counts
- Wasted bytes from duplicates
- Grouped by CRC32 hash

### lines.py - Read specific lines

```bash
python3 scripts/lines.py <file> [--start N] [--end N] [--context N]
```

**Options:**
- `--start N` - Starting line number (1-based, default: 1)
- `--end N` - Ending line number (default: end of file)
- `--context N` - Extra lines before/after range

**Output format:**
```
    8| function setup() {
    9|     console.log("Starting...");
>>> 10|     const data = loadData();
>>> 11|     if (!data) {
>>> 12|         throw new Error("No data");
>>> 13|     }
   14| }
```

Lines in the requested range are marked with `>>>`.

## Examples

### Check if two config files are functionally identical

```bash
python3 scripts/compare.py config.dev.json config.prod.json --mode smart --ignore-whitespace --ignore-blank
```

### Find all duplicate files in a large project

```bash
python3 scripts/folders.py duplicates ./src --depth 20
```

### See what changed between backup and current

```bash
python3 scripts/folders.py compare ./backup ./current --depth 15
```

### Read a specific function from source

```bash
python3 scripts/lines.py app.py --start 45 --end 67 --context 3
```

### Quick hash check on a file

```bash
python3 scripts/hash.py myfile.txt
```

## Additional Resources

For detailed output format specifications and advanced options, see [references/reference.md](references/reference.md).
