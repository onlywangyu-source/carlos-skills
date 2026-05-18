---
name: kms-ops
description: Read and write Confluence pages on the Fineres KMS (https://kms.fineres.com/). This skill should be used when the user asks to read, write, create, update, search, or delete KMS/Confluence pages, or when they mention operations on the KMS system. Trigger phrases include: KMS, Confluence, 读取KMS, 写入KMS, 创建KMS页面, 更新KMS页面, 搜索KMS, 查看KMS页面.
---

# KMS Operations

Read, write, search, and manage Confluence pages on the Fineres KMS system.

## Overview

This skill provides direct read/write access to the Fineres KMS (Confluence) via REST API.
All operations are authenticated with a built-in token — no additional credentials needed.

Base URL: `https://kms.fineres.com/rest/api`
Space: `support`

## Supported Operations

### 1. Read a page

Convert a Confluence page to Markdown by page ID.

- Read `scripts/kms_client.py` and use `get_page_body(page_id)`.
- Or execute: `python3 scripts/kms_client.py get <page_id>`

### 2. Create a page

Create a new Confluence page from Markdown content.

- Read `scripts/kms_client.py` and use `create_page(title, body_md, parent_id)`.
- Or execute: `python3 scripts/kms_client.py create "Title" --file body.md --parent <parent_id>`

### 3. Update a page

Update an existing page's title and/or body.

- Read `scripts/kms_client.py` and use `update_page(page_id, title, body_md)`.
- Or execute: `python3 scripts/kms_client.py update <page_id> --title "New Title" --file body.md`

### 4. Search pages

Search pages using Confluence Query Language (CQL).

- Read `scripts/kms_client.py` and use `search_pages(query)`.
- Or execute: `python3 scripts/kms_client.py search "title ~ 'keyword'"`

Common CQL patterns:
- `title ~ "keyword"` — fuzzy title search
- `text ~ "keyword"` — full-text search
- `space = support` — restrict to support space
- `type = page` — only pages

### 5. List child pages

List all child pages under a given page.

- Read `scripts/kms_client.py` and use `list_children(page_id)`.
- Or execute: `python3 scripts/kms_client.py children <page_id>`

### 6. Delete a page

Delete a page by ID.

- Read `scripts/kms_client.py` and use `delete_page(page_id)`.
- Or execute: `python3 scripts/kms_client.py delete <page_id>`

## Markdown ↔ Confluence Conversion

The bundled script `scripts/kms_client.py` handles bidirectional conversion:

- **Markdown → Confluence Storage XHTML**: headings, lists, tables, code blocks, bold/italic, links, blockquotes, horizontal rules.
- **Confluence Storage XHTML → Markdown**: best-effort extraction of readable Markdown.

When the user provides content in Markdown, always convert it via `md_to_confluence_storage()` before sending to the API.
When reading page content back for the user, always convert via `storage_to_md()` for readability.

## Workflow

1. Parse the user's intent (read / write / search / list / delete).
2. Identify the page by ID, title, or parent page as needed.
3. Load `scripts/kms_client.py` into context.
4. Call the appropriate Python function or execute the CLI command.
5. Report the result (title, page ID, URL, and content preview).

## Safety Notes

- Deletion is permanent. Confirm with the user before calling `delete_page`.
- When updating a page, fetch the current version number first (the script auto-handles this).
- Large tables or complex Confluence macros may not round-trip perfectly through Markdown conversion.
