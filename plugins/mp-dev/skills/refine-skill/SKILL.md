---
name: refine-skill
description: >
  Review and score skills for quality, correctness, and effectiveness. Use this skill
  whenever you need to evaluate an existing skill, audit a skill before deployment, check
  a skill for bugs or dead code, or score a skill's quality on a standardized rubric. Also
  use it when someone asks "is this skill any good?", "review my skill", "rate this skill",
  "what's wrong with this skill", or "how can I improve this skill". This skill provides
  both automated static analysis (dead code, unused imports, frontmatter validation) and a
  structured rubric for subjective evaluation (triggering quality, conciseness, writing
  style). The output is a scored report with concrete, prioritized fixes. Use this skill
  even for quick gut-checks — a fast review catches bugs that cost hours to debug later.
---

# Skill Reviewer

Evaluate any skill against a standardized quality rubric. Produces a scored report
with concrete fixes, ordered by impact. Combines automated static analysis with
structured subjective review.

## Review Workflow

### Step 1: Automated Analysis

Run the static analysis script against the skill directory:

```bash
python3 <skill-path>/scripts/analyze.py /path/to/skill --format text
```

Use `--format json` if you need structured output for further processing.

This catches mechanical issues automatically: spec compliance (name format, name-directory
match, description char limit, optional field validation), broken file references, token
estimation, dead imports, unused variables, third-party dependencies, structural problems,
misplaced top-level files/directories, line counts, and shell script structure.
Start here because these findings are objective — they're either present or not.

If `skills-ref` is available, also run `skills-ref validate /path/to/skill` for additional
spec validation from the [official reference library](https://github.com/agentskills/agentskills/tree/main/skills-ref).

### Step 2: Read the Rubric

Read `references/rubric.md` for the full scoring criteria. The rubric covers eight
dimensions, each with a 1-10 scale and specific criteria per score band:

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| Triggering & Description | 1.5x | Would the skill activate when it should? |
| Conciseness | 1.0x | Does every line earn its place? |
| Why Explanation | 1.0x | Are instructions motivated, not just commanded? |
| Progressive Disclosure | 1.0x | Is info at the right loading level? |
| Script Quality | 1.5x | Do bundled scripts actually work correctly? |
| Separation of Concerns | 1.0x | Does the skill have a single clear job? |
| Generality | 1.0x | Would it work beyond the test cases? |
| Writing Style | 0.5x | Is it scannable, imperative, well-structured? |

Triggering and Script Quality carry 1.5x weight because they're the two most common
failure modes — skills that don't fire, and scripts that produce wrong results.

### Step 3: Manual Investigation

With the rubric in mind, investigate the skill:

1. **Verify spec compliance** — confirm `name` matches parent directory, is
   lowercase alphanumeric + hyphens (1-64 chars, no leading/trailing/consecutive
   hyphens). Confirm description is under 1024 characters. Check optional fields
   (`license`, `compatibility` ≤500 chars, `metadata`, `allowed-tools`) for
   correctness when present.
2. **Read SKILL.md** — evaluate description, body structure, style. Estimate
   token cost of the body (target under 5000 tokens, roughly word count x 1.3).
3. **Read each bundled script** — all languages, not just Python. Look for bugs,
   dead code, edge cases. Check shell scripts for shebang and error handling.
4. **Cross-reference claims vs. behavior** — if SKILL.md says "supports X", verify
   the script actually handles X. This is where the most damaging bugs hide.
5. **Verify file references** — every relative path in SKILL.md should resolve to
   an existing file. Check that reference chains stay one level deep (the spec
   warns against deeply nested reference chains).
6. **Test edge cases** — run scripts with tricky inputs, boundary conditions,
   unusual phrasings. Think about what a real user would actually type.
7. **Check what's missing** — are there limitations that aren't documented?
   Patterns that should work but don't?
8. **Check folder conventions** — if reusable resources are at the skill root,
   propose creating `scripts/`, `references/`, and/or `assets/` (as needed) and
   moving files into those folders.

### Step 4: Score and Report

First, check the spec compliance gate from the rubric. If the skill fails any
spec compliance checks (name format, description limit, broken file references),
report those failures first and note the score as provisional until they're fixed.

Score each dimension, then compute the weighted overall:

```
overall = (triggering×1.5 + conciseness×1.0 + why×1.0 + disclosure×1.0
         + scripts×1.5 + separation×1.0 + generality×1.0 + style×0.5) / 8.5
```

Present the report with this structure:

1. **Spec compliance** — pass/fail gate results (name, description, structure, references)
2. **Static analysis** — output from analyze.py
3. **Dimension scores** — score, evidence, specific issues per dimension
4. **Overall score** — weighted average out of 10
5. **Fix list** organized by priority:
   - **Must fix**: spec violations, bugs, broken features, misleading docs
   - **Should fix**: dead code, documentation gaps, missing edge cases, and
     structure cleanup (create `scripts/` / `references/` / `assets/` when
     needed and move misplaced files)
   - **Nice to have**: style improvements, coverage expansion
   - **Cleanup**: Remove any empty progressive disclosure subfolders (`scripts/`, `assets/`, `references/`) using `find <target-dir> -type d -empty -delete`

## What Makes a Good Review

A good skill review is honest and specific. Avoid vague praise ("looks good") or
vague criticism ("needs work"). Every finding should point to a specific line, file,
or behavior, and every fix should be concrete enough that someone could implement it
without asking follow-up questions.

The goal isn't to be harsh — it's to catch the things that would cause real problems
when the skill is used at scale. A bug in a script that's called thousands of times
will burn thousands of tool calls producing wrong results. An undertriggered description
means the skill sits unused while the model fumbles through the task manually. These
are the high-impact findings worth surfacing.

When reviewing script correctness, actually run the scripts. Don't just read the code
and guess — execute it with realistic inputs and edge cases. The "in N business days"
bug pattern (where a regex can't match multi-word units because `\w` doesn't cross
spaces) is the kind of thing that looks fine on a read-through but fails immediately
when tested.
