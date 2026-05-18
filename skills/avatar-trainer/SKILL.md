---
name: avatar-trainer
description: Train a personal AI avatar based on user's KMS (Confluence) historical content. This skill should be used when the user wants to create an AI clone of themselves that can reply in their style via KMS comments, WeChat, or WeCom. Trigger phrases include: 训练分身, 个人分身, AI分身, 风格克隆, persona训练, 模仿我的风格回复.
agent_created: true
---

# Avatar Trainer

Train a personal AI avatar by analyzing historical content from KMS (Confluence).

## Overview

This skill provides a workflow to:
1. **Collect** user's historical pages and comments from KMS
2. **Analyze** writing style, thinking patterns, and domain knowledge
3. **Generate** a persona prompt that can be used to create an AI clone

## Prerequisites

- KMS access token configured in `kms-ops` skill
- Python 3 with `requests`, `jieba` packages
- User's KMS username (e.g., `carlos`)

## Workflow

### Step 1: Collect Content

Run the collection script to fetch user's historical content:

```bash
python3 scripts/collect_avatar_data.py <username> <since_year> <output_dir> [max_comments]
```

Example:
```bash
python3 scripts/collect_avatar_data.py carlos 2023 ./avatar_data 500
```

This will:
- Search all content created by the user since the specified year
- Fetch page bodies and comment contents
- Skip non-text attachments (images, Excel, PDF)
- Save structured data to `collected_content.json`
- Save text corpus to `text_corpus.md`
- Save summary to `summary.json`

**Parameters:**
- `username`: KMS username (e.g., `carlos`)
- `since_year`: Starting year for collection (e.g., `2023`)
- `output_dir`: Output directory path
- `max_comments`: (Optional) Max comments to fetch (default: 500). Pages are always fully fetched.

### Step 2: Analyze Style

After collection, analyze the data to extract style characteristics:

```bash
python3 scripts/analyze_style.py <data_dir>
```

This analyzes:
- Sentence length distribution
- Common opening patterns
- Question patterns
- Word frequency (Chinese via jieba)
- Expression patterns (agree/disagree/suggest)

### Step 3: Generate Persona

Use the analysis results to generate a persona prompt:

1. Review `text_corpus.md` for sample content
2. Review analysis output for statistical patterns
3. Generate `avatar_persona.md` with:
   - Language style rules
   - Thinking pattern rules
   - Domain knowledge
   - Decision principles
   - Response templates

### Step 4: Use the Avatar

Copy the generated persona prompt into AI conversations as system prompt, or save as a reusable skill.

## Output Files

| File | Description |
|------|-------------|
| `collected_content.json` | Structured data with full content |
| `text_corpus.md` | All text in readable markdown |
| `summary.json` | Collection statistics |
| `avatar_style_profile.md` | Detailed style analysis report |
| `avatar_persona.md` | Ready-to-use system prompt |

## Tips

- **Start with 500 comments**: If the user has many comments, sampling 500 is usually enough for style extraction
- **Pages are more valuable than comments for domain knowledge**: Pages contain original thinking; comments contain communication style
- **Iterate**: After using the persona, collect feedback and refine the prompt
- **Privacy**: All data stays local; nothing is sent to external services except KMS API calls

## Example Persona Structure

A good persona prompt should include:

1. **Core Identity**: Who the user is, their role, domain expertise
2. **Language Style**: Sentence length, tone, favorite expressions
3. **Thinking Patterns**: How they analyze problems, make decisions
4. **Domain Knowledge**: Products, models, frameworks they use
5. **Decision Principles**: What they value, what they oppose
6. **Response Templates**: How they reply to different types of content
7. **Prohibitions**: What they would never say or do
