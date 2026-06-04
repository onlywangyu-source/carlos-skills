"""
卡洛斯跨会话记忆模块
每次对话结束后调用，将关键信息写入 memory.json
下次对话开始时自动加载
"""
import json, os
from datetime import datetime

MEMORY_FILE = os.path.expanduser("~/.workbuddy/skills/carlos-avatar/memory.json")

def load_memory():
    """加载跨会话记忆"""
    if not os.path.exists(MEMORY_FILE):
        return {"sessions": [], "key_facts": {}, "user_preferences": {}}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(memory):
    """保存跨会话记忆"""
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def append_session(session_summary: dict):
    """
    session_summary 格式：
    {
        "timestamp": "2026-05-31T14:30:00",
        "topic": "评审录屏 / 分析方案 / 讨论CSM方法论",
        "key_points": ["用户偏好XXX", "决策：XXX", "待跟进：XXX"],
        "decisions": ["决定做XXX", "放弃XXX方案"],
        "follow_ups": ["下次需要确认XXX"]
    }
    """
    memory = load_memory()
    memory["sessions"].append(session_summary)
    # 只保留最近20次会话
    memory["sessions"] = memory["sessions"][-20:]
    save_memory(memory)
    return memory

def update_key_facts(facts: dict):
    """更新关键事实（覆盖式）"""
    memory = load_memory()
    memory["key_facts"].update(facts)
    save_memory(memory)

def update_preferences(prefs: dict):
    """更新用户偏好"""
    memory = load_memory()
    memory["user_preferences"].update(prefs)
    save_memory(memory)

def get_context_for_prompt() -> str:
    """生成供 LLM 使用的记忆上下文字符串"""
    memory = load_memory()
    if not memory["sessions"]:
        return ""

    lines = ["## 跨会话记忆（最近对话摘要）"]
    for s in memory["sessions"][-5:]:
        lines.append(f"- {s['timestamp'][:10]} | {s['topic']}")
        for kp in s.get("key_points", [])[:3]:
            lines.append(f"  - {kp}")

    if memory.get("key_facts"):
        lines.append("\n## 关键事实")
        for k, v in memory["key_facts"].items():
            lines.append(f"- {k}: {v}")

    if memory.get("user_preferences"):
        lines.append("\n## 用户偏好")
        for k, v in memory["user_preferences"].items():
            lines.append(f"- {k}: {v}")

    return "\n".join(lines)

if __name__ == "__main__":
    # 测试
    append_session({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "topic": "测试记忆功能",
        "key_points": ["测试关键点1", "测试关键点2"],
        "decisions": [],
        "follow_ups": []
    })
    print(get_context_for_prompt())
