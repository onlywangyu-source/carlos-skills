---
name: finebi-connector
description: This skill should be used when the user needs to connect to a Fanruan FineBI/FineReport decision platform (URL containing /webroot/decision) and read/report data. Trigger phrases include: 读取FineBI数据、FineReport数据、帆软报表、决策平台数据、BI数据查询、报表数据导出、查询FineBI上的数据、FineBI报表、webroot/decision 等.
---

# FineBI/FineReport 数据连接器

## Overview

连接帆软 FineBI/FineReport 决策平台，读取报表数据、数据集、SQL查询结果。

## Authentication

支持两种认证方式，按优先级使用：

### 方式一：开放平台 API 密钥（推荐）

在决策平台「管理系统 > 应用管理」中创建应用，获取 `client_id` 和 `secret`。

请求时在 Headers 中携带：
```
client_id: <应用ID>
secret: <应用密钥>
```

### 方式二：网页登录（Cookie 认证）

当没有开放平台密钥时，使用用户名密码登录获取 Session Cookie。

基础 URL: `https://bi.finereporthelp.com/webroot/decision`

## API 基础信息

- 基础 URL 前缀: `https://bi.finereporthelp.com/webroot/decision/sp/client/api/`
- 完整请求格式: `<基础URL前缀><API路径>`

## 核心能力

### 1. SQL 数据服务

执行指定数据源的 SQL 语句并返回结果。

- **API 路径**: `sql/data`
- **方法**: `GET`
- **参数**:
  - `connection`: 数据源连接名称
  - `sql`: 执行的 SQL 语句

### 2. 报表数据集服务

读取报表模板中定义的数据集。

- **API 路径**: `ds/data`
- **方法**: `GET`
- **参数**:
  - `report`: 报表模板路径（相对于 `reportlets`，如 `GettingStarter.cpt`）
  - `dsName`: 数据集名称（如 `ds1`）
- **传参方式**:
  - URL 参数: `?地区=华北`
  - Body: `{"地区":"华北"}`

### 3. 报表数据服务

读取报表单元格数据。

- **API 路径**: `list/report/data`
- **方法**: `GET`
- **参数**:
  - `report`: 报表路径
  - `tag`: Sheet 名称

### 4. 报表分组数据服务

以分组格式读取报表数据（title + items）。

- **API 路径**: `group/report/data`
- **方法**: `GET`
- **参数**: 同报表数据服务

### 5. 填报服务

向填报模板写入数据。

- **API 路径**: `write/report/data`
- **参数**:
  - `report`: 填报模板路径

## 使用流程

1. 确认认证方式（优先使用开放平台 API 密钥）
2. 确定需要调用的数据服务类型
3. 构造请求参数
4. 执行 API 调用
5. 解析返回的 JSON 数据

## Python 脚本使用

使用 `scripts/query_finebi.py` 执行查询：

```bash
python3 scripts/query_finebi.py --base-url "https://bi.finereporthelp.com/webroot/decision" --client-id "xxx" --secret "xxx" --service "ds/data" --params '{"report":"GettingStarter.cpt","dsName":"ds1"}'
```

或使用网页登录方式：

```bash
python3 scripts/query_finebi.py --base-url "https://bi.finereporthelp.com/webroot/decision" --username "carlos@fanruan.com" --password "Cherry320" --service "ds/data" --params '{"report":"GettingStarter.cpt","dsName":"ds1"}'
```

## 注意事项

- Headers 中的字段名必须是 `client_id`，不是 `clientId`
- 生产环境请新建 API 并选择对应数据服务，避免直接使用 Demo 接口（重启后会重置）
- 报表数据服务不适用于复杂模板或大数据量场景
- 多行批量填报需要安装「数据工厂数据集插件」

## Resources

### scripts/
- `query_finebi.py`: 通用查询脚本，支持 API 密钥和网页登录两种认证方式

### references/
- `api_docs.md`: FineReport 开放平台 API 详细文档
