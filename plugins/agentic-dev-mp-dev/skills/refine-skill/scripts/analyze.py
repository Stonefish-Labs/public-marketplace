#!/usr/bin/env python3
"""
Static analysis tool for skill quality review.

Performs automated checks on a skill directory and outputs structured JSON
with findings. This handles the objective, mechanical checks — the reviewing
agent handles subjective quality assessment.

Usage:
    python3 analyze.py /path/to/skill-directory
"""

import argparse
import ast
import json
import os
import re
import sys

SCRIPT_EXTENSIONS = {
    ".py", ".sh", ".bash", ".zsh", ".fish", ".rb", ".js", ".ts"
}
REFERENCE_EXTENSIONS = {
    ".md", ".txt", ".rst", ".adoc", ".json", ".yaml", ".yml", ".toml", ".csv"
}
ASSET_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".pdf", ".pptx",
    ".docx", ".xlsx", ".zip", ".tar", ".gz", ".tgz", ".ttf", ".otf", ".woff",
    ".woff2", ".html", ".css"
}

STDLIB_MODULES = {
    "abc", "argparse", "ast", "asyncio", "atexit", "base64", "bisect",
    "calendar", "cgi", "cmd", "codecs", "collections", "colorsys",
    "concurrent", "configparser", "contextlib", "copy", "csv", "ctypes",
    "dataclasses", "datetime", "decimal", "difflib", "dis", "email",
    "encodings", "enum", "errno", "faulthandler", "filecmp", "fileinput",
    "fnmatch", "fractions", "ftplib", "functools", "gc", "getopt",
    "getpass", "gettext", "glob", "gzip", "hashlib", "heapq", "hmac",
    "html", "http", "imaplib", "importlib", "inspect", "io", "ipaddress",
    "itertools", "json", "keyword", "linecache", "locale", "logging",
    "lzma", "mailbox", "math", "mimetypes", "mmap", "multiprocessing",
    "numbers", "operator", "optparse", "os", "pathlib", "pdb", "pickle",
    "pkgutil", "platform", "plistlib", "poplib", "posixpath", "pprint",
    "profile", "pstats", "queue", "quopri", "random", "re", "readline",
    "reprlib", "resource", "rlcompleter", "sched", "secrets", "select",
    "selectors", "shelve", "shlex", "shutil", "signal", "site", "smtplib",
    "socket", "socketserver", "sqlite3", "ssl", "stat", "statistics",
    "string", "struct", "subprocess", "sys", "sysconfig", "syslog",
    "tarfile", "tempfile", "textwrap", "threading", "time", "timeit",
    "tkinter", "token", "tokenize", "tomllib", "trace", "traceback",
    "tracemalloc", "turtle", "types", "typing", "unicodedata", "unittest",
    "urllib", "uuid", "venv", "warnings", "wave", "weakref", "webbrowser",
    "xml", "xmlrpc", "zipfile", "zipimport", "zlib",
}


def suggest_resource_folder(skill_dir: str, entry_name: str) -> str:
    """Suggest where a misplaced top-level entry should live."""
    full_path = os.path.join(skill_dir, entry_name)
    if os.path.isdir(full_path):
        lowered = entry_name.lower()
        if "script" in lowered or "bin" in lowered:
            return "scripts"
        if "reference" in lowered or "docs" in lowered or "doc" in lowered:
            return "references"
        return "assets"

    _, ext = os.path.splitext(entry_name.lower())
    if ext in SCRIPT_EXTENSIONS:
        return "scripts"
    if ext in REFERENCE_EXTENSIONS:
        return "references"
    if ext in ASSET_EXTENSIONS:
        return "assets"
    return "unknown"


def validate_name_format(name: str, skill_dir: str) -> list:
    """Validate name field against the Agent Skills spec."""
    findings = []

    if len(name) > 64:
        findings.append({
            "severity": "error",
            "check": "name_length",
            "message": f"Name is {len(name)} characters — spec max is 64."
        })

    if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", name) and len(name) > 1:
        findings.append({
            "severity": "error",
            "check": "name_format",
            "message": f"Name '{name}' violates spec: must be lowercase alphanumeric + hyphens, cannot start or end with hyphen."
        })
    elif len(name) == 1 and not re.match(r"^[a-z0-9]$", name):
        findings.append({
            "severity": "error",
            "check": "name_format",
            "message": f"Name '{name}' must be a lowercase letter or digit."
        })

    if "--" in name:
        findings.append({
            "severity": "error",
            "check": "name_consecutive_hyphens",
            "message": f"Name '{name}' contains consecutive hyphens — not allowed by spec."
        })

    dir_name = os.path.basename(os.path.abspath(skill_dir))
    if name != dir_name:
        findings.append({
            "severity": "error",
            "check": "name_dir_match",
            "message": f"Name '{name}' does not match parent directory '{dir_name}' — spec requires these to match."
        })

    return findings


def parse_optional_fields(frontmatter: str) -> tuple:
    """Parse and validate optional frontmatter fields per spec."""
    findings = []
    metadata = {}

    license_match = re.search(r"^license:\s*(.+)$", frontmatter, re.MULTILINE)
    if license_match:
        metadata["license"] = license_match.group(1).strip()

    compat_match = re.search(r"^compatibility:\s*(.+)$", frontmatter, re.MULTILINE)
    if compat_match:
        val = compat_match.group(1).strip()
        metadata["compatibility"] = val
        if len(val) > 500:
            findings.append({
                "severity": "error",
                "check": "compatibility_length",
                "message": f"Compatibility field is {len(val)} characters — spec max is 500."
            })

    at_match = re.search(r"^allowed-tools:\s*(.+)$", frontmatter, re.MULTILINE)
    if at_match:
        metadata["allowed_tools"] = at_match.group(1).strip()

    meta_match = re.search(r"^metadata:\s*\n((?:\s+.+\n?)+)", frontmatter, re.MULTILINE)
    if meta_match:
        raw = meta_match.group(1)
        pairs = {}
        for line in raw.strip().split("\n"):
            kv = line.strip().split(":", 1)
            if len(kv) == 2:
                pairs[kv[0].strip()] = kv[1].strip().strip('"').strip("'")
        metadata["metadata"] = pairs

    return findings, metadata


def analyze_frontmatter(skill_md_path: str, skill_dir: str = "") -> dict:
    """Check SKILL.md frontmatter for required fields, spec compliance, and quality."""
    findings = []
    metadata = {}

    if not skill_dir:
        skill_dir = os.path.dirname(skill_md_path)

    with open(skill_md_path) as f:
        content = f.read()

    if not content.startswith("---"):
        findings.append({
            "severity": "error",
            "check": "frontmatter_exists",
            "message": "SKILL.md must start with YAML frontmatter (---)"
        })
        return {"findings": findings, "metadata": metadata}

    parts = content.split("---", 2)
    if len(parts) < 3:
        findings.append({
            "severity": "error",
            "check": "frontmatter_closed",
            "message": "YAML frontmatter is not properly closed with ---"
        })
        return {"findings": findings, "metadata": metadata}

    frontmatter = parts[1].strip()

    # --- Required: name ---
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        metadata["name"] = name
        findings.extend(validate_name_format(name, skill_dir))
    else:
        findings.append({
            "severity": "error",
            "check": "name_present",
            "message": "Frontmatter missing required 'name' field"
        })

    # --- Required: description ---
    desc_match = re.search(r"description:\s*>?\s*\n((?:\s+.+\n?)+)", frontmatter)
    if desc_match:
        desc = desc_match.group(1).strip()
        metadata["description"] = desc
        metadata["description_words"] = len(desc.split())
        metadata["description_chars"] = len(desc)
    elif re.search(r"description:\s*(.+)$", frontmatter, re.MULTILINE):
        desc = re.search(r"description:\s*(.+)$", frontmatter, re.MULTILINE).group(1).strip()
        metadata["description"] = desc
        metadata["description_words"] = len(desc.split())
        metadata["description_chars"] = len(desc)
    else:
        findings.append({
            "severity": "error",
            "check": "description_present",
            "message": "Frontmatter missing required 'description' field"
        })

    if "description" in metadata:
        cc = metadata["description_chars"]
        if cc > 1024:
            findings.append({
                "severity": "error",
                "check": "description_char_limit",
                "message": f"Description is {cc} characters — spec max is 1024."
            })

        wc = metadata["description_words"]
        if wc < 20:
            findings.append({
                "severity": "warning",
                "check": "description_length",
                "message": f"Description is only {wc} words — likely too short for effective triggering. Aim for 50-120 words."
            })
        elif wc > 150:
            findings.append({
                "severity": "warning",
                "check": "description_length",
                "message": f"Description is {wc} words — may be too long for metadata that's always in context. Aim for 50-120 words."
            })

        desc_lower = metadata["description"].lower()
        if "todo" in desc_lower or "[todo" in desc_lower:
            findings.append({
                "severity": "error",
                "check": "description_todo",
                "message": "Description contains TODO placeholder — not filled in"
            })

    # --- Optional fields ---
    opt_findings, opt_metadata = parse_optional_fields(frontmatter)
    findings.extend(opt_findings)
    metadata.update(opt_metadata)

    return {"findings": findings, "metadata": metadata}


def analyze_structure(skill_dir: str, fm_metadata: dict = None) -> dict:
    """Check directory structure and file sizes."""
    findings = []
    stats = {}
    if fm_metadata is None:
        fm_metadata = {}

    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        findings.append({
            "severity": "error",
            "check": "skill_md_exists",
            "message": "SKILL.md not found — required for all skills"
        })
        return {"findings": findings, "stats": stats}

    with open(skill_md) as f:
        lines = f.readlines()
    stats["skill_md_lines"] = len(lines)

    if len(lines) > 500:
        findings.append({
            "severity": "warning",
            "check": "skill_md_length",
            "message": f"SKILL.md is {len(lines)} lines — exceeds 500-line guideline. Consider moving detail to references/."
        })

    unwanted = ["README.md", "INSTALLATION_GUIDE.md", "CHANGELOG.md"]
    for uw in unwanted:
        if os.path.exists(os.path.join(skill_dir, uw)):
            findings.append({
                "severity": "warning",
                "check": "unwanted_files",
                "message": f"Found {uw} — skills are for AI agents, not human onboarding. Consider removing."
            })

    has_license_field = "license" in fm_metadata
    for license_file in ("LICENSE", "LICENSE.txt", "LICENSE.md"):
        if os.path.exists(os.path.join(skill_dir, license_file)):
            if not has_license_field:
                findings.append({
                    "severity": "warning",
                    "check": "license_file_orphaned",
                    "message": f"Found {license_file} but no 'license' field in frontmatter. Either add a license field referencing it or remove the file."
                })
            break

    # Count scripts
    scripts_dir = os.path.join(skill_dir, "scripts")
    if os.path.isdir(scripts_dir):
        scripts = [f for f in os.listdir(scripts_dir) if not f.startswith(".")]
        stats["script_count"] = len(scripts)
        stats["scripts"] = scripts
        if not scripts:
            findings.append({
                "severity": "warning",
                "check": "empty_directory",
                "message": "The 'scripts/' directory is empty. Empty directories should be removed."
            })
    else:
        stats["script_count"] = 0
        stats["scripts"] = []

    # Count references
    refs_dir = os.path.join(skill_dir, "references")
    if os.path.isdir(refs_dir):
        refs = [f for f in os.listdir(refs_dir) if not f.startswith(".")]
        stats["reference_count"] = len(refs)
        stats["references"] = refs
        if not refs:
            findings.append({
                "severity": "warning",
                "check": "empty_directory",
                "message": "The 'references/' directory is empty. Empty directories should be removed."
            })
    else:
        stats["reference_count"] = 0
        stats["references"] = []

    # Count assets
    assets_dir = os.path.join(skill_dir, "assets")
    if os.path.isdir(assets_dir):
        assets = [f for f in os.listdir(assets_dir) if not f.startswith(".")]
        stats["asset_count"] = len(assets)
        stats["assets"] = assets
        if not assets:
            findings.append({
                "severity": "warning",
                "check": "empty_directory",
                "message": "The 'assets/' directory is empty. Empty directories should be removed."
            })
    else:
        stats["asset_count"] = 0
        stats["assets"] = []

    # Check for misplaced top-level files/directories that should be in subfolders.
    allowed_top_level = {"SKILL.md", "scripts", "references", "assets", "agents"}
    top_level_entries = [
        entry for entry in os.listdir(skill_dir)
        if not entry.startswith(".")
    ]
    unexpected = sorted(
        entry for entry in top_level_entries
        if entry not in allowed_top_level
    )
    stats["unexpected_top_level"] = unexpected

    if unexpected:
        by_target = {"scripts": [], "references": [], "assets": [], "unknown": []}
        for entry in unexpected:
            by_target[suggest_resource_folder(skill_dir, entry)].append(entry)

        actions = []
        for target in ("scripts", "references", "assets"):
            entries = by_target[target]
            if not entries:
                continue
            move_list = ", ".join(entries)
            target_dir = os.path.join(skill_dir, target)
            if os.path.isdir(target_dir):
                actions.append(f"move to {target}/: {move_list}")
            else:
                actions.append(f"create {target}/ and move: {move_list}")

        if by_target["unknown"]:
            actions.append(
                "manually classify and move: " + ", ".join(by_target["unknown"])
            )

        findings.append({
            "severity": "warning",
            "check": "top_level_layout",
            "message": (
                "Found top-level entries outside the canonical skill layout "
                f"(SKILL.md, scripts/, references/, assets/, agents/): "
                + ", ".join(unexpected)
                + ". Reorganize by "
                + "; ".join(actions)
                + "."
            ),
        })

    return {"findings": findings, "stats": stats}


def analyze_python_file(filepath: str) -> dict:
    """Static analysis of a single Python file."""
    findings = []
    stats = {}

    with open(filepath) as f:
        source = f.read()

    stats["lines"] = source.count("\n") + 1
    stats["path"] = filepath

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        findings.append({
            "severity": "error",
            "check": "syntax",
            "message": f"Syntax error: {e}"
        })
        return {"findings": findings, "stats": stats}

    # Collect all imports
    imports = {}
    third_party = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                imports[alias.name] = node.lineno
                if root not in STDLIB_MODULES:
                    third_party.append({"module": alias.name, "line": node.lineno})
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]
                imports[node.module] = node.lineno
                if root not in STDLIB_MODULES:
                    third_party.append({"module": node.module, "line": node.lineno})

    stats["imports"] = list(imports.keys())
    stats["third_party"] = third_party

    if third_party:
        mods = ", ".join(tp["module"] for tp in third_party)
        findings.append({
            "severity": "info",
            "check": "third_party_imports",
            "message": f"Third-party dependencies found: {mods}. Ensure these are documented and installed."
        })

    # Check for unused imports by scanning source for references
    for mod_name, lineno in imports.items():
        short = mod_name.split(".")[-1]
        # Remove the import line itself before checking usage
        lines = source.split("\n")
        other_lines = "\n".join(l for i, l in enumerate(lines, 1) if i != lineno)
        if short not in other_lines:
            findings.append({
                "severity": "warning",
                "check": "unused_import",
                "message": f"Import '{mod_name}' (line {lineno}) appears unused"
            })

    # Check for defined-but-unused module-level variables (simple heuristic)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id
                    # Count occurrences in source (excluding the definition line)
                    lines = source.split("\n")
                    other_lines = "\n".join(
                        l for i, l in enumerate(lines, 1) if i != node.lineno
                    )
                    # Use word boundary matching to avoid false positives
                    pattern = r"\b" + re.escape(name) + r"\b"
                    if not re.search(pattern, other_lines):
                        findings.append({
                            "severity": "warning",
                            "check": "unused_variable",
                            "message": f"Module-level variable '{name}' (line {node.lineno}) appears unused"
                        })

    # Check for functions with no docstring
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)):
                if not node.name.startswith("_"):
                    findings.append({
                        "severity": "info",
                        "check": "missing_docstring",
                        "message": f"Public function '{node.name}' (line {node.lineno}) has no docstring"
                    })

    # Check for error handling
    has_try = any(isinstance(n, ast.Try) for n in ast.walk(tree))
    stats["has_error_handling"] = has_try
    if not has_try:
        findings.append({
            "severity": "info",
            "check": "error_handling",
            "message": "No try/except blocks found — consider adding error handling for robustness"
        })

    return {"findings": findings, "stats": stats}


def analyze_file_references(skill_dir: str) -> dict:
    """Scan SKILL.md for relative path references and verify they exist on disk."""
    findings = []
    stats = {"referenced_files": [], "broken_refs": [], "deep_chains": []}

    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        return {"findings": findings, "stats": stats}

    with open(skill_md) as f:
        content = f.read()

    parts = content.split("---", 2)
    body = parts[2] if len(parts) >= 3 else content

    md_link_pattern = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
    bare_path_pattern = re.compile(
        r"(?:^|[\s`\"'(])((?:scripts|references|assets)/[^\s,)\"'>`]+)", re.MULTILINE
    )

    refs = set()
    for _, target in md_link_pattern.findall(body):
        if not target.startswith(("http://", "https://", "#", "mailto:")):
            refs.add(target)
    for match in bare_path_pattern.findall(body):
        refs.add(match)

    stats["referenced_files"] = sorted(refs)

    for ref in refs:
        full = os.path.join(skill_dir, ref)
        if not os.path.exists(full):
            stats["broken_refs"].append(ref)
            findings.append({
                "severity": "error",
                "check": "broken_file_ref",
                "message": f"SKILL.md references '{ref}' but the file does not exist."
            })

    depth_limit = {"scripts", "references", "assets"}
    for ref in refs:
        ref_path = os.path.join(skill_dir, ref)
        if os.path.isfile(ref_path) and ref.endswith((".md", ".txt", ".rst")):
            try:
                with open(ref_path) as rf:
                    ref_body = rf.read()
                nested = md_link_pattern.findall(ref_body)
                for _, nested_target in nested:
                    if nested_target.startswith(("http://", "https://", "#")):
                        continue
                    parts_of_ref = nested_target.split("/")
                    if len(parts_of_ref) > 0 and parts_of_ref[0] in depth_limit:
                        stats["deep_chains"].append(f"{ref} -> {nested_target}")
                        findings.append({
                            "severity": "warning",
                            "check": "deep_reference_chain",
                            "message": f"Nested reference chain: {ref} references {nested_target}. Spec recommends keeping references one level deep."
                        })
            except OSError:
                pass

    return {"findings": findings, "stats": stats}


SHELL_EXTENSIONS = {".sh", ".bash", ".zsh", ".fish"}


def analyze_shell_script(filepath: str) -> dict:
    """Basic structural checks for shell scripts."""
    findings = []
    stats = {"path": filepath}

    with open(filepath) as f:
        source = f.read()

    lines = source.split("\n")
    stats["lines"] = len(lines)

    if not lines or not lines[0].startswith("#!"):
        findings.append({
            "severity": "warning",
            "check": "shebang_missing",
            "message": f"Shell script '{os.path.basename(filepath)}' has no shebang line (e.g. #!/usr/bin/env bash)."
        })

    has_set_e = any(
        re.match(r"^\s*set\s+.*-.*e", line) for line in lines
    )
    has_set_pipefail = any(
        re.match(r"^\s*set\s+.*-o\s+pipefail", line) for line in lines
    )
    if not has_set_e:
        findings.append({
            "severity": "info",
            "check": "shell_error_handling",
            "message": f"Shell script '{os.path.basename(filepath)}' does not use 'set -e'. Consider adding 'set -euo pipefail' for robustness."
        })
    elif not has_set_pipefail:
        findings.append({
            "severity": "info",
            "check": "shell_pipefail",
            "message": f"Shell script '{os.path.basename(filepath)}' uses 'set -e' but not 'set -o pipefail'. Pipe failures may go undetected."
        })

    if not os.access(filepath, os.X_OK):
        findings.append({
            "severity": "info",
            "check": "shell_not_executable",
            "message": f"Shell script '{os.path.basename(filepath)}' is not marked executable (chmod +x)."
        })

    return {"findings": findings, "stats": stats}


def estimate_tokens(text: str) -> int:
    """Rough token estimate: word count * 1.3, which approximates typical LLM tokenizers."""
    return int(len(text.split()) * 1.3)


def analyze_skill(skill_dir: str) -> dict:
    """Run all analyses on a skill directory."""
    results = {
        "skill_dir": os.path.abspath(skill_dir),
        "sections": {},
        "summary": {"error": 0, "warning": 0, "info": 0}
    }

    # Frontmatter analysis
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if os.path.exists(skill_md):
        fm = analyze_frontmatter(skill_md, skill_dir)
        results["sections"]["frontmatter"] = fm

    # Structure analysis (pass frontmatter metadata for context-aware checks)
    fm_metadata = results["sections"].get("frontmatter", {}).get("metadata", {})
    struct = analyze_structure(skill_dir, fm_metadata)
    results["sections"]["structure"] = struct

    # Token estimation for SKILL.md body
    if os.path.exists(skill_md):
        with open(skill_md) as f:
            content = f.read()
        parts = content.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]
            tok = estimate_tokens(body)
            struct_stats = results["sections"]["structure"].get("stats", {})
            struct_stats["estimated_body_tokens"] = tok
            if tok > 5000:
                results["sections"]["structure"]["findings"].append({
                    "severity": "warning",
                    "check": "body_token_count",
                    "message": f"SKILL.md body is ~{tok} tokens — spec recommends <5000. Move detail to references/."
                })

    # File reference analysis
    refs = analyze_file_references(skill_dir)
    results["sections"]["file_references"] = refs

    # Script analysis
    scripts_dir = os.path.join(skill_dir, "scripts")
    if os.path.isdir(scripts_dir):
        py_results = []
        shell_results = []
        for fname in sorted(os.listdir(scripts_dir)):
            fpath = os.path.join(scripts_dir, fname)
            if fname.endswith(".py"):
                py_results.append(analyze_python_file(fpath))
            else:
                _, ext = os.path.splitext(fname.lower())
                if ext in SHELL_EXTENSIONS:
                    shell_results.append(analyze_shell_script(fpath))
        if py_results:
            results["sections"]["python"] = py_results
        if shell_results:
            results["sections"]["shell"] = shell_results

    # Reference file size analysis
    refs_dir = os.path.join(skill_dir, "references")
    if os.path.isdir(refs_dir):
        ref_findings = []
        for fname in sorted(os.listdir(refs_dir)):
            if fname.startswith("."):
                continue
            fpath = os.path.join(refs_dir, fname)
            if os.path.isfile(fpath):
                with open(fpath) as rf:
                    line_count = sum(1 for _ in rf)
                if line_count > 300:
                    ref_findings.append({
                        "severity": "warning",
                        "check": "reference_file_size",
                        "message": f"Reference file '{fname}' is {line_count} lines. Keep reference files focused and concise to minimize context usage."
                    })
        if ref_findings:
            results["sections"].setdefault("file_references", {"findings": [], "stats": {}})
            results["sections"]["file_references"]["findings"].extend(ref_findings)

    # Tally findings
    for section in results["sections"].values():
        items = section if isinstance(section, list) else [section]
        for item in items:
            for f in item.get("findings", []):
                results["summary"][f["severity"]] = (
                    results["summary"].get(f["severity"], 0) + 1
                )

    return results


def main():
    parser = argparse.ArgumentParser(description="Static analysis for skill quality")
    parser.add_argument("skill_dir", help="Path to skill directory")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                        help="Output format")
    args = parser.parse_args()

    if not os.path.isdir(args.skill_dir):
        print(f"Error: '{args.skill_dir}' is not a directory", file=sys.stderr)
        sys.exit(1)

    results = analyze_skill(args.skill_dir)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        # Human-readable text output
        print(f"=== Skill Analysis: {results['skill_dir']} ===\n")

        for section_name, section_data in results["sections"].items():
            items = section_data if isinstance(section_data, list) else [section_data]
            for item in items:
                # Print stats
                for key, val in item.get("stats", {}).items():
                    print(f"  [{section_name}] {key}: {val}")
                for key, val in item.get("metadata", {}).items():
                    if key != "description":  # Don't dump the full description
                        print(f"  [{section_name}] {key}: {val}")

                # Print findings
                for f in item.get("findings", []):
                    icon = {"error": "X", "warning": "!", "info": "-"}[f["severity"]]
                    print(f"  [{icon}] {f['check']}: {f['message']}")
            print()

        s = results["summary"]
        print(f"Summary: {s['error']} error(s), {s['warning']} warning(s), {s['info']} info")


if __name__ == "__main__":
    main()
