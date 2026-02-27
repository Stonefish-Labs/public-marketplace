# IPA Guidelines For TTS (Offline)

## Purpose

Use this document as the default pronunciation reference for turning ordinary TTS scripts into selective IPA-enhanced scripts without internet access.

## Scope

Target accent baseline: General American English (GA), unless user specifies another accent.

## Core Decision Rule

Only replace a token with IPA if one of these is true:

1. The token is likely mispronounced by TTS.
2. The token has multiple common pronunciations and context picks one.
3. The token is a name, acronym, loanword, or technical term where incorrect pronunciation harms clarity.

If none apply, keep the original spelling.

## Conversion Workflow

1. Scan line for risky tokens.
2. Mark each token with risk type: `name`, `acronym`, `loanword`, `technical`, `ambiguous`.
3. Convert risky tokens to IPA.
4. Preserve punctuation, capitalization, and spacing.
5. Keep conversion consistent for repeated tokens.
6. Add low-confidence items to `Uncertain Items`.

## High-Value IPA Conventions (GA)

- Primary stress: `ˈ` before stressed syllable (`/ˈdætə/`).
- Secondary stress: `ˌ` if needed for long words.
- Rhotic `r`: GA is rhotic (`/ɑr/`, `/ɝ/`, `/ɚ/`).
- Schwa: use `/ə/` for unstressed reduced vowels.
- Syllabic consonants: common in natural speech (`/ˈbʌtn̩/` for "button").

## Common Phoneme Cheat Sheet (GA)

Vowels and diphthongs:

- FLEECE `/i/` as in "see"
- KIT `/ɪ/` as in "sit"
- DRESS `/ɛ/` as in "set"
- TRAP `/æ/` as in "cat"
- STRUT `/ʌ/` as in "cut"
- LOT `/ɑ/` as in "cot"
- THOUGHT `/ɔ/` as in "caught" (if distinguished)
- FOOT `/ʊ/` as in "book"
- GOOSE `/u/` as in "food"
- FACE `/eɪ/` as in "day"
- PRICE `/aɪ/` as in "my"
- CHOICE `/ɔɪ/` as in "boy"
- MOUTH `/aʊ/` as in "now"
- GOAT `/oʊ/` as in "go"
- NURSE `/ɝ/` stressed, `/ɚ/` unstressed

Common consonants:

- `/θ/` voiceless "th" (thin)
- `/ð/` voiced "th" (this)
- `/ʃ/` "sh"
- `/ʒ/` "zh" (measure)
- `/tʃ/` "ch"
- `/dʒ/` "j"
- `/ŋ/` "ng"
- `/ɹ/` English "r"

## Stress And Readability Rules

- Include stress markers for 2+ syllable replacements.
- Skip stress markers only for very obvious monosyllables.
- Prefer broad IPA over narrow allophonic detail to keep output maintainable.

## Acronyms And Initialisms

Use letter-by-letter IPA when spoken as letters:

- `AI` -> `/ˌeɪˈaɪ/`
- `SQL` (letter form) -> `/ˌɛsˌkjuːˈɛl/`
- `GPU` -> `/ˌdʒiːpiːˈjuː/`

If spoken as a word, use word pronunciation:

- `NASA` -> `/ˈnæsə/`
- `NATO` -> `/ˈneɪtoʊ/`

## Ambiguous Word Patterns

Prefer contextual disambiguation:

- `read` (present) `/riːd/`, (past) `/rɛd/`
- `live` (verb) `/lɪv/`, (adjective) `/laɪv/`
- `lead` (verb) `/liːd/`, (metal) `/lɛd/`
- `record` (noun) `/ˈrɛkɚd/`, (verb) `/rɪˈkɔrd/`
- `data` common GA variants `/ˈdeɪtə/` or `/ˈdætə/` (pick one consistently)

## Proper Nouns And Foreign Terms

- If confidence is high, convert directly.
- If confidence is medium or low, include best guess and flag in `Uncertain Items`.
- Keep repeated names identical across the script.
- Do not invent hyper-specific dialectal detail unless requested.

## Technical Terms (Default Preferences)

- `Linux` `/ˈlɪnəks/`
- `Git` `/ɡɪt/`
- `nginx` `/ˌɛnˈdʒɪnɛks/`
- `Kubernetes` `/ˌkuːbɚˈnɛtɪz/`
- `PostgreSQL` `/ˈpoʊstɡrɛˌɛsˌkjuːˈɛl/` (or user-preferred variant)

## Quality Bar

Good output:

- Replaces only risky terms.
- Keeps script meaning unchanged.
- Uses consistent IPA for repeated tokens.
- Includes reasons for each replacement.

Bad output:

- Converts every word to IPA.
- Mixes accents in one script without reason.
- Drops punctuation or formatting.
- Hides uncertainty instead of flagging it.

## Output Contract

Return three sections:

1. `Updated Script`
2. `Replacement Log` (Original | IPA | Reason)
3. `Uncertain Items` (if any)
