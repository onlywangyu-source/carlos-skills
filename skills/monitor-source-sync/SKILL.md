---
name: monitor-source-sync
agent_created: true
description: 当用户提供一个外部链接或文件，要求基于其内容更新多事务主动管理系统（Hermes Monitor）中某个项目的配置、里程碑、风险或 dashboard 记录时，使用本技能完成从读取源内容到同步数据库的完整流程。
---

# Monitor Source Sync

## 触发条件

用户给出以下任一形式的输入，并要求"更新项目"、"更新 dashboard"、"更新配置"或类似含义：
- 一个网页链接（如悟帆AI、KMS、腾讯文档、飞书文档等）
- 一个本地文件路径（PDF、Word、TXT、MP3 等）
- 一段聊天记录或会议纪要的粘贴文本

目标项目属于 `/opt/hermes/monitor/monitor-config.yml` 中定义的 6 个项目之一：区域转型、服务价值触达、CSM方法论、A3二期、智能客服、AI生成客户案例。

## 执行流程

### 1. 读取源内容

- 如果是网页链接：
  - 先用 `WebFetch` 尝试获取内容
  - 如果返回内容为空或只有标题，加载 `agent-browser` skill，用真实浏览器访问并 `snapshot`
- 如果是本地文件：
  - PDF：使用 `pypdf` 或 `PyMuPDF` 提取文本（优先用已安装的 venv）
  - Word/PPT：使用对应的 `docx` / `pptx` skill
  - MP3：告知用户当前环境无本地语音识别能力，建议用 API 或外部工具转写
- 如果是粘贴文本：直接使用

### 2. 识别目标项目

从内容中提取项目名称或关键词，映射到 `project_id`：
| 名称 | project_id |
|------|-----------|
| 区域转型 | regional_transformation |
| 服务价值触达 | service_value |
| CSM方法论 | csm_methodology |
| A3二期 | a3_phase2 |
| 智能客服 | ai_customer_service |
| AI生成客户案例 | ai_case_gen |

### 3. 查询现有配置

SSH 到服务器 `111.229.206.147`，读取 `/opt/hermes/monitor/monitor-config.yml` 中目标项目的完整配置块：
```bash
ssh -i ~/.ssh/WBmiyao.pem ubuntu@111.229.206.147 'sed -n "<start>,<end>p" /opt/hermes/monitor/monitor-config.yml'
```

同时查询 `project_state.db` 当前状态：
```bash
ssh -i ~/.ssh/WBmiyao.pem ubuntu@111.229.206.147 'python3 -c "...sqlite3..."'
```

### 4. 设计更新内容

基于源内容，判断需要对以下哪些项进行更新：
- 里程碑：新增 / 修改 deadline / 更新状态为 completed / 更新 note
- 风险：新增或更新 `station_risk`，level 可选 `warning` / `critical`
- 负责人：统一使用企微 ID，避免中文名/英文名混用（参考企微用户注册表）
- 来源：在 `source` 中记录原始出处（URL、页面ID、文件路径、会议时间）

### 5. 修改服务器配置

1. 先备份：
```bash
ssh -i ~/.ssh/WBmiyao.pem ubuntu@111.229.206.147 'cp /opt/hermes/monitor/monitor-config.yml /opt/hermes/monitor/monitor-config.yml.bak.$(date +%Y%m%d%H%M)'
```

2. 用 Python 脚本精确替换目标项目配置块，避免破坏 YAML 结构。脚本可通过 heredoc + ssh 上传到 `/tmp/` 执行。

3. 验证 YAML 格式：
```bash
ssh -i ~/.ssh/WBmiyao.pem ubuntu@111.229.206.147 'python3 -c "import yaml; yaml.safe_load(open(\"/opt/hermes/monitor/monitor-config.yml\"))"'
```

### 6. 同步到数据库

在 `/opt/hermes/monitor` 目录下执行：
```bash
ssh -i ~/.ssh/WBmiyao.pem ubuntu@111.229.206.147 'cd /opt/hermes/monitor && python3 sync_config_to_db.py --db /opt/hermes-data/project_state.db'
```

注意：
- 默认脚本会写到 `~/.hermes/test_state.db`，必须显式指定 `--db /opt/hermes-data/project_state.db`
- `sync_config_to_db.py` 目前采用增量 INSERT，**不会自动去重**。每次同步后必须检查是否有重复里程碑

### 6.5 检查并修复数据重复

同步完成后，立即查询数据库确认是否有重复：
```python
SELECT name, status, deadline, COUNT(*) as cnt 
FROM milestones 
WHERE project_id = '<project_id>' 
GROUP BY name, status, deadline 
HAVING cnt > 1;
```

如果发现重复，说明 `sync_config_to_db.py` 产生了脏数据。在继续之前执行数据库重建：

1. 备份数据库：
```bash
ssh -i ~/.ssh/WBmiyao.pem ubuntu@111.229.206.147 'cp /opt/hermes-data/project_state.db /opt/hermes-data/project_state.db.bak.$(date +%Y%m%d%H%M)'
```

2. 清空并重建（Python 脚本）：
```python
import sqlite3
conn = sqlite3.connect("/opt/hermes-data/project_state.db")
c = conn.cursor()
c.execute("DELETE FROM milestones")
c.execute("DELETE FROM risks")
c.execute("DELETE FROM sqlite_sequence WHERE name='milestones'")
c.execute("DELETE FROM sqlite_sequence WHERE name='risks'")
conn.commit()
conn.close()
```

3. 重新运行同步：
```bash
ssh -i ~/.ssh/WBmiyao.pem ubuntu@111.229.206.147 'cd /opt/hermes/monitor && python3 sync_config_to_db.py --db /opt/hermes-data/project_state.db'
```

### 7. 同步本地 workspace

```bash
scp -i ~/.ssh/WBmiyao.pem ubuntu@111.229.206.147:/opt/hermes/monitor/monitor-config.yml /Users/wangyu/WorkBuddy/2026-05-10-task-28/monitor-config.yml
```

### 8. 更新 memory

在 `/Users/wangyu/WorkBuddy/2026-05-10-task-28/.workbuddy/memory/YYYY-MM-DD.md` 追加：
- 读取的源链接/文件
- 更新的项目名称
- 具体变更点（里程碑、风险等）
- 发现的异常或待确认事项

### 9. 向用户汇报

用表格汇总变更，列出：
- 新增/修改的里程碑
- 更新后的风险状态
- 待用户确认的事项
- 发现的数据质量问题（如 DB 中里程碑重复）

## 注意事项

- 修改配置前备份 `monitor-config.yml`；重建数据库前备份 `project_state.db`。
- 发现 `sync_config_to_db.py` 产生重复数据时，不要反复叠加同步。优先采用"备份 → 清空里程碑/风险表 → 重新同步"的重建方式，从源头恢复数据一致性。
- 所有 destructive 操作前必须先备份 `monitor-config.yml`。
- 人员字段统一使用企微 ID；若源内容中只有中文名/英文名，查注册表映射。
- 如果源内容无法读取（如需登录），优先尝试生成公开分享链接，或请用户复制粘贴关键内容。
- 修改配置后必须验证 YAML 格式有效，再同步 DB。

## 相关路径

| 路径 | 说明 |
|------|------|
| `/opt/hermes/monitor/monitor-config.yml` | 服务器主配置 |
| `/opt/hermes-data/project_state.db` | 正式项目状态数据库 |
| `/Users/wangyu/WorkBuddy/2026-05-10-task-28/monitor-config.yml` | 本地 workspace 副本 |
| `~/.ssh/WBmiyao.pem` | 服务器 SSH key |
