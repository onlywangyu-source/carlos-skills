---
name: self-evolution-engine
summary: "WorkBuddy 自我进化引擎 - 定期复盘历史对话与任务经验，沉淀为 skills/memory/身份文件的增量更新"
description: "定期（每两周）复盘 WorkBuddy 的工作历史，从使用习惯和任务问题中吸取经验，自动沉淀为 skills / memory / 身份文件的增量更新，实现持续进化。全自动模式，内置安全护栏（变更前必备份、变更日志、身份文件保守原则、可回滚）。"
triggers:
  - 自我进化
  - 进化引擎
  - 定期复盘
  - 经验沉淀
  - 跑一次进化
  - evolution
agent_created: true
---

# Self-Evolution Engine · 自我进化引擎

## 用途

定期复盘 WorkBuddy 的工作历史，从使用习惯和任务问题中吸取经验，自动沉淀为 skills / memory / 身份文件的增量更新，实现持续进化。

## 触发方式

- **定时触发**：automation 每两周周一凌晨 2:00 自动触发
- **手动触发**：用户说"自我进化"、"跑一次进化"、"复盘一下"时触发
- **触发后**：立即按下方流程执行一次完整迭代

## 关键路径

- 进化工作区：`/Users/wangyu/WorkBuddy/wangyu-space/.workbuddy/memory/evolution/`
- 进化索引：`evolution/INDEX.md`（历次进化摘要，追加式）
- 变更日志：`evolution/CHANGELOG.md`（每次变更的 diff 摘要，追加式）
- 单次报告：`evolution/YYYY-MM-DD-evolution.md`
- 单次备份：`evolution/YYYY-MM-DD-backups/`（被修改文件的原版）
- 身份文件根：`/Users/wangyu/.workbuddy/`（USER.md / SOUL.md / IDENTITY.md）
- 用户级 skills：`/Users/wangyu/.workbuddy/skills/`
- 项目级记忆：`/Users/wangyu/WorkBuddy/wangyu-space/.workbuddy/memory/`
- 用户级长期记忆：`/Users/wangyu/.workbuddy/MEMORY.md`
- **Obsidian Vault**：`/Users/wangyu/Documents/Obsidian-Vaults/Carlos-Knowledge`
- **Obsidian 进化目录**：`99-System/WorkBuddy-Evolution/`（与 `02-知识管理/` 完全隔离）
  - `_MOC.md`：进化日志索引页
  - `使用习惯模式.md`：使用习惯维度（追加式，按日期分段）
  - `问题错误复盘.md`：问题复盘维度（追加式，按日期分段）
  - `知识缺口识别.md`：知识缺口维度（追加式，按日期分段）
  - `偏好变化捕捉.md`：偏好变化维度（追加式，按日期分段）
  - `YYYY-MM-DD-evolution.md`：每次进化的完整报告副本

---

## 执行流程

### 阶段 0：初始化

1. **确定时间窗口**
   - 读取 `evolution/INDEX.md` 获取上次进化日期
   - 若 INDEX.md 不存在或为空，默认取近 14 天
   - 时间窗口 = [上次进化日期, 今天]

2. **创建本次工作目录**
   - 报告文件：`evolution/YYYY-MM-DD-evolution.md`
   - 备份目录：`evolution/YYYY-MM-DD-backups/`

3. **备份即将修改的文件**（全自动模式的安全底线）
   - 复制到 `evolution/YYYY-MM-DD-backups/`：
     - `~/.workbuddy/USER.md`
     - `~/.workbuddy/SOUL.md`
     - `~/.workbuddy/IDENTITY.md`
     - `~/.workbuddy/MEMORY.md`
     - `项目级/.workbuddy/memory/MEMORY.md`
   - 若文件不存在则跳过

### 阶段 1：采集（并行拉取数据源）

**1.1 历史对话检索**（使用 conversation_search 工具）
发起 3 条自包含查询：
- 查询 A："近两周用户与 WorkBuddy 的对话，包含任务执行、工具使用、工作流程"（start_date 设为窗口起点）
- 查询 B："近两周出现的错误、失败、返工、低效环节、用户反馈与纠正"
- 查询 C："近两周重复出现的任务模式、工作习惯、常用工具调用"

**1.2 记忆日志读取**
- 读取 `项目级/.workbuddy/memory/` 下时间窗口内的所有 `YYYY-MM-DD.md`
- 读取项目级 `MEMORY.md` 和用户级 `~/.workbuddy/MEMORY.md`

**1.3 现有 skills 清单**
- 用 Bash `find ~/.workbuddy/skills -name "SKILL.md" -maxdepth 2` 列出所有用户级 skill（Glob 的 `*/SKILL.md` 模式在某些环境下匹配不到，find 更可靠）
- 读取每个 skill 的 frontmatter（name/summary/triggers）和最近修改时间
- 记录 skill 用途速览

**1.4 身份文件现状**
- 读取 `USER.md`、`SOUL.md`、`IDENTITY.md` 全文

### 阶段 2：分析（四维度提炼）

每个维度产出"发现清单"，每条发现需标注来源证据（哪段对话/哪条日志）。

**2.1 使用习惯模式**
- 高频任务类型分布（数据分析 / 文档生成 / 代码开发 / 记忆维护 / 流程自动化 ...）
- 常用工具与连接器（FineBI / 企微 / 腾讯文档 / KMS ...）
- 工作时段分布（哪些时段任务密度高）
- 对话深度分布（简短问答 vs 多轮复杂任务）

**2.2 问题与低效复盘**
- 执行失败或返工的任务（根因 + 改进点）
- 重复出现的操作（可沉淀为 skill 的候选）
- 用户明确反馈"不要这样做"的项（边界校正）
- 工具调用错误或低效链路

**2.3 知识缺口识别**
- 反复出现但无对应 skill 的工作流
- 每次都要重新摸索的流程
- 应该但尚未沉淀为长期记忆的事实

**2.4 偏好与画像变化**
- USER.md 中需要补充的新偏好 / 新项目 / 新背景
- SOUL.md 中性格或边界需要微调的点（谨慎，需充分证据）
- IDENTITY.md 是否需要更新（极少）

### 阶段 3：沉淀（产出候选更新清单）

基于分析结果，产出结构化清单。每个候选需说明：来源证据、预期收益、风险等级。

**3.1 skills 增改候选**
- 新增 skill 候选：从重复工作流中提炼（命名、用途、核心步骤）
- 修改 skill 候选：修正发现的问题/低效环节（目标 skill、改什么、为什么）

**3.2 memory 沉淀候选**
- 追加到每日日志的要点
- 长期 MEMORY.md 需要新增/修订的条目

**3.3 身份文件更新候选**
- USER.md 更新项（新偏好、新项目、新背景）
- SOUL.md 更新项（保守，仅小幅增量，每项需 2+ 条证据）
- IDENTITY.md 更新项（极少，需 3+ 条证据）

### 阶段 4：应用（全自动模式）

按风险分层执行。所有变更写入 `evolution/CHANGELOG.md`。

**🟢 低风险 - 直接应用：**
- 追加每日记忆日志（`memory/YYYY-MM-DD.md`）
- 新增独立 skill（不覆盖现有的，新建目录）
- 长期 MEMORY.md 追加条目（仅追加，不删改原有内容）

**🟡 中风险 - 应用 + 记录 diff：**
- 修改现有 skill（已在阶段0备份）
- 更新 USER.md（已在阶段0备份）
- 应用后在 CHANGELOG.md 记录修改前后的关键差异

**🔴 高风险 - 保守原则 + 应用 + 记录 diff：**
- 修改 SOUL.md / IDENTITY.md（已在阶段0备份）
- 保守原则三条：
  1. 只做小幅增量调整，不重写整段
  2. 每项变更必须有 ≥2 条明确证据（对话/日志）
  3. 证据不足时，写入"未应用候选"清单，不强行修改
- 应用后在 CHANGELOG.md 记录完整 diff

### 阶段 4.5：Obsidian 同步（四维度分析结果写入知识库）

将阶段2的四维度分析结果同步到 Obsidian，**与一般知识更新完全隔离**。

#### 4.5.1 前置检查
- 确认 Obsidian Vault 路径存在：`~/Documents/Obsidian-Vaults/Carlos-Knowledge/`
- 若 `99-System/WorkBuddy-Evolution/` 不存在，创建之

#### 4.5.2 四维度页面追加（追加式，按日期分段）

对每个维度页面，在文件末尾 **追加** 一个以日期为标题的新段落：

**`使用习惯模式.md`** — 追加内容：
```markdown
## YYYY-MM-DD
### 高频任务类型分布（表格）
### 常用工具与连接器
### 工作时段特征
### 对话深度分布
### 趋势观察（与前几次对比）
```

**`问题错误复盘.md`** — 追加内容：
```markdown
## YYYY-MM-DD
### 执行失败或返工的任务（表格：# | 问题 | 日期 | 根因 | 改进措施 | 状态）
### 重复出现的操作 → 可沉淀为skill的候选
### 用户明确反馈的边界校正
### 趋势观察
```

**`知识缺口识别.md`** — 追加内容：
```markdown
## YYYY-MM-DD
### 缺失的 Skill（已补/待补）
### 未沉淀的长期记忆（已补/待补）
### 重复摸索的流程
### 趋势观察
```

**`偏好变化捕捉.md`** — 追加内容：
```markdown
## YYYY-MM-DD
### USER.md 画像更新（🟡 中风险）
### SOUL.md 协作风格更新（🔴 高风险 · 保守增量）
### IDENTITY.md（未变更说明）
### 偏好变化趋势观察表
```

**写入规则**：
- 每个维度页面是 **纯追加**，不修改历史段落
- 每次迭代的内容用 `## YYYY-MM-DD` 作为二级标题分段
- 表格格式统一，方便跨期对比
- 若某维度本次无发现，写"本期无显著变化"并跳过

#### 4.5.3 进化报告副本
- 将完整的 `evolution/YYYY-MM-DD-evolution.md` 复制到 Obsidian 的 `99-System/WorkBuddy-Evolution/YYYY-MM-DD-evolution.md`
- 格式微调：添加 YAML frontmatter 和 Obsidian 内部链接（`[[使用习惯模式]]` 等）

#### 4.5.4 更新索引页 `_MOC.md`
- 在进化报告归档表格中追加一行：`| 日期 | [[YYYY-MM-DD-evolution]] | 变更数 |`
- 更新快速导航中的"最新进化报告"链接

#### 4.5.5 写入方式
- 使用 Write 工具直接写入 Obsidian 路径下的 .md 文件
- 对于已有文件（四维度页面），先 Read 全文，再 Edit 在末尾追加新段落
- 对于新文件（首次或首次创建），用 Write 直接创建

### 阶段 5：生成进化报告

输出到 `evolution/YYYY-MM-DD-evolution.md`，使用下方模板。

同时更新 `evolution/INDEX.md`：追加一行本次进化摘要。

---

## 安全护栏（不可违反）

1. **变更前必备份** — 所有被修改的文件必须先复制到 `evolution/YYYY-MM-DD-backups/`
2. **变更必记日志** — 每次修改写入 `evolution/CHANGELOG.md`，含文件路径、改动类型、diff 摘要
3. **身份文件保守原则** — SOUL.md / IDENTITY.md 只增不删、只小幅调整不重写，需 ≥2 条证据
4. **永不删除** — 进化引擎从不删除现有 skill / memory，只新增或修订
5. **可回滚** — 保留所有 backups/，用户可随时从备份恢复（说"回滚到某次进化前"即可）
6. **证据驱动** — 所有分析发现和更新候选必须标注来源证据，不臆测

---

## 进化报告模板

```markdown
# 进化报告 · YYYY-MM-DD

## 摘要
（一句话总结本次进化的核心收获）

## 时间窗口
YYYY-MM-DD ~ YYYY-MM-DD（共 N 天）

## 数据源统计
- 历史对话检索：N 条相关结果
- 记忆日志：N 篇
- 现有 skills：N 个
- 身份文件：已读取

## 四维度发现

### 使用习惯
- ...

### 问题与低效
- ...

### 知识缺口
- ...

### 偏好与画像变化
- ...

## 应用的变更

### 🟢 自动应用
| 类型 | 目标 | 内容摘要 |
|------|------|----------|
| ... | ... | ... |

### 🟡 中风险应用（含 diff）
| 文件 | 改动类型 | diff 摘要 |
|------|----------|----------|
| ... | ... | ... |

### 🔴 高风险应用（含 diff）
| 文件 | 改动类型 | 证据 | diff 摘要 |
|------|----------|------|----------|
| ... | ... | ... | ... |

## 未应用候选（证据不足）
- ...

## 下次进化建议
- ...
```

---

## INDEX.md 格式（追加式）

```markdown
# 进化历史索引

| 日期 | 摘要 | 变更数 | 报告路径 |
|------|------|--------|----------|
| YYYY-MM-DD | 一句话摘要 | N 项 | evolution/YYYY-MM-DD-evolution.md |
```

---

## 执行注意事项

- 这是一个**自包含流程**，执行时没有当前对话上下文，所有信息从文件和 conversation_search 获取
- 执行顺序严格按阶段 0→5，不可跳步
- 若某阶段数据不足（如首次执行无历史），如实记录"数据不足"并跳过该维度，不臆造
- 报告生成后，用 present_files 展示报告路径给用户（若为手动触发）
- 若为 automation 自动触发，报告生成后无需等待用户，正常结束即可
