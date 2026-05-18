#!/usr/bin/env python3
"""
FineBI/FineReport 数据查询脚本
支持两种认证方式：
1. 开放平台 API 密钥（client_id + secret）
2. 网页登录（用户名 + 密码获取 Cookie）

用法示例:
  # API 密钥方式
  python3 query_finebi.py --base-url "https://bi.finereporthelp.com/webroot/decision" \
    --client-id "xxx" --secret "xxx" \
    --service "ds/data" --params '{"report":"GettingStarter.cpt","dsName":"ds1"}'

  # 网页登录方式
  python3 query_finebi.py --base-url "https://bi.finereporthelp.com/webroot/decision" \
    --username "carlos@fanruan.com" --password "Cherry320" \
    --service "ds/data" --params '{"report":"GettingStarter.cpt","dsName":"ds1"}'
"""

import argparse
import json
import sys
import urllib.parse

import requests


def login_with_password(base_url: str, username: str, password: str) -> dict:
    """使用用户名密码登录，获取 Session Cookie。"""
    session = requests.Session()
    login_url = f"{base_url}/login/cross/domain"
    
    # 帆软决策平台的登录接口可能因版本而异
    # 尝试通用的登录接口
    payload = {
        "username": username,
        "password": password,
        "validity": -1,  # 会话有效期，-1 表示浏览器关闭前有效
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
    }
    
    resp = session.post(login_url, data=payload, headers=headers, allow_redirects=True)
    resp.raise_for_status()
    
    # 检查登录是否成功
    try:
        result = resp.json()
        if result.get("error") or result.get("message") == "fail":
            print(f"登录失败: {result}", file=sys.stderr)
            sys.exit(1)
    except Exception:
        pass
    
    return {"session": session}


def query_with_api_key(base_url: str, client_id: str, secret: str, service: str, params: dict) -> dict:
    """使用 API 密钥查询数据。"""
    api_base = f"{base_url}/sp/client/api/"
    url = f"{api_base}{service}"
    
    headers = {
        "client_id": client_id,
        "secret": secret,
        "Content-Type": "application/json",
    }
    
    resp = requests.get(url, headers=headers, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


def query_with_session(session: requests.Session, base_url: str, service: str, params: dict) -> dict:
    """使用已登录的 Session 查询数据。"""
    api_base = f"{base_url}/sp/client/api/"
    url = f"{api_base}{service}"
    
    headers = {
        "Content-Type": "application/json",
    }
    
    resp = session.get(url, headers=headers, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="FineBI/FineReport 数据查询")
    parser.add_argument("--base-url", required=True, help="决策平台基础URL，如 https://bi.finereporthelp.com/webroot/decision")
    parser.add_argument("--client-id", help="开放平台应用ID")
    parser.add_argument("--secret", help="开放平台应用密钥")
    parser.add_argument("--username", help="登录用户名（用于Cookie认证）")
    parser.add_argument("--password", help="登录密码（用于Cookie认证）")
    parser.add_argument("--service", required=True, help="API服务路径，如 sql/data, ds/data, list/report/data 等")
    parser.add_argument("--params", default="{}", help="查询参数JSON字符串")
    parser.add_argument("--output", help="输出结果到文件（可选）")
    
    args = parser.parse_args()
    
    # 解析参数
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"参数解析失败: {e}", file=sys.stderr)
        sys.exit(1)
    
    result = None
    
    # 优先使用 API 密钥
    if args.client_id and args.secret:
        result = query_with_api_key(args.base_url, args.client_id, args.secret, args.service, params)
    elif args.username and args.password:
        auth = login_with_password(args.base_url, args.username, args.password)
        session = auth["session"]
        result = query_with_session(session, args.base_url, args.service, params)
    else:
        print("请提供认证信息：(--client-id 和 --secret) 或 (--username 和 --password)", file=sys.stderr)
        sys.exit(1)
    
    # 输出结果
    output = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"结果已保存到: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
