# Skill Review Rubric

Use this rubric to evaluate skills across eight dimensions. Each dimension is scored
1-10. The overall score is the average, weighted by the category weights below.

Before scoring, verify spec compliance. A skill that fails the prerequisite gate
has structural defects that must be fixed before quality scoring is meaningful.

## Spec Compliance (prerequisite gate)

These are pass/fail checks from the Agent Skills specification. Any failure here
should be reported as a **must fix** item before proceeding with scoring. If the
skill fails multiple spec checks, note the score as provisional.

| Check | Rule | Severity |
|-------|------|----------|
| Name format | 1-64 chars, lowercase alphanumeric + hyphens only, no leading/trailing/consecutive hyphens | error |
| Name-directory match | `name` field must match parent directory name exactly | error |
| Description present | Non-empty, max 1024 characters | error |
| Frontmatter well-formed | Starts and ends with `---`, contains valid YAML | error |
| Compatibility length | If present, max 500 characters | error |
| Body token budget | SKILL.md body should be under ~5000 tokens (roughly word count x 1.3) | warning |
| Line count | SKILL.md should be under 500 lines; move detail to `references/` | warning |
| File references valid | All relative paths in SKILL.md must resolve to existing files | error |
| Directory structure | Only `SKILL.md`, `scripts/`, `references/`, `assets/`, `agents/` at root | warning |

Run `scripts/analyze.py` to check these automatically. Optionally also run
`skills-ref validate` (from the [reference library](https://github.com/agentskills/agentskills/tree/main/skills-ref))
for additional validation.

## Scoring Dimensions

### 1. Triggering & Description (weight: 1.5x)

The description is the primary mechanism that determines whether the skill gets used.
A skill that doesn't trigger when it should is worthless regardless of how good its
internals are.

| Score | Criteria |
|-------|----------|
| 9-10 | Description covers all plausible trigger phrases. Explicitly lists edge cases. Addresses undertriggering with assertive language. Clear scope boundaries (what it does AND doesn't do). |
| 7-8 | Good trigger coverage, minor gaps. Scope is clear. Could catch a few more edge cases. |
| 5-6 | Basic triggers present but missing common phrasings. Scope is vague. |
| 3-4 | Minimal triggering — would miss most use cases. |
| 1-2 | No meaningful trigger phrases. Generic or placeholder description. |

**What to check:**
- Does the description list specific trigger phrases/contexts?
- Would the skill trigger for paraphrased versions of the same intent?
- Does it address undertriggering (the "even if you think you can..." pattern)?
- Are scope boundaries clear (what's in vs. out)?
- Is the description 50-120 words (the sweet spot for always-in-context metadata)?
- Is the description under the spec hard limit of 1024 characters?

### 2. Conciseness (weight: 1.0x)

Every line in SKILL.md costs context window space every time the skill triggers.
Lean skills are fast skills.

| Score | Criteria |
|-------|----------|
| 9-10 | Every line earns its place. No redundancy between description and body. Tables used for dense info. Under 200 lines. |
| 7-8 | Mostly lean. Minor redundancy. Under 300 lines. |
| 5-6 | Some bloat — sections that repeat or could be cut. 300-500 lines. |
| 3-4 | Significant bloat. Explanations that don't aid the model. Over 500 lines without references. |
| 1-2 | Massive, unfocused. Would eat significant context for little value. |

**What to check:**
- Does the body repeat what's in the description?
- Are there sections a model wouldn't need (installation guides, changelogs)?
- Could any section be moved to references/ for on-demand loading?
- Is information density high (tables, examples) or low (verbose prose)?

### 3. Why Explanation (weight: 1.0x)

Skills that explain WHY produce better results than skills that just say WHAT.
Models with good theory of mind respond better to reasoning than rigid commands.

| Score | Criteria |
|-------|----------|
| 9-10 | Every instruction has clear motivation. The model understands failure modes and can reason about edge cases independently. No unexplained rigid rules. |
| 7-8 | Most instructions are motivated. A few rules lack explanation but are reasonable. |
| 5-6 | Mix of explained and unexplained rules. Some ALWAYS/NEVER without rationale. |
| 3-4 | Mostly imperative with little explanation. Rigid structure. |
| 1-2 | Pure command list. No reasoning provided. |

**What to check:**
- Are there ALWAYS/NEVER/MUST in all caps without explanation? (yellow flag)
- Does the skill explain what goes wrong if instructions aren't followed?
- Could a model generalize the instructions to novel situations?
- Is there a "Why This Exists" or equivalent section?

### 4. Progressive Disclosure (weight: 1.0x)

The three-level loading system: metadata (~100 tokens, always in context) →
SKILL.md body (<5000 tokens recommended, loaded on trigger) → bundled resources
(loaded on demand). Well-structured skills minimize what's loaded at each level.

| Score | Criteria |
|-------|----------|
| 9-10 | Clean level separation. SKILL.md body is self-sufficient for common cases. References used for deep dives. Scripts execute without being loaded. Body under 5000 tokens. |
| 7-8 | Good separation. Maybe one reference that could be inlined or vice versa. |
| 5-6 | Everything in SKILL.md — workable but not optimal for large skills. |
| 3-4 | Information in wrong levels (deep detail in description, overview in references). |
| 1-2 | No consideration for loading levels. |

**What to check:**
- Is the description self-contained for triggering decisions?
- Does SKILL.md handle the 80% case without needing references?
- Is the SKILL.md body under the spec-recommended 5000 token budget?
- Are references clearly signposted (when to read, what you'll find)?
- Are individual reference files focused and concise (not dumping entire docs)?
- Are scripts self-contained executables (not requiring the model to read them)?
- Are reusable files organized under `scripts/`, `references/`, and `assets/`
  instead of being left at the skill root?

### 5. Script Quality (weight: 1.5x)

If the skill bundles scripts, they need to work correctly. Bugs in scripts
directly undermine the skill's value and the model's trust in its outputs.
This applies to all script types — Python, shell, JavaScript, TypeScript, Ruby,
not just Python.

| Score | Criteria |
|-------|----------|
| 9-10 | Zero dead code. All documented features work. Good error messages. Structured output. Handles edge cases. Minimal dependencies. |
| 7-8 | Works correctly. Minor dead code or missing edge cases. Dependencies are documented. |
| 5-6 | Mostly works but has bugs or unreachable code paths. Missing error handling. |
| 3-4 | Significant bugs. Documented features that don't work. Poor error messages. |
| 1-2 | Broken. Would fail on basic inputs. |

**What to check (use scripts/analyze.py for automated checks):**
- Dead imports or unused variables?
- Third-party dependencies — documented and necessary?
- Do all documented features actually work? (Cross-reference SKILL.md claims vs. script behavior)
- Error handling — does it return useful messages or crash?
- Output format — structured (JSON) or unstructured (raw text)?
- Shell scripts: shebang line present? `set -euo pipefail` for robustness?
- All script languages in `scripts/` reviewed, not just Python.

### 6. Separation of Concerns (weight: 1.0x)

Each skill should have a single, clear responsibility. Overloaded skills are
harder to trigger correctly and harder to maintain.

| Score | Criteria |
|-------|----------|
| 9-10 | Single clear responsibility. No feature creep. Easy to describe in one sentence. |
| 7-8 | Focused but with one or two secondary features that are closely related. |
| 5-6 | Trying to do two related things. Could arguably be split. |
| 3-4 | Clearly overloaded — doing multiple unrelated things. |
| 1-2 | Kitchen sink. No clear focus. |

**What to check:**
- Can you describe the skill's purpose in one sentence?
- Are all features serving the same core use case?
- Would splitting improve triggering accuracy?
- Are there features that belong in a different skill or a different layer (e.g., hooks)?

### 7. Generality (weight: 1.0x)

Skills should work across many prompts, not just the examples used during
development. Overfitting to test cases makes skills brittle.

| Score | Criteria |
|-------|----------|
| 9-10 | Handles wide input variety. Abbreviations, alternate phrasings. Limitations are documented. Graceful degradation for unsupported inputs. |
| 7-8 | Good coverage. A few gaps. Degradation is mostly graceful. |
| 5-6 | Works for common cases but brittle on variations. Undocumented gaps. |
| 3-4 | Only works for specific input patterns. Fails silently on variations. |
| 1-2 | Narrow to specific examples. Would break on real-world variety. |

**What to check:**
- Does it handle abbreviations, alternate phrasings, edge cases?
- Are limitations explicitly documented?
- Does it fail gracefully (error messages) or silently (wrong results)?
- Would it generalize to prompts beyond the test cases?

### 8. Writing Style (weight: 0.5x)

The style of the SKILL.md affects how well the model follows instructions.
Clear, imperative, well-structured prose produces better compliance.

| Score | Criteria |
|-------|----------|
| 9-10 | Imperative form. Scannable (tables, examples). Explains the "why." Natural, not robotic. |
| 7-8 | Mostly well-written. Good use of examples. Minor style issues. |
| 5-6 | Functional but flat. Heavy on prose, light on examples. |
| 3-4 | Disorganized. Hard to scan. Inconsistent style. |
| 1-2 | Confusing. Contradictory instructions. Walls of text. |

**What to check:**
- Imperative form ("Run the script") vs. passive ("The script should be run")?
- Tables and examples for dense information?
- Headings that serve as a scannable table of contents?
- Consistent formatting throughout?

## Computing the Overall Score

```
weighted_sum = (
    triggering * 1.5 +
    conciseness * 1.0 +
    why_explanation * 1.0 +
    progressive_disclosure * 1.0 +
    script_quality * 1.5 +
    separation_of_concerns * 1.0 +
    generality * 1.0 +
    writing_style * 0.5
)
overall = weighted_sum / 8.5
```

The heavier weights on triggering and script quality reflect that these are the
two most common failure modes: skills that don't activate when they should, and
scripts that produce wrong results.

## Review Output Format

Present the review as:

1. **Spec compliance** — pass/fail gate results (name, description, structure, references)
2. **Static analysis results** — output from scripts/analyze.py
3. **Dimension scores** — each dimension with score, evidence, and specific issues
4. **Overall score** — weighted average (provisional if spec gate has failures)
5. **Fix list** — concrete, prioritized changes ordered by impact

Organize fixes into:
- **Must fix** — spec violations, bugs, broken features, misleading documentation
- **Should fix** — dead code, missing edge cases, documentation gaps
- **Nice to have** — style improvements, additional coverage
