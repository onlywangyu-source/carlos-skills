#!/usr/bin/env python3
"""
KMS Content Collector for Avatar Training (Optimized)
批量获取指定用户创建的KMS内容，用于分身训练。
策略：优先获取评论和原创页面，跳过纯附件。
"""

import json
import os
import sys
import re
from datetime import datetime, timezone

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TOKEN = os.getenv("KMS_TOKEN", "YOUR_KMS_TOKEN_HERE")
BASE_URL = "https://kms.fineres.com/rest/api"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# ---------------------------------------------------------------------------
# API Helpers
# ---------------------------------------------------------------------------

def api_get(path: str, params: dict = None):
    url = f"{BASE_URL}{path}"
    resp = requests.get(url, headers=HEADERS, params=params or {}, timeout=60)
    resp.raise_for_status()
    return resp.json()


def search_all(query: str, expand: str = "history"):
    """Search all results with pagination."""
    all_results = []
    start = 0
    limit = 50
    while True:
        data = api_get("/content/search", params={
            "cql": query,
            "start": start,
            "limit": limit,
            "expand": expand
        })
        results = data.get("results", [])
        if not results:
            break
        all_results.extend(results)
        if len(results) < limit:
            break
        start += limit
    return all_results


def get_page_body(page_id: str) -> str:
    """Get page body as markdown."""
    page = api_get(f"/content/{page_id}", params={"expand": "body.storage"})
    storage = page.get("body", {}).get("storage", {}).get("value", "")
    return storage_to_md(storage) if storage else ""


# ---------------------------------------------------------------------------
# Storage to Markdown
# ---------------------------------------------------------------------------

def storage_to_md(html_text: str) -> str:
    text = html_text
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    text = re.sub(r'<ac:structured-macro[^>]*>.*?</ac:structured-macro>', '', text, flags=re.DOTALL)
    text = re.sub(r'<ac:macro[^>]*>.*?</ac:macro>', '', text, flags=re.DOTALL)
    text = re.sub(r'<ac:parameter[^>]*>.*?</ac:parameter>', '', text, flags=re.DOTALL)
    text = re.sub(r'<ac:inline-comment-marker[^>]*>', '', text)
    text = text.replace('</ac:inline-comment-marker>', '')
    text = re.sub(r'<ac:image[^>]*>.*?<ri:attachment[^>]*ri:filename="([^"]+)"[^>]*/>.*?</ac:image>', r'![\1](\1)', text, flags=re.DOTALL)
    text = re.sub(r'<img[^>]+src="([^"]+)"[^>]*/?>', r'![image](\1)', text)
    text = re.sub(r'<pre>(.*?)</pre>', lambda m: f"```\n{m.group(1)}\n```", text, flags=re.DOTALL)
    text = re.sub(r'<code>(.*?)</code>', lambda m: f"`{m.group(1)}`", text, flags=re.DOTALL)
    text = re.sub(r'</?ul[^>]*>', '', text)
    text = re.sub(r'</?ol[^>]*>', '', text)
    text = re.sub(r'<li[^>]*>', '- ', text)
    text = text.replace('</li>', '')
    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', text, flags=re.DOTALL)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', text, flags=re.DOTALL)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', text, flags=re.DOTALL)
    text = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', text, flags=re.DOTALL)
    text = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', lambda m: "> " + m.group(1).replace("\n", "\n> "), text, flags=re.DOTALL)
    text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', text, flags=re.DOTALL)
    text = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', text, flags=re.DOTALL)
    text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', text, flags=re.DOTALL)
    text = re.sub(r'<hr[^>]*/?>', '---', text)
    text = re.sub(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.DOTALL)
    text = text.replace('<br/>', '\n').replace('<br>', '\n')
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def is_text_content(title: str, content_type: str) -> bool:
    """Check if content is likely text-based (not pure attachment)."""
    if content_type == "comment":
        return True
    if content_type == "page":
        return True
    # Skip obvious attachments
    skip_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.pdf', '.xlsx', '.xls', '.doc', '.docx', '.xmind', '.pptx', '.ppt')
    if title.lower().endswith(skip_extensions):
        return False
    if title.startswith("image"):
        return False
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "carlos"
    since_year = int(sys.argv[2]) if len(sys.argv) > 2 else 2023
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "./avatar_data"
    max_comments = int(sys.argv[4]) if len(sys.argv) > 4 else 500  # Limit comments for speed

    os.makedirs(output_dir, exist_ok=True)
    since_str = f"{since_year}-01-01"

    print(f"🔍 Searching content by '{username}' since {since_year}...")

    # 1. Search all content
    query = f'creator = "{username}" and created >= "{since_str}"'
    results = search_all(query, expand="history")
    print(f"📊 Found {len(results)} total items")

    # 2. Filter to text content
    text_items = []
    for r in results:
        title = r.get("title", "")
        ctype = r.get("type", "")
        if is_text_content(title, ctype):
            text_items.append(r)

    print(f"📝 Text items: {len(text_items)}")

    # Separate comments and pages
    comments = [r for r in text_items if r.get("type") == "comment"]
    pages = [r for r in text_items if r.get("type") == "page"]
    others = [r for r in text_items if r.get("type") not in ("comment", "page")]

    print(f"   Comments: {len(comments)}")
    print(f"   Pages: {len(pages)}")
    print(f"   Other: {len(others)}")

    # 3. Collect content
    collected = []

    # Collect all pages
    print(f"\n📥 Fetching {len(pages)} pages...")
    for i, item in enumerate(pages):
        pid = item.get("id")
        title = item.get("title", "")
        try:
            md = get_page_body(pid)
            history = item.get("history", {})
            created = history.get("createdDate", "")
            collected.append({
                "id": pid,
                "title": title,
                "type": "page",
                "space": item.get("space", {}).get("key", ""),
                "created": created,
                "url": f"https://kms.fineres.com/pages/viewpage.action?pageId={pid}",
                "content": md,
                "content_length": len(md)
            })
            if (i + 1) % 20 == 0:
                print(f"   ... {i + 1}/{len(pages)} pages done")
        except Exception as e:
            print(f"   ⚠️ Error fetching page {pid}: {e}")

    # Collect comments (with limit)
    comments_to_fetch = comments[:max_comments]
    print(f"\n📥 Fetching {len(comments_to_fetch)} comments (out of {len(comments)})...")
    for i, item in enumerate(comments_to_fetch):
        pid = item.get("id")
        title = item.get("title", "")
        try:
            md = get_page_body(pid)
            history = item.get("history", {})
            created = history.get("createdDate", "")
            collected.append({
                "id": pid,
                "title": title,
                "type": "comment",
                "space": item.get("space", {}).get("key", ""),
                "created": created,
                "url": f"https://kms.fineres.com/pages/viewpage.action?pageId={pid}",
                "content": md,
                "content_length": len(md)
            })
            if (i + 1) % 50 == 0:
                print(f"   ... {i + 1}/{len(comments_to_fetch)} comments done")
        except Exception as e:
            print(f"   ⚠️ Error fetching comment {pid}: {e}")

    # 4. Save
    print(f"\n💾 Saving {len(collected)} items...")

    with open(os.path.join(output_dir, "collected_content.json"), "w", encoding="utf-8") as f:
        json.dump(collected, f, ensure_ascii=False, indent=2)

    # Text corpus
    corpus_path = os.path.join(output_dir, "text_corpus.md")
    with open(corpus_path, "w", encoding="utf-8") as f:
        f.write(f"# KMS Content Corpus for Avatar Training\n\n")
        f.write(f"User: {username}\n")
        f.write(f"Period: {since_year}-present\n")
        f.write(f"Total items: {len(collected)}\n\n")
        f.write("---\n\n")

        for item in collected:
            f.write(f"## {item['title']}\n")
            f.write(f"- ID: {item['id']} | Type: {item['type']} | Space: {item['space']}\n")
            f.write(f"- Created: {item['created']}\n")
            f.write(f"- URL: {item['url']}\n\n")
            f.write(f"{item['content']}\n\n")
            f.write("---\n\n")

    # Summary
    type_counts = {}
    year_counts = {}
    for item in collected:
        t = item['type']
        y = item['created'][:4] if item['created'] else 'unknown'
        type_counts[t] = type_counts.get(t, 0) + 1
        year_counts[y] = year_counts.get(y, 0) + 1

    summary = {
        "username": username,
        "since_year": since_year,
        "total_collected": len(collected),
        "total_available": len(text_items),
        "comments_sampled": len(comments_to_fetch),
        "comments_total": len(comments),
        "pages_total": len(pages),
        "by_type": type_counts,
        "by_year": year_counts,
        "total_text_length": sum(item['content_length'] for item in collected)
    }

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"✅ Collection complete!")
    print(f"{'='*50}")
    print(f"Collected: {summary['total_collected']} items")
    print(f"By type: {summary['by_type']}")
    print(f"By year: {summary['by_year']}")
    print(f"Total text: {summary['total_text_length']:,} chars")
    print(f"Output: {os.path.abspath(output_dir)}")


if __name__ == "__main__":
    main()
