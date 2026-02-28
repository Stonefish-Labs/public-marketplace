---
description: Create a reverse brief from content with purpose, key points, risks, deadlines, actions, and open questions
argument-hint: [content-or-path-or-url]
---

# reverse-brief

## Task

Arguments: `$ARGUMENTS`

Create a reverse brief of the provided content for a non-expert reader.

## Workflow

1. Determine the content source from `$ARGUMENTS`:
   - If it is a local file path, read the file first.
   - If it is a URL, fetch it first.
   - If it is direct pasted content, use it as-is.
2. If no content is provided or retrievable, ask the user what content they want briefed.

## Output Format

Use this exact structure:

### 1. Purpose
Explain what the document is and why it exists in plain language. Avoid jargon.

### 2. Key Points
List the most important facts, decisions, or takeaways as bullet points, ordered by significance.

### 3. Risks & Concerns
Identify liabilities, caveats, gotchas, and anything likely to cause issues if missed.

### 4. Deadlines & Obligations
List all due dates, time-sensitive requirements, and responsibilities.
If none are present, explicitly state that no deadlines or obligations were identified.

### 5. Action Items
List concrete next actions with owner and timeline when available.

### 6. Open Questions
Call out ambiguous, missing, or unclear details that need clarification.

## Writing Rules

- Keep language clear, direct, and easy to scan.
- Write for someone who has not read the original content.
- Do not invent facts; use only what is in the provided source.
