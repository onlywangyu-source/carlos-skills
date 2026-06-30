# Publish Checklist

Use this before updating a live KMS / Confluence page or creating a child page.

## Pre-Publish Checks

| Check | Pass criteria |
|---|---|
| Target page | User has confirmed the page or parent page in this conversation |
| Credentials | No credential is stored in the skill, repo, memory, or prompt output |
| Version drift | Current live version was read or user accepted that live verification is unavailable |
| Scope | Draft changes match the user's requested sections |
| Sensitive content | No token, cookie, private key, signed URL, or unnecessary internal path |
| Data口径 | Metrics, dates, units, and status labels are consistent |
| Reversibility | Original content can be recovered from page history or local draft |

## Required User Confirmation

Before publishing, summarize:

- Target page label or parent label, without exposing sensitive URLs.
- Sections that will be changed or created.
- P0 risks, if any.
- Whether live version drift was checked.

Ask for explicit confirmation such as "确认发布" or "确认更新".

## Post-Publish Report

After publishing, report:

- Operation type: update or create.
- Page title.
- Changed sections.
- Any warnings, failed conversions, or manual follow-up needed.

Do not print credentials, auth headers, cookies, or full private URLs.
