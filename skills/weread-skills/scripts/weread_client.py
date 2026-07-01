#!/usr/bin/env python3
"""微信读书 API 客户端。

API Key must be provided through the WEREAD_API_KEY environment variable.
"""
import os, sys, json, urllib.request, urllib.parse

API_KEY = os.environ.get("WEREAD_API_KEY")
BASE_URL = "https://i.weread.qq.com/api/agent/gateway"

def api_post(api_name, **params):
    """调用微信读书 Agent API"""
    if not API_KEY:
        raise RuntimeError("WEREAD_API_KEY environment variable is not set")
    body = {"api_name": api_name, "skill_version": "1.0.3"}
    body.update(params)
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 weread_client.py <api_name> [key=value ...]")
        print("示例: python3 weread_client.py /shelf/sync")
        sys.exit(1)

    api_name = sys.argv[1]
    kwargs = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            # 尝试解析为数字
            try:
                v = int(v)
            except ValueError:
                try:
                    v = float(v)
                except ValueError:
                    pass
            kwargs[k] = v

    try:
        result = api_post(api_name, **kwargs)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ 调用失败: {e}", file=sys.stderr)
        sys.exit(1)
