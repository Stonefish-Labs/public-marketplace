---
name: tts-ipa-pronunciation
description: Review TTS scripts and replace pronunciation-sensitive words with IPA where needed to improve voice-model pronunciation while preserving script meaning and flow.
---

# TTS IPA Pronunciation

Use this skill when a user wants better pronunciation in text-to-speech output, especially for names, acronyms, uncommon words, or multilingual terms.

Use the local reference first: [references/ipa-guidelines.md](references/ipa-guidelines.md). Do not rely on internet lookups unless the user explicitly asks.

## What This Skill Does

1. Reviews a TTS script line by line.
2. Identifies words likely to be mispronounced by a voice model.
3. Replaces only those words with IPA.
4. Returns an updated script plus a replacement log for review.

## Workflow

### Step 1: Read Inputs

Collect:
- Original TTS script
- Target language/accent (if provided)
- Voice-model constraints (if provided)

If language or accent is missing, default to General American English.

### Step 2: Detect Pronunciation Risks

Prioritize likely failure cases:
- Proper nouns (people, places, brands)
- Acronyms and initialisms
- Loanwords or non-English names
- Domain-specific technical terms
- Words with known ambiguous pronunciation

### Step 3: Apply IPA Selectively

Replace only tokens that need disambiguation.

Rules:
- Do not rewrite sentence meaning.
- Do not over-convert common words.
- Preserve punctuation, capitalization, and line breaks.
- Keep replacements minimal and readable for downstream editing.
- Follow stress, schwa, rhotic, acronym, and proper-noun handling from [references/ipa-guidelines.md](references/ipa-guidelines.md).

### Step 4: Produce Output

Return:
1. `Updated Script` with selective IPA replacements
2. `Replacement Log` table:
   - Original token
   - IPA token
   - Reason for replacement
3. `Uncertain Items` list for any low-confidence mappings

## Output Template

Use [assets/output-template.md](assets/output-template.md).

## References

- [references/ipa-guidelines.md](references/ipa-guidelines.md)
