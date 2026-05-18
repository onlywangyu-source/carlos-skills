---
name: tencent-cloud-server
description: Connect and manage the user's Tencent Cloud server (CVM) via SSH. Use this skill ONLY when the user explicitly mentions their "云服务器" (cloud server), "腾讯云服务器", or the specific IP 111.229.206.147. Do NOT trigger on generic "服务器" mentions. Trigger phrases include "帮我在我的云服务器上...", "ssh到我的云服务器", "在我的云服务器上执行", "部署到腾讯云服务器", "查看我的云服务器状态", and any request explicitly involving the Tencent Cloud server.
agent_created: true
---

# Tencent Cloud Server

## Overview

This skill provides the connection details and procedures for accessing the user's Tencent Cloud CVM (Cloud Virtual Machine) server via SSH. It enables remote command execution, file management, deployment workflows, and server administration tasks.

## Server Specs (from Tencent Cloud Console + Live Probe)

| Property | Value |
|----------|-------|
| **Instance Name** | Ubuntu-BlZa |
| **Instance ID** | lhins-6kx3c4ww |
| **Status** | 运行中 (Running) |
| **Region** | 上海四区 (Shanghai Zone 4) |
| **Public IPv4** | `111.229.206.147` |
| **IPv6** | Not enabled |
| **CPU** | 2核 (2 Cores) |
| **Memory** | 4GB (3.6Gi usable) |
| **System Disk** | SSD云硬盘 60GB (59G usable, 14% used) |
| **Bandwidth** | 5Mbps (流量包 500GB/月) |
| **Expiration** | 2027-05-16 21:40:43 |
| **Auto-Renewal** | Enabled |

## OS & Environment

| Property | Value |
|----------|-------|
| **OS** | Ubuntu 24.04.4 LTS (Noble Numbat) |
| **Kernel** | Linux 6.8.0-117-generic |
| **Architecture** | x86_64 |
| **Default User** | `ubuntu` |
| **Shell** | zsh (from `.zshrc`) |

## Connection Info

| Property | Value |
|----------|-------|
| **SSH Host** | `ubuntu@111.229.206.147` |
| **SSH Port** | 22 |
| **Auth Method** | SSH Key |
| **Private Key Path** | `~/.ssh/WBmiyao.pem` (or `/Users/wangyu/Downloads/WBmiyao.pem`) |
| **VNC Password** | `6WHrGMd54uDiZ` (for Tencent Console VNC login only) |

## Quick Start

To execute commands on the remote server, use `ssh` with the private key:

```bash
ssh -o StrictHostKeyChecking=no -i ~/.ssh/WBmiyao.pem ubuntu@111.229.206.147 "<command>"
```

For file transfers, use `scp` with the private key:

```bash
# Upload file
scp -o StrictHostKeyChecking=no -i ~/.ssh/WBmiyao.pem local-file ubuntu@111.229.206.147:/remote/path

# Download file
scp -o StrictHostKeyChecking=no -i ~/.ssh/WBmiyao.pem ubuntu@111.229.206.147:/remote/path local-file
```

## Workflow Decision Tree

```
User request explicitly mentions "云服务器" / "腾讯云" / IP 111.229.206.147?
├── "Connect / SSH to my cloud server"
│   └── Use: ssh -i <key> ubuntu@111.229.206.147 "<command>"
├── "Run command on my cloud server"
│   └── Use: ssh -i <key> ... "<command>"
├── "Check my cloud server status"
│   └── Run: uptime, df -h, free -h, top (non-interactive)
├── "Deploy / Upload to my cloud server"
│   └── Use: scp -i <key> ...
├── "Download from my cloud server"
│   └── Use: scp -i <key> (reverse direction)
└── "Manage Hermes on my cloud server"
    └── Use: ssh to run docker commands in /opt/hermes
```

## Installed Software

| Software | Version | Notes |
|----------|---------|-------|
| Docker | 29.1.3 | Engine installed, no running containers currently |
| Python | 3.12.3 | System Python |
| Node.js | Not installed | `.npmrc` exists but no node binary found |
| Nginx | Not installed | No /var/www directory |
| Java | Not installed | |
| Go | Not installed | |

## Important Directories

| Path | Owner | Purpose |
|------|-------|---------|
| `/opt/hermes` | ubuntu | Hermes application directory |
| `/opt/hermes-data` | ubuntu | Hermes data directory |
| `/home/ubuntu/.hermes` | ubuntu | Hermes user config/cache |
| `/home/ubuntu/.ssh` | ubuntu | SSH keys and config |

## Common Tasks

### Check System Status
```bash
ssh -o StrictHostKeyChecking=no -i ~/.ssh/WBmiyao.pem ubuntu@111.229.206.147 "uname -a && uptime && df -h && free -h"
```

### List Running Processes
```bash
ssh -o StrictHostKeyChecking=no -i ~/.ssh/WBmiyao.pem ubuntu@111.229.206.147 "ps aux --sort=-%mem | head -20"
```

### Check Docker Status
```bash
ssh -o StrictHostKeyChecking=no -i ~/.ssh/WBmiyao.pem ubuntu@111.229.206.147 "docker ps -a && docker system df"
```

### Check Hermes Directory
```bash
ssh -o StrictHostKeyChecking=no -i ~/.ssh/WBmiyao.pem ubuntu@111.229.206.147 "ls -la /opt/hermes && ls -la /opt/hermes-data"
```

### Update System Packages
```bash
ssh -o StrictHostKeyChecking=no -i ~/.ssh/WBmiyao.pem ubuntu@111.229.206.147 "sudo apt update && sudo apt upgrade -y"
```

### Upload a File
```bash
scp -o StrictHostKeyChecking=no -i ~/.ssh/WBmiyao.pem /local/path/file ubuntu@111.229.206.147:/home/ubuntu/
```

### Download a File
```bash
scp -o StrictHostKeyChecking=no -i ~/.ssh/WBmiyao.pem ubuntu@111.229.206.147:/home/ubuntu/file /local/path/
```

## Security Notes

- The private key file (`WBmiyao.pem`) must have `chmod 600` permissions. SSH will reject keys with overly permissive permissions.
- Always use `-o StrictHostKeyChecking=no` for automated connections (first-time or ephemeral environments).
- Be cautious with destructive commands (rm, dd, mkfs, etc.) — always confirm with the user before execution.
- The VNC password `6WHrGMd54uDiZ` is ONLY for Tencent Cloud Console VNC login, NOT for SSH.
