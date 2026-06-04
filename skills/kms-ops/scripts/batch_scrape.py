#!/usr/bin/env python3
"""
批量采集 Carlos 在 KMS 上的历史内容
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kms_client import search_pages, get_page_body, get_page, api_get

OUTPUT_DIR = os.path.expanduser("~/.workbuddy/wiki-knowledge/raw/kms-content")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_all_carlos_pages():
    """分页获取所有 carlos 创建的页面"""
    all_pages = []
    start = 0
    limit = 50
    max_pages = 1000  # 安全上限
    
    print("🔍 正在搜索 carlos 在 KMS 上的所有内容...")
    
    while start < max_pages:
        query = f'creator = carlos AND type = page'
        data = api_get("/content/search", params={
            "cql": query,
            "limit": limit,
            "start": start,
            "expand": "space"
        })
        
        results = data.get("results", [])
        if not results:
            break
            
        for r in results:
            # 只保留页面，跳过附件
            if r.get("type") == "page":
                all_pages.append({
                    "id": r.get("id"),
                    "title": r.get("title"),
                    "space": r.get("space", {}).get("key", "unknown"),
                    "url": f"https://kms.fineres.com/pages/viewpage.action?pageId={r.get('id')}"
                })
        
        print(f"  已获取 {len(all_pages)} 个页面...")
        
        if len(results) < limit:
            break
        start += limit
        time.sleep(0.5)  # 避免请求过快
    
    return all_pages

def download_page_content(page_info):
    """下载单个页面的内容"""
    page_id = page_info["id"]
    title = page_info["title"]
    
    # 清理文件名
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_title = safe_title.replace(' ', '_')[:80]
    filename = f"{page_id}_{safe_title}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    if os.path.exists(filepath):
        print(f"  ⏭ 已存在，跳过: {title}")
        return True
    
    try:
        body_md = get_page_body(page_id)
        
        # 添加元数据头部
        content = f"""---
title: {title}
source: KMS
space: {page_info['space']}
page_id: {page_id}
url: {page_info['url']}
scraped_at: {time.strftime('%Y-%m-%d %H:%M:%S')}
---

# {title}

> 来源: [{title}]({page_info['url']})
> 空间: `{page_info['space']}`

{body_md}
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ 已保存: {title}")
        return True
        
    except Exception as e:
        print(f"  ❌ 失败: {title} - {e}")
        return False

def main():
    print("=" * 60)
    print("KMS 内容批量采集工具")
    print("=" * 60)
    
    pages = fetch_all_carlos_pages()
    print(f"\n📊 共找到 {len(pages)} 个页面")
    
    if not pages:
        print("没有找到任何内容，退出。")
        return
    
    # 保存页面索引
    index_path = os.path.join(OUTPUT_DIR, "_index.json")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)
    print(f"📑 页面索引已保存: {index_path}")
    
    # 批量下载内容
    print(f"\n⬇️ 开始下载内容到: {OUTPUT_DIR}")
    success = 0
    failed = 0
    
    for i, page in enumerate(pages, 1):
        print(f"\n[{i}/{len(pages)}]", end="")
        if download_page_content(page):
            success += 1
        else:
            failed += 1
        time.sleep(0.3)  # 避免请求过快
    
    print("\n" + "=" * 60)
    print(f"✅ 采集完成!")
    print(f"   成功: {success}")
    print(f"   失败: {failed}")
    print(f"   总计: {len(pages)}")
    print(f"   保存位置: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
