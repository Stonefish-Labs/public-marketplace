# IntelliDiff Reference

Detailed documentation for comparison options and normalization features.

## Comparison Modes

### exact (default)

Fast CRC32 hash comparison. Binary-safe, detects any byte-level difference.

Use when:
- You need the fastest comparison
- Files should be byte-identical
- Comparing binary files

### smart

Text-aware comparison with normalization. Files are read as UTF-8 text and compared line-by-line after normalization.

Use when:
- Comparing text files that may have formatting differences
- You want to ignore whitespace, case, or line endings
- Content matters more than exact bytes

### binary

Forces binary comparison even for text files. Uses CRC32.

Use when:
- Explicitly comparing binary files
- You want hash output for non-text files

## Normalization Options

These options only apply in `smart` mode.

### --ignore-blank

Removes all blank lines before comparison.

Useful for:
- Code where blank line conventions differ
- Configuration files with varying spacing

### --ignore-whitespace

Strips leading and trailing whitespace from each line.

Useful for:
- Code formatted with different indentation styles
- Files with trailing whitespace differences

### --ignore-case

Converts all text to lowercase before comparison.

Useful for:
- Case-insensitive languages (HTML, some configs)
- Documentation where casing varies

### --ignore-newlines

Normalizes line endings:
- CRLF (Windows) → LF (Unix)
- CR (old Mac) → LF

Useful for:
- Cross-platform file comparison
- Git diff settings that don't normalize

### --normalize-tabs

Converts all tabs to spaces using Python's default tab size (8 spaces).

Useful for:
- Code with mixed tab/space indentation
- Files edited in different editors

### --unicode-normalize

Applies Unicode NFKC normalization:
- Compatibility characters → canonical forms
- Accented characters → composed or decomposed forms

Useful for:
- International text comparison
- Files from different systems with varying Unicode representations

## Output Formats

### hash.py

Always outputs plaintext with labeled fields:
```
<filename>
crc32: <8-char hex>
size: <human-readable>
type: text|binary
modified: <datetime> (<weekday>)
created: <datetime> (<weekday>)
path: <absolute path>
```

### compare.py

Status line: `IDENTICAL` or `DIFFERENT`

For IDENTICAL:
```
IDENTICAL
left: <filename> (<crc32>)
right: <filename> (<crc32>)
```

For DIFFERENT:
```
DIFFERENT
left: <filename> (<size>, <crc32>)
right: <filename> (<size>, <crc32>)
diff:
--- <left_path>
+++ <right_path>
@@ -start,count +start,count @@
<unified diff output>
```

### folders.py compare

```
COMPARE <left>/ <right>/
identical: <count>
different: <count>
left_only: <count>
right_only: <count>
total_files: <count>

identical_files:
  - <path> (<crc32>)
  ...

different_files:
  - <path> (left: <crc32>, right: <crc32>)
  ...

orphans:
  left_only:
    - <path> (<size>)
  right_only:
    - <path> (<size>)
```

### folders.py duplicates

```
DUPLICATES <folder>/
total_files: <count>
unique_files: <count>
duplicate_files: <count>
duplicate_groups: <count>
wasted_bytes: <human-readable>

duplicates:
  <crc32> (<size> x <count>):
    - <path>
    - <path>
  ...
```

### lines.py

```
    <line_num>| <content>    # Context line
>>> <line_num>| <content>    # In-range line
```

## Binary Detection

Text vs binary classification uses a null-byte heuristic: if the first 1024 bytes contain a null byte (0x00), the file is classified as binary.

**Caveats:**
- UTF-16/UTF-32 text files contain null bytes and will be classified as binary
- Some binary formats (e.g., certain image headers) may not have null bytes in the first 1KB
- For edge cases, use `--mode binary` to force binary comparison

This heuristic works well for common cases (UTF-8 text vs images, executables, archives) but is not perfect.

## CRC32 Hash

All scripts use CRC32 for file hashing:
- Fast computation (streaming, constant memory)
- 32-bit hash (8 hex characters)
- Not cryptographically secure (not the goal)
- Good for quick identity checking

For cryptographic verification, use external tools (sha256sum, etc.).

## Error Handling

All scripts:
- Exit code 0 on success
- Exit code 1 on error
- Error messages written to stderr
- Errors prefixed with `ERROR:`
