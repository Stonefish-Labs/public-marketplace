# Humanizer

Remove signs of AI-generated writing from text. Makes writing sound more natural and human-written using Wikipedia's "Signs of AI writing" guide.

**Source:** [biostartechnology/humanizer](https://clawhub.ai/biostartechnology/humanizer) on ClawHub

## Overview

This skill teaches an agent to identify and fix 24+ AI writing patterns: inflated symbolism, promotional language, superficial -ing analyses, vague attributions, em dash overuse, rule of three, AI vocabulary words, negative parallelisms, and more. It also guides adding voice and personality so text doesn't just avoid slop—it sounds like a human wrote it.

## Installation

Install via the agent marketplace CLI:

```bash
marketplace install humanizer
```

Or manually copy the `skills/humanizer/` folder into your agent's config directory.

## Usage

**Trigger phrases:** "humanize this text", "remove AI patterns", "make this sound more natural", "edit to sound human-written", "fix AI-sounding prose"

When invoked, the agent will:
1. Scan text for AI patterns (e.g., "serves as a testament", "pivotal role", em dash overuse)
2. Rewrite problematic sections while preserving meaning
3. Add voice and variation where appropriate
4. Return the humanized version with optional change summary

## License

MIT. Original skill by [biostartechnology](https://clawhub.ai/biostartechnology/humanizer).
