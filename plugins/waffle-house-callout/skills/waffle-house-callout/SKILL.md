---
name: waffle-house-callout
description: Turn any user request into a ridiculous Waffle House-style Pull Drop Mark callout. Use this when someone asks to "waffle-house-ify" something, convert a topic into pull/drop/mark format, or wants a funny short-order remix.
metadata:
  version: 1.0.0
  category: fun
  tags: ["humor", "prompt-formatting", "waffle-house"]
---

# Waffle House Callout

Convert any input into a playful kitchen call using three sections: `Pull`, `Drop`, and `Mark`.

Read `references/pull-drop-mark-cheatsheet.md` for mapping rules.
Read `assets/voice-style.md` for tone and phrasing.

## Input

`$ARGUMENTS` is the thing to convert. It can be concrete (a sandwich, a video game, a bug ticket) or abstract (an emotion, a life plan, a startup pitch).

If `$ARGUMENTS` is empty, infer the target from the latest user message.

## Output Format

Always output exactly these headers and keep each section non-empty:

```text
Pull:
- ...

Drop:
- ...

Mark:
- ...
```

## Rules

1. Map the input into kitchen logic, not literal recipes.
   - `Pull`: core components, heavy hitters, main "protein" ideas.
   - `Drop`: base/staging layer, quantity, placement, heat/tempo.
   - `Mark`: detailed modifiers, special handling, vibe, finish.
2. Keep it funny but readable. Aim for punchy short-order cadence.
3. Respect user constraints (for example: vegan, chaotic, formal, PG).
4. Do not invent unsafe or hateful content. Keep humor light and non-abusive.
5. If the input is vague, choose the funniest reasonable interpretation and proceed.
6. Prefer 2-5 bullets per section unless the user asks for a longer call.

## Style

- Use imperative kitchen verbs: "Pull", "Drop", "Mark", "Fire", "Hold".
- Use quick modifier phrases: "scattered", "in the ring", "all the way", "extra loud".
- Keep each bullet short; one move per line.

## Examples

### Example 1

Input: "My Monday morning routine"

Output:

```text
Pull:
- Pull one double-shot ambition and one travel mug of denial.

Drop:
- Drop one hashbrown of calendar chaos, scattered well.

Mark:
- Mark with two alarms, hold snooze, add panic at 8:42.
- Mark coffee dark, motivation light, send it all the way.
```

### Example 2

Input: "A SaaS onboarding flow"

Output:

```text
Pull:
- Pull one welcome email, one product tour, one trial timer.

Drop:
- Drop one user journey in the ring, scattered with tooltips.

Mark:
- Mark step one friction light, value reveal heavy.
- Mark with progress bar, hold jargon, add one celebratory checkmark.
```
