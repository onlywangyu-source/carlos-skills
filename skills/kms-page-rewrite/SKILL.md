---
name: kms-page-rewrite
description: Use when restructuring, rewriting, comparing, or preparing updates for KMS or Confluence knowledge pages. This skill turns existing page content or user-provided drafts into cleaner page structures, produces a change-only diff for review, and requires explicit confirmation before any publish or update action.
---

# KMS Page Rewrite

Use this skill for KMS / Confluence page restructuring tasks: rewriting a page, creating a child-page outline, comparing old vs new content, or preparing a publish-ready Markdown draft.

This is a workflow skill, not a credential store. Do not put tokens, cookies, private links, page IDs, or internal page content into the skill.

## Core Rules

- Separate **drafting** from **publishing**.
- Default output is a reviewable Markdown draft plus a change summary.
- If the user says not to publish, still include the publish checklist, but do not ask for publish confirmation yet.
- Before updating a live page, get explicit user confirmation in the current conversation.
- If credentials or API access are needed, use the approved local runtime or connector; never ask to save credentials in the skill.
- When comparing a KMS page, output only the meaningful differences unless the user asks for a full rewrite.
- Preserve the user's intended conclusion unless the evidence contradicts it; call out contradictions instead of silently changing the argument.

## Workflow

1. **Clarify the operation**
   - Read existing page.
   - Rewrite / restructure.
   - Create child page.
   - Compare two versions.
   - Prepare update package.
   - Publish after confirmation.

2. **Gather source content**
   - Prefer structured page export or a connector/API read.
   - If live access is unavailable, ask the user for exported Markdown or copied content.
   - Do not rely on page IDs or URLs as durable memory.

3. **Diagnose the current page**
   - Identify page purpose, audience, decision needed, and current structure.
   - Mark P0/P1/P2 issues when useful.
   - Check data口径, ownership, timeline, and conclusion/evidence fit.

4. **Rewrite**
   - Use a structure that fits the page type.
   - Keep headings decision-oriented.
   - Use tables for options, status, owners, metrics, and action lists.
   - Keep operational detail collapsible or secondary when the target system supports it.

5. **Produce review output**
   - Summary of changes.
   - Change-only diff or section-level before/after.
   - Open questions and risky assumptions.
   - Publish checklist.

6. **Publish only after confirmation**
   - Re-read the current live version first if possible.
   - Check for version drift.
   - Confirm target page / parent page at a non-sensitive label level.
   - Report the result without exposing credentials.

## References

- For page patterns, read `references/rewrite-patterns.md`.
- Before any live update or child-page creation, read `references/publish-checklist.md`.

## Do Not Include

- KMS auth values, cookies, passwords, API keys, or authorization header values.
- Internal URLs, page IDs, or signed links.
- Customer data, personnel lists, or page exports.
- WorkBuddy raw scripts or caches.
- `.env`, `.pem`, `.key`, `.db`, `.sqlite`, logs, or compiled files.
