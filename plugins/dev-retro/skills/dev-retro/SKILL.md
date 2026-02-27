---
name: dev-retro
description: Extract a structured retrospective from chat history, project session history, planning files, or specified files/folders. Analyzes what happened during a development session and produces an actionable retro document.
argument-hint: [source - file path, folder, "session", or "chat"]
---

# Retrospective Extractor

Generate a structured retrospective from development work by analyzing chat histories, planning documents, session logs, or any specified project files.

## Input

`$ARGUMENTS` specifies what to analyze. It can be:

- **A file path** - analyze a specific file (chat export, planning doc, markdown notes, etc.)
- **A folder path** - recursively read all `.md`, `.plan.md`, and text files in the folder
- **`session`** or **`sessions`** - analyze the Claude Code session history for this project (from `~/.claude/projects/` matching the current working directory)
- **`chat`** - analyze the current conversation history (everything above this invocation)
- **Nothing / empty** - ask the user what they want to retrospect on

Multiple sources can be comma-separated: `/retro content/, session`

## Steps

1. **Identify sources** - Parse `$ARGUMENTS` to determine what to read. If empty or ambiguous, ask the user.

2. **Gather material** - Read all specified sources:
   - For file paths: read the file directly
   - For folder paths: glob for `**/*.md`, `**/*.plan.md`, `**/*.txt` and read each
   - For `session`: find the project session directory under `~/.claude/projects/` that corresponds to the current working directory (directory name is the path with `-` replacing `/`), then read the session files (JSONL format - extract user messages and assistant messages)
   - For `chat`: work from the conversation context already available

3. **Analyze the work** - Read through all gathered material and extract:
   - The original goal or problem statement
   - What tasks were attempted and their outcomes
   - Decision points, corrections, and back-and-forth
   - Errors, stumbling blocks, and dead ends
   - What was left unfinished or explicitly dropped
   - Patterns that worked well vs. patterns that caused friction

4. **Generate the retrospective** - Fill in the template from `references/retro-template.md` using the analysis. Every section must be populated - use "None identified" if a section genuinely has no content, but look hard before concluding that.

5. **Output the retrospective** - Present the completed retrospective to the user as markdown. Then ask if they want to:
   - Save it to a file (suggest `retro-YYYY-MM-DD-<slug>.md` in the project root or a `retros/` folder)
   - Adjust or expand any section
   - Generate a follow-up plan or skill from the suggestions

## Analysis Guidelines

When extracting the retrospective, follow these principles:

### Goal Extraction
- Look for the first user message or problem statement - that's usually the goal
- If there were goal changes mid-session, note both the original and revised goals
- Planning docs with `overview` or `name` frontmatter fields often state the goal concisely

### What Got Done
- Track each discrete task/change that was completed
- Note file paths and specific changes where available
- Reference plan todo items and their final status if a `.plan.md` was involved

### What Went Right
- Identify smooth sequences where work flowed without corrections
- Note good decisions the agent or user made proactively
- Highlight any patterns that saved time (e.g., reading before editing, checking existing code first)

### What Went Wrong
- Look for errors, failed attempts, and incorrect assumptions
- Identify misunderstandings between user intent and agent action
- Note any rework or wasted effort

### Agent Stumbling Blocks
- Specifically isolate moments where the agent made mistakes the user had to correct
- Categorize: wrong assumption, missed context, hallucinated API, wrong tool choice, etc.
- Note the correction pattern - how was the mistake caught and fixed?

### Communication Friction
This section is specifically coaching for the user - not blame, but a mirror. Look for moments where:
- A user message was ambiguous and the agent made a reasonable but wrong interpretation
- The user gave incomplete context that would have been easy to include (e.g., "the other files are also wrong" vs. just "fix this one")
- A correction came *after* the agent had already committed to a wrong direction, when earlier phrasing could have prevented it
- The user assumed the agent had context it didn't have (domain knowledge, awareness of other files, intent behind a request)
- A vague instruction ("fix it," "make it better") left the agent guessing at scope or approach

For each friction point, produce three things:
1. **What was said** - the actual user message (or paraphrase)
2. **How it likely landed** - the reasonable interpretation an agent would make
3. **Sharper version** - a concrete rewrite of what the user could say next time to get the right result immediately

Keep the tone neutral and instructive - this is a personal coaching tool, not a critique. The goal is to help the user build better communication habits with AI agents.

### What Was Abandoned
- Tasks that were started but not finished
- Approaches that were tried then switched away from
- Features or changes that were discussed but explicitly dropped

### Open Questions
- Unresolved technical decisions
- Things the user flagged for future work
- Inconsistencies discovered but not addressed

### Suggested Skills
This is the most actionable section. Based on the patterns observed, suggest:
- **Reusable skills** - workflows that could be templated for similar future work
- **Guard-rail skills** - checks or validations that would have caught mistakes earlier
- **Reference materials** - docs or context that would have prevented wrong assumptions
- Format each suggestion as: `skill-name` - one-line description of what it would do

## Handling Different Source Formats

### Chat Exports (Cursor, Claude, etc.)
- Look for `**User**` / `**Assistant**` or `**Cursor**` delimiters
- Extract the conversational flow: requests, responses, corrections

### Planning Documents (.plan.md)
- Parse YAML frontmatter for `name`, `overview`, `todos`
- Use todo statuses (completed/pending/in_progress) to determine what got done vs. abandoned
- The markdown body often contains the technical specification

### Session JSONL Files
- Each line is a JSON object with `role` and `content` fields
- Focus on user messages (intent) and assistant tool calls / responses (execution)
- Session files can be large - prioritize the most recent session if multiple exist

### Raw Files / Folders
- Treat as reference material supporting the retrospective
- Cross-reference with chat/session data when available

## Output Format

Use the template in `references/retro-template.md` exactly. The output should be a single markdown document that stands alone - someone reading it without access to the source material should understand what happened and what to do next.
