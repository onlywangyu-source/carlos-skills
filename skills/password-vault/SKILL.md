---
name: password-vault
description: Manage and retrieve the user's account credentials and passwords. Use this skill when the user asks to store, update, retrieve, or manage passwords, API tokens, or account credentials. Trigger phrases include "记录密码", "存密码", "我的密码", "账号信息", "credentials", "password", "token", "API key".
agent_created: true
---

# Password Vault

## Overview

This skill stores the user's account credentials in a local skill file. All passwords are stored in plain text within this skill for retrieval by the agent. **This is for convenience only — do not store highly sensitive credentials here.**

## Stored Accounts

### GitHub

| Property | Value |
|----------|-------|
| **Platform** | GitHub |
| **Username** | `onlywangyu-source` |
| **Email** | `onlywangyu@gmail.com` |
| **Password** | `Cherry2026!Git` |
| **Profile URL** | https://github.com/onlywangyu-source |

### 帆软 KMS

| Property | Value |
|----------|-------|
| **Platform** | 帆软 KMS (Confluence) |
| **Username** | `carlos` |
| **URL** | https://kms.fineres.com/ |

### 腾讯云服务器

| Property | Value |
|----------|-------|
| **Platform** | Tencent Cloud CVM |
| **IP** | `111.229.206.147` |
| **SSH User** | `ubuntu` |
| **SSH Key** | `~/.ssh/WBmiyao.pem` |
| **VNC Password** | `6WHrGMd54uDiZ` |

## SSH Keys

| Purpose | Public Key File | Private Key File |
|---------|----------------|------------------|
| GitHub | `~/.ssh/id_ed25519_github.pub` | `~/.ssh/id_ed25519_github` |
| 腾讯云 | `~/.ssh/id_ed25519.pub` | `~/.ssh/id_ed25519` |
| 腾讯云备用 | N/A (PEM format) | `~/.ssh/WBmiyao.pem` |

### 企业微信会话存档

| Property | Value |
|----------|-------|
| **Platform** | 企业微信 (WeCom) |
| **企业 ID (CorpID)** | `ww1cfe92ce0552bbe8` |
| **Secret** | `rWsGUeafmS-_Q83aLoSqNVk5vxkv-osHsFsxGPdmq1M` |
| **RSA 私钥** | 已部署至服务器 `/home/ubuntu/.hermes/private.pem`（PKCS#8 格式） |
| **解密填充方式** | PKCS1v15（非 OAEP） |
| **用途** | 会话存档 (Message Archive) |

## Workflows

### Add New Credential

When user says "记录 XX 账号" or "存密码":
1. Ask for platform, username, password, and any other fields
2. Append to the "Stored Accounts" section above
3. Update the skill file via Write tool

### Retrieve Credential

When user asks "我的 XX 密码是多少" or "查看账号信息":
1. Look up the account in the table above
2. Return the requested information

### Update Credential

When user says "更新 XX 密码" or "修改账号":
1. Use Read tool to read this skill file
2. Use Edit tool to update the specific field
3. Confirm the change with the user
