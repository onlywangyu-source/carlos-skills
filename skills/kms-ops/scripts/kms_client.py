#!/usr/bin/env python3
"""
KMS (Confluence) Read/Write Client
Supports: get page, create page, update page, search pages, list children.
"""

import argparse
import json
import os
import re
import sys
import html
import textwrap

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
# Fallback token for Fineres KMS (carlos)
TOKEN = os.environ.get("KMS_TOKEN")
if not TOKEN:
    raise RuntimeError("Environment variable KMS_TOKEN is required")
BASE_URL = "https://kms.fineres.com/rest/api"
SPACE_KEY = "support"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def api_get(path: str, params: dict = None):
    url = f"{BASE_URL}{path}"
    resp = requests.get(url, headers=HEADERS, params=params or {}, timeout=60)
    resp.raise_for_status()
    return resp.json()


def api_post(path: str, payload: dict):
    url = f"{BASE_URL}{path}"
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def api_put(path: str, payload: dict):
    url = f"{BASE_URL}{path}"
    resp = requests.put(url, headers=HEADERS, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def api_delete(path: str):
    url = f"{BASE_URL}{path}"
    resp = requests.delete(url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    return resp.json() if resp.text else {}


# ---------------------------------------------------------------------------
# Markdown -> Confluence Storage XHTML
# ---------------------------------------------------------------------------

def md_to_confluence_storage(md: str) -> str:
    """Convert Markdown to Confluence Storage XHTML."""
    lines = md.split("\n")
    result = []
    in_code_block = False
    code_lang = None
    in_table = False
    table_rows = []
    in_list = False
    list_type = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.startswith("```"):
            if in_code_block:
                result.append(f"</code></pre>")
                in_code_block = False
                code_lang = None
            else:
                lang = line[3:].strip()
                code_lang = lang
                attrs = ' class="language-' + lang + '"' if lang else ''
                result.append(f'<pre><code{attrs}>')
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            result.append(html.escape(line))
            i += 1
            continue

        # Empty line
        if line.strip() == "":
            if in_table:
                result.extend(_flush_table(table_rows))
                in_table = False
                table_rows = []
            if in_list:
                result.append(f"</{list_type}>")
                in_list = False
                list_type = None
            i += 1
            continue

        # Tables
        if "|" in line and not in_table and not line.startswith("#") and not line.startswith("-"):
            in_table = True
            table_rows = [line]
            i += 1
            continue
        elif in_table and "|" in line:
            table_rows.append(line)
            i += 1
            continue
        elif in_table:
            result.extend(_flush_table(table_rows))
            in_table = False
            table_rows = []
            continue

        # Headers
        if line.startswith("# "):
            result.append(f"<h1>{process_inline(line[2:])}</h1>")
            i += 1
            continue
        elif line.startswith("## "):
            result.append(f"<h2>{process_inline(line[3:])}</h2>")
            i += 1
            continue
        elif line.startswith("### "):
            result.append(f"<h3>{process_inline(line[4:])}</h3>")
            i += 1
            continue
        elif line.startswith("#### "):
            result.append(f"<h4>{process_inline(line[5:])}</h4>")
            i += 1
            continue

        # Lists
        ul_match = re.match(r"^\s*[-*+]\s+", line)
        ol_match = re.match(r"^\s*\d+\.\s+", line)
        if ul_match:
            if not in_list or list_type != "ul":
                if in_list:
                    result.append(f"</{list_type}>")
                result.append("<ul>")
                in_list = True
                list_type = "ul"
            content = re.sub(r"^\s*[-*+]\s+", "", line)
            result.append(f"<li>{process_inline(content)}</li>")
            i += 1
            continue
        elif ol_match:
            if not in_list or list_type != "ol":
                if in_list:
                    result.append(f"</{list_type}>")
                result.append("<ol>")
                in_list = True
                list_type = "ol"
            content = re.sub(r"^\s*\d+\.\s+", "", line)
            result.append(f"<li>{process_inline(content)}</li>")
            i += 1
            continue
        elif in_list and line.strip() != "":
            if line.startswith("  ") or line.startswith("\t"):
                result.append(f"<li>{process_inline(line.strip())}</li>")
                i += 1
                continue
            else:
                result.append(f"</{list_type}>")
                in_list = False
                list_type = None

        # Blockquote
        if line.startswith("> "):
            result.append(f"<blockquote>{process_inline(line[2:])}</blockquote>")
            i += 1
            continue

        # Horizontal rule
        if line.strip() == "---":
            result.append("<hr/>")
            i += 1
            continue

        # Regular paragraph
        result.append(f"<p>{process_inline(line)}</p>")
        i += 1

    # Close any open elements
    if in_list:
        result.append(f"</{list_type}>")
    if in_table and table_rows:
        result.extend(_flush_table(table_rows))

    return "\n".join(result)


def _flush_table(rows):
    out = ["<table>"]
    for j, row in enumerate(rows):
        # Skip separator rows
        if j == 1 and all("-" in c for c in row.split("|") if c.strip()):
            continue
        out.append("<tr>")
        cells = row.split("|")
        cells = [c.strip() for c in cells]
        cells = [c for c in cells if c or c == ""]
        tag = "th" if j == 0 else "td"
        for cell in cells:
            out.append(f"<{tag}>{process_inline(cell)}</{tag}>")
        out.append("</tr>")
    out.append("</table>")
    return out


def process_inline(text):
    """Process inline markdown formatting."""
    # Bold **text**
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic *text*
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Code `text`
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Links [text](url)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    # Escape HTML entities
    text = html.escape(text)
    # Unescape the HTML tags we just added
    text = text.replace("&lt;strong&gt;", "<strong>").replace("&lt;/strong&gt;", "</strong>")
    text = text.replace("&lt;em&gt;", "<em>").replace("&lt;/em&gt;", "</em>")
    text = text.replace("&lt;code&gt;", "<code>").replace("&lt;/code&gt;", "</code>")
    text = text.replace("&lt;a ", "<a ").replace("&lt;/a&gt;", "</a>")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    return text


# ---------------------------------------------------------------------------
# Confluence Storage XHTML -> Markdown
# ---------------------------------------------------------------------------

def storage_to_md(html_text: str) -> str:
    """Convert Confluence Storage XHTML back to Markdown (best-effort)."""
    text = html_text

    # Unescape common entities first
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

    # Structured macros (task list, info, etc.) – strip or simplify
    text = re.sub(r'<ac:structured-macro[^>]*>.*?</ac:structured-macro>', '', text, flags=re.DOTALL)
    # Plain macros
    text = re.sub(r'<ac:macro[^>]*>.*?</ac:macro>', '', text, flags=re.DOTALL)
    # Parameters
    text = re.sub(r'<ac:parameter[^>]*>.*?</ac:parameter>', '', text, flags=re.DOTALL)
    # Inline comments
    text = re.sub(r'<ac:inline-comment-marker[^>]*>', '', text)
    text = text.replace('</ac:inline-comment-marker>', '')

    # Images
    text = re.sub(
        r'<ac:image[^>]*>.*?<ri:attachment[^>]*ri:filename="([^"]+)"[^>]*/>.*?</ac:image>',
        r'![\1](\1)',
        text,
        flags=re.DOTALL
    )
    text = re.sub(
        r'<img[^>]+src="([^"]+)"[^>]*/?>',
        r'![image](\1)',
        text
    )

    # Pre / code
    text = re.sub(r'<pre>(.*?)</pre>', lambda m: f"```\n{m.group(1)}\n```", text, flags=re.DOTALL)
    text = re.sub(r'<code>(.*?)</code>', lambda m: f"`{m.group(1)}`", text, flags=re.DOTALL)

    # Tables
    def table_to_md(m):
        table_html = m.group(1)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, flags=re.DOTALL)
        md_rows = []
        for idx, row in enumerate(rows):
            cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, flags=re.DOTALL)
            md_cells = [strip_tags(c).strip() for c in cells]
            md_rows.append("| " + " | ".join(md_cells) + " |")
            if idx == 0:
                md_rows.append("| " + " | ".join(["---"] * len(md_cells)) + " |")
        return "\n".join(md_rows)

    text = re.sub(r'<table[^>]*>(.*?)</table>', table_to_md, text, flags=re.DOTALL)

    # Lists
    text = re.sub(r'</?ul[^>]*>', '', text)
    text = re.sub(r'</?ol[^>]*>', '', text)
    text = re.sub(r'<li[^>]*>', '- ', text)
    text = text.replace('</li>', '')

    # Headings
    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', text, flags=re.DOTALL)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', text, flags=re.DOTALL)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', text, flags=re.DOTALL)
    text = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', text, flags=re.DOTALL)
    text = re.sub(r'<h5[^>]*>(.*?)</h5>', r'##### \1', text, flags=re.DOTALL)
    text = re.sub(r'<h6[^>]*>(.*?)</h6>', r'###### \1', text, flags=re.DOTALL)

    # Blockquote
    text = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', lambda m: "> " + m.group(1).replace("\n", "\n> "), text, flags=re.DOTALL)

    # Bold / italic
    text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', text, flags=re.DOTALL)
    text = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', text, flags=re.DOTALL)

    # Paragraphs
    text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', text, flags=re.DOTALL)

    # Horizontal rule
    text = re.sub(r'<hr[^>]*/?>', '---', text)

    # Links
    text = re.sub(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.DOTALL)

    # Line breaks
    text = text.replace('<br/>', '\n').replace('<br>', '\n')

    # Strip remaining tags
    text = strip_tags(text)

    # Clean up multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def strip_tags(html_text):
    """Remove all HTML tags."""
    return re.sub(r'<[^>]+>', '', html_text)


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------

def get_page(page_id: str, expand: str = "body.storage,ancestors,space"):
    """Read a Confluence page by ID. Returns page dict."""
    return api_get(f"/content/{page_id}", params={"expand": expand})


def get_page_body(page_id: str) -> str:
    """Return the page body as Markdown."""
    page = get_page(page_id, expand="body.storage")
    storage = page.get("body", {}).get("storage", {}).get("value", "")
    return storage_to_md(storage)


def create_page(title: str, body_md: str, parent_id: str = None, space_key: str = SPACE_KEY):
    """Create a new Confluence page. Returns created page dict."""
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {
            "storage": {
                "value": md_to_confluence_storage(body_md),
                "representation": "storage",
            }
        },
    }
    if parent_id:
        payload["ancestors"] = [{"id": parent_id}]
    return api_post("/content", payload)


def update_page(page_id: str, title: str, body_md: str, version: int = None):
    """Update an existing Confluence page. Returns updated page dict."""
    # Need current version if not provided
    if version is None:
        current = get_page(page_id, expand="version")
        version = current.get("version", {}).get("number", 1)
    payload = {
        "type": "page",
        "title": title,
        "body": {
            "storage": {
                "value": md_to_confluence_storage(body_md),
                "representation": "storage",
            }
        },
        "version": {"number": version + 1},
    }
    return api_put(f"/content/{page_id}", payload)


def search_pages(query: str, limit: int = 25):
    """CQL search for pages. Returns list of page dicts."""
    data = api_get("/content/search", params={"cql": query, "limit": limit, "expand": "space"})
    return data.get("results", [])


def list_children(page_id: str, limit: int = 50):
    """List child pages. Returns list of page dicts."""
    data = api_get(f"/content/{page_id}/child/page", params={"limit": limit, "expand": "space"})
    return data.get("results", [])


def delete_page(page_id: str):
    """Delete a page."""
    return api_delete(f"/content/{page_id}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="KMS Confluence CLI")
    sub = parser.add_subparsers(dest="cmd")

    # get
    p_get = sub.add_parser("get", help="Get page content by ID")
    p_get.add_argument("page_id", help="Confluence page ID")
    p_get.add_argument("--raw", action="store_true", help="Print raw storage HTML instead of Markdown")

    # create
    p_create = sub.add_parser("create", help="Create a new page")
    p_create.add_argument("title", help="Page title")
    p_create.add_argument("--file", "-f", help="Markdown file path for body")
    p_create.add_argument("--body", "-b", help="Markdown body string")
    p_create.add_argument("--parent", "-p", help="Parent page ID")
    p_create.add_argument("--space", "-s", default=SPACE_KEY, help="Space key")

    # update
    p_update = sub.add_parser("update", help="Update an existing page")
    p_update.add_argument("page_id", help="Page ID to update")
    p_update.add_argument("--title", "-t", help="New title")
    p_update.add_argument("--file", "-f", help="Markdown file path for new body")
    p_update.add_argument("--body", "-b", help="Markdown body string")

    # search
    p_search = sub.add_parser("search", help="Search pages with CQL")
    p_search.add_argument("query", help="CQL query string")
    p_search.add_argument("--limit", "-l", type=int, default=25)

    # children
    p_children = sub.add_parser("children", help="List child pages")
    p_children.add_argument("page_id", help="Parent page ID")
    p_children.add_argument("--limit", "-l", type=int, default=50)

    # delete
    p_del = sub.add_parser("delete", help="Delete a page")
    p_del.add_argument("page_id", help="Page ID to delete")

    args = parser.parse_args()

    if args.cmd == "get":
        page = get_page(args.page_id)
        title = page.get("title", "")
        url = f"https://kms.fineres.com/pages/viewpage.action?pageId={args.page_id}"
        if args.raw:
            storage = page.get("body", {}).get("storage", {}).get("value", "")
            print(f"# {title}\nURL: {url}\n\n{storage}")
        else:
            md = get_page_body(args.page_id)
            print(f"# {title}\nURL: {url}\n\n{md}")

    elif args.cmd == "create":
        body = ""
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                body = f.read()
        elif args.body:
            body = args.body
        result = create_page(args.title, body, parent_id=args.parent, space_key=args.space)
        pid = result.get("id")
        print(f"Created page: {result.get('title')}")
        print(f"Page ID: {pid}")
        print(f"URL: https://kms.fineres.com/pages/viewpage.action?pageId={pid}")

    elif args.cmd == "update":
        page = get_page(args.page_id)
        title = args.title or page.get("title", "")
        body = ""
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                body = f.read()
        elif args.body:
            body = args.body
        else:
            body = get_page_body(args.page_id)
        result = update_page(args.page_id, title, body)
        pid = result.get("id")
        print(f"Updated page: {result.get('title')}")
        print(f"Page ID: {pid}")
        print(f"URL: https://kms.fineres.com/pages/viewpage.action?pageId={pid}")

    elif args.cmd == "search":
        results = search_pages(args.query, limit=args.limit)
        for r in results:
            pid = r.get("id")
            space = r.get("space", {}).get("key", "")
            print(f"{r.get('title')} | ID:{pid} | Space:{space}")

    elif args.cmd == "children":
        results = list_children(args.page_id, limit=args.limit)
        for r in results:
            pid = r.get("id")
            print(f"{r.get('title')} | ID:{pid}")

    elif args.cmd == "delete":
        delete_page(args.page_id)
        print(f"Deleted page {args.page_id}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
