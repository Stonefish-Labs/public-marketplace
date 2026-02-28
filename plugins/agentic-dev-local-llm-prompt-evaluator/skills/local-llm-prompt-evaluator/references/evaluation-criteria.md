# Evaluation Criteria — Local LLM Prompt Fitness

Reference rubric for scoring prompts against the 7 dimensions. Each dimension has a 1–5 scale, specific failure signals, and local LLM-specific failure mode examples.

---

## 1. Specificity & Clarity (weight: 1.5x)

**What it measures**: Whether the prompt states its intent precisely enough that a fixed-weight model with limited inference capability can comply without guessing.

| Score | Criteria |
|---|---|
| 5 | Every instruction has a measurable or observable success state. No ambiguous verbs. |
| 4 | Mostly specific; one or two terms could be interpreted multiple ways. |
| 3 | Core intent is clear but key constraints are missing (length, scope, audience). |
| 2 | Relies on the model to define "good", "better", "readable", "interesting". |
| 1 | Entirely open-ended. Could produce any output and satisfy the prompt literally. |

**Fail signals to look for:**
- `make this better` / `improve this` — better how? By what measure?
- `write something about X` — length, audience, format, tone undefined
- `fix this` — what counts as fixed?
- `summarize` with no length or depth guidance
- `what do you think?` — no action defined

**Local LLM failure mode**: Cloud models infer "better" from context and prior conversation. A local model at 7B–13B will output a minor paraphrase and stop, having technically satisfied the literal request.

**Remediation pattern**:
```
# Bad
Can you make this email better?

# Good
Rewrite the email below to be more direct and professional.
Constraints:
- Keep it under 150 words
- Remove filler phrases like "I hope this finds you well"
- Preserve all factual content
- Audience: B2B client, decision-maker level
```

---

## 2. Structure & Delimiters (weight: 1.0x)

**What it measures**: Whether multi-step or multi-section prompts are organized so the model can parse instruction boundaries without ambiguity.

| Score | Criteria |
|---|---|
| 5 | All tasks numbered or bulleted. Distinct delimiters used for context, instructions, and input. Consistent throughout. |
| 4 | Most tasks structured; minor inconsistency in delimiter use. |
| 3 | Some structure present but instructions and context bleed together. |
| 2 | Paragraph prose with no step separation; model must infer task order. |
| 1 | Wall of text. No structural signals whatsoever. |

**Fail signals to look for:**
- Multi-step tasks written as a single run-on sentence
- Same delimiter (`---`) used for both context sections and actionable instructions
- Instructions embedded inside example blocks
- No separation between "here is background" and "here is what to do"

**Local LLM failure mode**: Smaller models lose track of instruction boundaries mid-prompt. They will often execute only the last clear instruction in a paragraph, or conflate context with instructions.

**Remediation pattern**:
```
# Bad
Summarize these notes and give me an outline with sections for characters, plot, and setting.

# Good
### Task
1. Summarize the notes below in 3–5 bullet points.
2. Create an outline with three sections: Characters, Plot, Setting.

---
### Notes
[notes pasted here]
```

---

## 3. Output Format Spec (weight: 1.5x)

**What it measures**: Whether the prompt defines exactly what the output should look like — structure, length, schema, and content boundaries.

| Score | Criteria |
|---|---|
| 5 | Format, length, and schema fully specified. Example output structure provided. Edge cases handled ("if none found, return empty list"). |
| 4 | Format specified; minor gaps (e.g., length range not defined). |
| 3 | Format partially defined (e.g., "use bullet points" but no count or nesting guidance). |
| 2 | Format implied but not stated (model must infer from examples). |
| 1 | No output format guidance. Model decides everything. |

**Fail signals to look for:**
- No mention of output format at all
- "Return a list" with no count, nesting, or key names
- JSON requested but no schema or field names given
- "Summarize" with no target length
- Format defined in the system prompt but contradicted in the user prompt

**Local LLM failure mode**: Without format guidance, local models will often match the format of the input. If input is prose, output will be prose. If you need JSON, you must say JSON explicitly with a schema — local models will not infer it from context the way GPT-4 might.

**Remediation pattern**:
```
# Bad
Extract the key information from the text below.

# Good
Extract the following fields from the text below and return them as JSON.
Schema:
{
  "company_name": string,
  "founding_year": integer or null,
  "headquarters": string or null,
  "product_category": string
}
If a field is not mentioned, return null for that field.
```

---

## 4. Role & Context (weight: 1.0x)

**What it measures**: Whether the prompt establishes who the model is, what it knows, and what situational context is relevant.

| Score | Criteria |
|---|---|
| 5 | System prompt defines role, expertise level, and behavioral constraints. Relevant background context provided in the user prompt. |
| 4 | Role defined; minor context gaps. |
| 3 | Implicit role (task implies expertise) but no explicit system prompt or context. |
| 2 | No role or context. Model must guess its stance and expertise level. |
| 1 | No role, no context, and the task requires domain knowledge not present in the prompt. |

**Fail signals to look for:**
- No system prompt at all for a task requiring consistent tone/behavior
- Role defined in the user prompt instead of system prompt
- Background context that the model would need to complete the task is missing
- Asking for expert-level output without establishing the model's expertise

**Local LLM failure mode**: Without an explicit role, local models default to a generic "helpful assistant" stance. This produces bland, hedged output. For domain-specific tasks (medical, legal, technical writing), the absence of a role anchor is particularly damaging at smaller parameter counts.

**Remediation pattern**:
```
# Bad (no system prompt, task dropped directly)
User: Analyze the following code for security vulnerabilities.

# Good
System: You are a senior application security engineer. Your reviews are precise, technical, and prioritized by exploitability. You do not hedge or offer generic advice — you identify specific CWEs and provide concrete remediation steps.

User: Analyze the following Python code for security vulnerabilities.
[code here]
```

---

## 5. Inference Burden (weight: 1.5x)

**What it measures**: How much the model is expected to infer, assume, or fill in — things not stated in the prompt.

| Score | Criteria |
|---|---|
| 5 | Nothing requires inference. All gaps are explicitly handled. Edge cases addressed. |
| 4 | One or two minor inferences required; unlikely to cause failure. |
| 3 | Model must make a judgment call on scope, tone, or format. |
| 2 | Core task requires inferring the user's definition of success. |
| 1 | Prompt is a fragment. Model must reconstruct intent entirely. |

**Fail signals to look for:**
- Implicit audience ("write a blog post" — for whom?)
- Implicit tone ("professional" means different things at 7B vs 70B)
- Missing edge case handling ("what if the list is empty?")
- Half-baked input: "here are some notes, do something useful with them"
- Phrases like "you know what I mean" or "use your judgment"

**Local LLM failure mode**: Cloud models use RLHF and system-level inference to bridge intent gaps. Local models take the literal path of least resistance. High inference burden is the single most common reason local LLM outputs disappoint users who are used to ChatGPT.

**Remediation pattern**:
```
# Bad
Convert these notes into something readable.

# Good
Rewrite the notes below as a structured meeting summary.
Format:
- **Date**: [extracted from notes or "Not specified"]
- **Attendees**: [bullet list]
- **Decisions Made**: [bullet list, action-verb framing]
- **Open Items**: [bullet list with owner if mentioned]
Tone: professional, third-person. Target length: 200–300 words.
```

---

## 6. Few-Shot Examples (weight: 1.0x)

**What it measures**: Whether the prompt provides input/output examples in cases where the output shape, tone, or transformation is non-obvious.

| Score | Criteria |
|---|---|
| 5 | 2–3 well-chosen examples that cover the common case and at least one edge case. Examples are consistent with instructions. |
| 4 | One good example. Covers common case; edge cases not shown. |
| 3 | Examples present but inconsistent with instructions, or only trivial cases shown. |
| 2 | No examples, but the task involves a non-obvious transformation or classification. |
| 1 | No examples and the output format is completely undemonstrated. |

**Fail signals to look for:**
- Classification tasks with no label examples
- Tone-transformation tasks with no target-tone sample
- Structured extraction with no example of desired output structure
- Examples that contradict the format instructions

**When few-shot examples are NOT needed**: Simple factual queries, straightforward summarizations with full format specs, and tasks where the output is unambiguous (e.g., "translate this to Spanish").

**Local LLM failure mode**: Local models with fewer parameters have weaker zero-shot generalization. An example is worth several sentences of instruction for a 7B model — it anchors the output format and tone more reliably than prose description.

**Remediation pattern**:
```
# Bad (classification, no examples)
Classify the sentiment of the following review as Positive, Negative, or Neutral.
Review: [text]

# Good
Classify the sentiment of the review as Positive, Negative, or Neutral.

Examples:
Review: "The product broke after two days."
Sentiment: Negative

Review: "Shipping was fast and the item matches the description."
Sentiment: Positive

Review: "It arrived on time. Nothing special."
Sentiment: Neutral

---
Review: [text]
Sentiment:
```

---

## 7. Token Efficiency (weight: 0.5x)

**What it measures**: Whether the prompt wastes tokens on redundant instructions, contradictions, or filler that increases context load without improving output.

| Score | Criteria |
|---|---|
| 5 | Every sentence earns its place. No redundancy between sections. No filler preamble. |
| 4 | Mostly lean; one or two sentences could be cut without loss. |
| 3 | Some redundancy; instructions repeated across system and user prompts. |
| 2 | Significant bloat — multiple paragraphs restating the same constraint. |
| 1 | Contradictions present, or the prompt is so long it likely exceeds the effective attention span of a small model. |

**Fail signals to look for:**
- "Please" / "thank you" / "I would appreciate it if you could" — filler that costs tokens
- Same instruction stated twice in different sections
- A system prompt and user prompt that both define the role differently
- Long preambles explaining what the task is before actually stating the task
- Context window warnings: prompt length approaching or exceeding model's practical attention window

**Local LLM failure mode**: Long prompts with redundant or contradictory instructions cause small models to selectively ignore sections. The model doesn't "average" conflicting instructions — it picks one and drops the other, usually the earlier one.

**Note on context window size**: If a prompt is approaching 2K tokens for a 4K-context model, flag this as a Warning. The model needs context budget for its output. Rule of thumb: prompt should use no more than 60–70% of the context window.

---

## Weighted Score Formula

```
weighted_sum = (
    specificity_clarity    * 1.5 +
    structure_delimiters   * 1.0 +
    output_format_spec     * 1.5 +
    role_context           * 1.0 +
    inference_burden       * 1.5 +
    few_shot_examples      * 1.0 +
    token_efficiency       * 0.5
)
overall = weighted_sum / 9.0
```

| Overall Score | Verdict |
|---|---|
| 4.5–5.0 | **Fit** — well-structured for local LLM use |
| 3.5–4.4 | **Needs Work** — functional but likely to produce inconsistent results |
| 2.5–3.4 | **High Risk** — significant ambiguity; local model will likely underperform |
| < 2.5 | **Not Fit** — requires substantial rewrite before local LLM use |

---

## Special Considerations by Model Size

| Parameter Range | Tolerance for Ambiguity | Notes |
|---|---|---|
| ≤ 7B | Very low | Apply strictest standards. Almost no zero-shot inference. Requires examples for any non-trivial output shape. |
| 8B–13B | Low | Can handle light inference but still literal. Format spec and examples strongly recommended. |
| 14B–34B | Moderate | Closer to cloud model behavior but still benefits heavily from structure. |
| 35B–70B | Higher | Approaches cloud model capability. Vague prompts have a better chance but still degrade quality. |
| 70B+ (quantized) | Similar to small cloud models | Still benefits from structure; quantization may reintroduce some 13B-level limitations. |
