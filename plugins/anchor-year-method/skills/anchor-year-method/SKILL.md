---
name: anchor-year-method
description: Guide users through the Anchor Year Method to uncover rich autobiographical memories for legacy journals, memoirs, and personal history interviews.
metadata:
  version: 1.0.0
  category: writing
  tags: ["memory", "journaling", "memoir", "interviewing"]
---

# Anchor Year Method

Use this skill to help someone recall vivid personal memories by anchoring on one specific year and expanding outward through connected context.

Read `references/method-guide.md` for the full method background.
Read `assets/prompt-bank.md` for optional follow-up questions.

## When To Use

Use this when the user wants help with:

- Legacy journal creation
- Memoir or autobiographical writing
- Family history interviews
- Reflection and personal storytelling
- Recovering forgotten details from a life period

## Input

`$ARGUMENTS` may include:

- A specific anchor year (for example `1996`)
- A date range or life chapter (for example `high school years`)
- A project goal (for example `help me write stories for my grandchildren`)

If no year is provided, start by helping the user choose one.

## Example Invocation

```text
User input:
"Help me write memories for my family history book."

Assistant first turn:
"Great idea. Let's use the Anchor Year Method so this feels manageable and detailed.
To start, pick one anchor year from your past. It can be important or random.
If you'd like, I can suggest one based on a life chapter (school, first job, move, marriage, etc.)."
```

## Workflow

Guide the user through these stages in order.

1. Select an anchor year.
2. Rebuild world context for that year (news, culture, technology, fashion).
3. Rebuild personal context (age, location, school/work, family, daily rhythm).
4. Explore passions and emotionally significant events.
5. Build memory chains from one concrete detail to related memories.
6. Suggest external memory sources (photos, journals, family interviews).

## Facilitation Rules

1. Ask one focused question at a time unless the user asks for a full worksheet.
2. Prefer concrete prompts over abstract prompts.
3. Reflect back details the user shares and use those details to ask better follow-ups.
4. Never invent personal memories for the user.
5. If the user is uncertain, offer options and examples to reduce pressure.
6. Keep tone warm, non-judgmental, and patient.

## Output Format

When giving a structured response, use these sections:

```text
Anchor Year:
- ...

World Context:
- ...

Personal Snapshot:
- ...

Passions And Key Events:
- ...

Memory Chains:
- ...

Next Questions:
- ...
```

## Relational Memory Principle

Treat memory like a network: each recalled detail can unlock connected details. Use chain prompts such as:

- "What did that make you hope for next?"
- "Who else was there with you?"
- "What happened right before or right after that?"
- "What object, place, or sound do you associate with that moment?"

## Safety And Sensitivity

- If difficult memories surface, slow down and offer the user control over pace and depth.
- Do not pressure the user to continue with upsetting topics.
- If they want, pivot to neutral anchors (music, school routines, hobbies, holidays).
