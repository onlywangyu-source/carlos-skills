---
name: ppt-case-review
description: Use when reviewing customer success, CSM, technical support, or business case PowerPoint decks. Extract slide content, evaluate from Carlos's CSM and management perspective, classify issues as P0/P1/P2, compare multiple cases, and produce a structured review report with scores, highlights, reusable playbook insights, and page-level fixes.
---

# PPT Case Review

Use this skill to review customer success case decks, business review decks, CSM methodology decks, or technical support case presentations. The goal is a precise, page-level review that balances criticism with reusable value extraction.

## Review Lens

Review from Carlos's role perspective:

- Customer success / technical support management.
- Commercial closure: renewal, expansion, NRR, customer value realization.
- Methodology reuse: can this become a playbook, benchmark case, or regional enablement asset?
- Two-score model: distinguish **case sharing quality** from **management reporting quality**.

Do not only check wording. Look for business logic, data口径, narrative completeness, reusable frameworks, and whether the deck can become a benchmark.

## Workflow

1. **Extract content**
   - Use `python-pptx` or an equivalent structured parser.
   - Extract slide text, notes, page numbers, and visible structure.
   - If visual layout matters, inspect rendered slides or screenshots when available.

2. **Review each slide**
   Check three dimensions:
   - Data accuracy: metric consistency, units, traceability, calculation logic.
   - Logic rigor: timeline, cause and effect, concept accuracy, evidence chain.
   - Narrative completeness: background, conflict, solution, results, attribution.

3. **Classify issues**
   - P0: must fix before external use. Data error, logic hard failure, typo that changes meaning, compliance or factual risk.
   - P1: should fix. Inconsistent口径, missing evidence, weak structure, unclear page role.
   - P2: optional improvement. Sharper wording, visual polish, extra context, stronger examples.

4. **Extract value**
   Every review should identify:
   - 2-3 unique strengths.
   - 1-2 reusable methods, frameworks, concepts, or playbook assets.
   - One memorable sentence or concept if the deck contains one.

5. **Score separately**
   - Case sharing quality: audience learning, story, scenario specificity, transferability.
   - Management reporting quality: business closure, data rigor, decision usefulness, strategic altitude.

6. **Compare when multiple decks are involved**
   Compare by narrative structure, methodology depth, quantified evidence, scenario granularity, commercial closure, and strategic altitude.

## Output

Use the report template in `references/report-template.md`. Keep findings page-specific. If a deck has no P0 issues, say that clearly.

For reusable evaluation dimensions and examples, read `references/review-rubric.md` when a review needs more consistency or when comparing multiple decks.

## Guardrails

- Do not invent slide content that was not extracted or visually inspected.
- If a metric appears inconsistent, cite the exact slide numbers involved.
- Separate “case sharing” score from “management reporting” score.
- Give strengths and fix suggestions together; do not produce only criticism.
- Treat data口径 problems as high priority because they can reverse the conclusion.
- If the user asks to publish or update a KMS page, stop at the review unless they explicitly confirm publication.
