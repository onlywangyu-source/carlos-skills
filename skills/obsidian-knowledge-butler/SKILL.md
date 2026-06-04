---
name: obsidian-knowledge-butler
description: Carlos 的 Obsidian 知识库自动化管家。支持缺口驱动学习系统：KMS 历史内容自动归类、外部资料入库、知识缺漏分析、读书推荐、业务缺漏添加等功能。
agent_created: true
---

# Obsidian 知识库自动化管家

## 功能

1. **KMS 历史内容自动归类** — 扫描 KMS 采集数据，按五域模型分类
2. **外部资料自动入库** — 将文章/书籍/课程自动创建为 Obsidian 页面
3. **知识缺漏分析** — 基于能力评估框架识别知识短板
4. **读书推荐** — 根据缺漏生成书单，附速读攻略和网络替代材料
5. **业务缺漏添加** — 工作中识别的新缺漏，一键添加到缺漏清单

## 用法

```bash
# 扫描 KMS 内容并归类
python3 ~/.workbuddy/wiki-knowledge/scripts/knowledge_butler.py --scan-kms

# 将外部资料入库
python3 ~/.workbuddy/wiki-knowledge/scripts/knowledge_butler.py --ingest <文件路径> --type [article|book|course]

# 执行知识缺漏分析
python3 ~/.workbuddy/wiki-knowledge/scripts/knowledge_butler.py --gap-analysis

# 生成读书推荐
python3 ~/.workbuddy/wiki-knowledge/scripts/knowledge_butler.py --book-recommend

# 添加业务触发的知识缺漏
python3 ~/.workbuddy/wiki-knowledge/scripts/knowledge_butler.py --add-gap "缺漏名称"
```

## 配置

- Vault 路径: `~/Documents/Obsidian-Vaults/Carlos-Knowledge`
- KMS 数据路径: `~/.workbuddy/wiki-knowledge/raw/kms-content`
- 五域模型: 客户成功 / 服务运营 / 团队管理 / 战略规划 / 领导力

## 缺口驱动学习系统

### 核心页面

| 页面 | 路径 | 作用 |
|------|------|------|
| 知识缺漏分析 | `02-知识管理/知识缺漏分析.md` | 统一管理所有缺漏（AI扫描 + 业务触发） |
| 读书推荐 | `02-知识管理/读书推荐.md` | 每个缺漏附速读攻略和网络替代材料 |
| 学习计划 | `02-知识管理/学习计划.md` | 缺口歼灭任务，6步闭环 |

### 状态流转

```
🔴 待启动 → 🟡 速读中 → 🟢 已入库 → ✅ 已掌握
```

### 速读标准

- 读目录 + 核心章节（30-60 分钟）
- 把划线内容丢给 WorkBuddy 提取框架
- 在 Obsidian 审阅入库，按需回读原文

## 五域分类规则

基于关键词匹配：
- **客户成功**: 客户成功、复购、续费、满意度、NPS、客户健康度、客户分层、客户生命周期、客户运营、客户留存、客户价值、客户体验、订阅制、客户线索、机会转化、客户声音
- **服务运营**: 技术支持、服务运营、SLA、服务流程、服务质量、工单、问题处理、响应时间、服务标准、运维、值班、服务台、售后、服务交付、服务团队、服务指标
- **团队管理**: 团队管理、组织设计、人才发展、绩效管理、薪酬激励、文化建设、职级、晋升、招聘、培训、组织能力、干部、管理者、教练、绩效、OKR、目标管理、述职、盘点
- **战略规划**: 战略、数据分析、行业洞察、商业模式、竞争、经营、预算、成本、收入、增长、市场份额、产品战略、业务规划、数字化转型、市场分析、财务分析、投资回报
- **领导力**: 领导力、沟通、影响力、跨部门、协作、变革管理、创新、决策、执行力、愿景、激励、授权、反馈、向上管理、横向协作、冲突处理

## 注意事项

- 运行前确保 KMS 数据已采集（`~/.workbuddy/wiki-knowledge/raw/kms-content/_index.json` 存在）
- 首次运行 `--scan-kms` 会生成分类报告，后续 `--gap-analysis` 依赖此报告
- 外部资料入库时，建议先用 `--type` 指定正确的资料类型以获得最佳模板
- 添加业务缺漏后，需在 Obsidian 中手动补充阅读材料
