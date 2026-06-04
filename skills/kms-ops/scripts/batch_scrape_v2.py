#!/usr/bin/env python3
"""
KMS 内容完整采集工具 - 支持分页和多种搜索策略
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kms_client import get_page_body, get_page, api_get

OUTPUT_DIR = os.path.expanduser("~/.workbuddy/wiki-knowledge/raw/kms-content")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# KMS API 硬限制
MAX_LIMIT = 200

def fetch_with_paging(cql_query, max_total=5000):
    """分页获取所有结果，处理KMS的200条硬限制"""
    all_results = []
    start = 0
    page_count = 0
    
    print(f"🔍 查询: {cql_query}")
    
    while len(all_results) < max_total:
        page_count += 1
        try:
            data = api_get("/content/search", params={
                "cql": cql_query,
                "limit": MAX_LIMIT,
                "start": start,
                "expand": "space,version"
            })
            
            results = data.get("results", [])
            total_size = data.get("size", 0)
            
            if not results:
                break
            
            all_results.extend(results)
            print(f"  第{page_count}页: 获取 {len(results)} 条，累计 {len(all_results)}/{total_size}")
            
            # 检查是否还有下一页
            has_next = "next" in data.get("_links", {})
            if not has_next or len(results) < MAX_LIMIT:
                break
                
            start += MAX_LIMIT
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ❌ 请求失败: {e}")
            break
    
    return all_results

def fetch_all_carlos_content():
    """使用多种策略获取carlos相关的所有内容"""
    all_pages = {}
    
    # 策略1: creator = carlos
    print("\n📌 策略1: 搜索 creator = carlos")
    results = fetch_with_paging("creator = carlos AND type = page")
    for r in results:
        if r.get("type") == "page":
            pid = r.get("id")
            all_pages[pid] = {
                "id": pid,
                "title": r.get("title"),
                "space": r.get("space", {}).get("key", "unknown"),
                "url": f"https://kms.fineres.com/pages/viewpage.action?pageId={pid}",
                "strategy": "creator"
            }
    print(f"   找到 {len(results)} 个页面，去重后 {len(all_pages)} 个")
    
    # 策略2: contributor = carlos (包含编辑过的)
    print("\n📌 策略2: 搜索 contributor = carlos")
    results = fetch_with_paging("contributor = carlos AND type = page")
    new_count = 0
    for r in results:
        if r.get("type") == "page":
            pid = r.get("id")
            if pid not in all_pages:
                all_pages[pid] = {
                    "id": pid,
                    "title": r.get("title"),
                    "space": r.get("space", {}).get("key", "unknown"),
                    "url": f"https://kms.fineres.com/pages/viewpage.action?pageId={pid}",
                    "strategy": "contributor"
                }
                new_count += 1
    print(f"   找到 {len(results)} 个页面，新增 {new_count} 个")
    
    # 策略3: 按空间搜索，确保覆盖所有相关空间
    spaces = ["support", "FRBI", "FIN", "ITR", "fine"]
    for space in spaces:
        print(f"\n📌 策略3: 搜索 space = {space} AND (creator = carlos OR contributor = carlos)")
        try:
            results = fetch_with_paging(f"space = {space} AND (creator = carlos OR contributor = carlos) AND type = page")
            new_count = 0
            for r in results:
                if r.get("type") == "page":
                    pid = r.get("id")
                    if pid not in all_pages:
                        all_pages[pid] = {
                            "id": pid,
                            "title": r.get("title"),
                            "space": r.get("space", {}).get("key", "unknown"),
                            "url": f"https://kms.fineres.com/pages/viewpage.action?pageId={pid}",
                            "strategy": f"space_{space}"
                        }
                        new_count += 1
            print(f"   找到 {len(results)} 个页面，新增 {new_count} 个")
        except Exception as e:
            print(f"   ⚠️ 搜索失败: {e}")
    
    # 策略4: 按时间范围搜索（最近3年）
    print("\n📌 策略4: 按时间范围搜索最近3年内容")
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=3*365)).strftime("%Y-%m-%d")
    
    time_queries = [
        f"creator = carlos AND type = page AND lastModified >= '{start_date}'",
        f"contributor = carlos AND type = page AND lastModified >= '{start_date}'",
    ]
    
    for query in time_queries:
        print(f"   查询: {query}")
        try:
            results = fetch_with_paging(query)
            new_count = 0
            for r in results:
                if r.get("type") == "page":
                    pid = r.get("id")
                    if pid not in all_pages:
                        all_pages[pid] = {
                            "id": pid,
                            "title": r.get("title"),
                            "space": r.get("space", {}).get("key", "unknown"),
                            "url": f"https://kms.fineres.com/pages/viewpage.action?pageId={pid}",
                            "strategy": "time_range"
                        }
                        new_count += 1
            print(f"   找到 {len(results)} 个页面，新增 {new_count} 个")
        except Exception as e:
            print(f"   ⚠️ 搜索失败: {e}")
    
    return list(all_pages.values())

def download_page_content(page_info):
    """下载单个页面的内容"""
    page_id = page_info["id"]
    title = page_info["title"]
    
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_title = safe_title.replace(' ', '_')[:80]
    filename = f"{page_id}_{safe_title}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    if os.path.exists(filepath):
        return True, "exists"
    
    try:
        body_md = get_page_body(page_id)
        
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
        
        return True, "success"
        
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("KMS 内容完整采集工具")
    print("目标: 采集 Carlos 近3年所有 KMS 内容")
    print("=" * 60)
    
    pages = fetch_all_carlos_content()
    print(f"\n📊 共找到 {len(pages)} 个唯一页面")
    
    if not pages:
        print("没有找到任何内容，退出。")
        return
    
    # 保存页面索引
    index_path = os.path.join(OUTPUT_DIR, "_index.json")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)
    print(f"📑 页面索引已保存: {index_path}")
    
    # 统计空间分布
    spaces = {}
    for p in pages:
        s = p['space']
        spaces[s] = spaces.get(s, 0) + 1
    print("\n📁 空间分布:")
    for s, c in sorted(spaces.items(), key=lambda x: -x[1]):
        print(f"   {s}: {c}")
    
    # 批量下载内容
    print(f"\n⬇️ 开始下载内容到: {OUTPUT_DIR}")
    success = 0
    failed = 0
    skipped = 0
    
    for i, page in enumerate(pages, 1):
        ok, status = download_page_content(page)
        if status == "exists":
            skipped += 1
        elif ok:
            success += 1
        else:
            failed += 1
            print(f"   ❌ [{i}/{len(pages)}] {page['title']}: {status}")
        
        if i % 50 == 0:
            print(f"   📈 进度: {i}/{len(pages)} (成功:{success} 跳过:{skipped} 失败:{failed})")
        
        time.sleep(0.2)
    
    print("\n" + "=" * 60)
    print(f"✅ 采集完成!")
    print(f"   总计页面: {len(pages)}")
    print(f"   新下载: {success}")
    print(f"   已存在跳过: {skipped}")
    print(f"   失败: {failed}")
    print(f"   保存位置: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
