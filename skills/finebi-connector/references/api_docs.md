# FineReport 开放平台 API 文档

> 来源: https://help.fanruan.com/finereport/doc-view-4932.html

## 认证机制

所有 API 均采用**应用级密钥鉴权**，需在请求头（Headers）中携带以下参数：

| 参数名 | 说明 |
|--------|------|
| `client_id` | 应用ID（在【应用管理】中创建应用后获取） |
| `secret` | 应用密钥（在【应用管理】中创建应用后获取） |

> **注意**：参数名应使用 `client_id`，而非 `clientId`。

## 请求基础格式

**基础URL前缀**（固定部分）：
```
http://<服务器地址>:<端口>/webroot/decision/sp/client/api/
```

**完整请求格式**：
```
<基础URL前缀><API路径>
```

请求方法以各接口定义的 **API方法** 为准（示例中多为 `GET`，填报场景涉及 `POST`）。

## 各类API详细调用示例

### 1. SQL数据服务

- **API路径**：`sql/data`
- **API方法**：`GET`
- **配置参数**：
  - `connection`：数据源连接名称（如 `FRDemo`）
  - `sql`：执行的SQL语句（如 `SELECT * FROM \`销量\` where 地区 = '华东'`）
- **请求示例**：
  ```
  GET http://localhost:8075/webroot/decision/sp/client/api/sql/data
  Headers: client_id=xxx, secret=xxx
  ```

### 2. 报表数据集服务

- **API路径**：`ds/data`
- **API方法**：`GET`
- **配置参数**：
  - `report`：报表模板路径（相对于 `reportlets`，如 `GettingStarter.cpt`）
  - `dsName`：数据集名称（如 `ds1`）
- **传参方式**（二选一）：
  - **Body**：`{"地区":"华北"}`
  - **Params（URL参数）**：`?地区=华北`
- **请求示例**：
  ```
  GET http://localhost:8075/webroot/decision/sp/client/api/ds/data?地区=华北
  Headers: client_id=xxx, secret=xxx
  ```

### 3. 报表数据服务

- **API路径**：`list/report/data`
- **API方法**：`GET`
- **配置参数**：
  - `report`：报表路径（如 `开放平台测试.cpt`）
  - `tag`：Sheet名称（如 `sheet1`）
- **请求示例**：
  ```
  GET http://localhost:8075/webroot/decision/sp/client/api/list/report/data
  Headers: client_id=xxx, secret=xxx
  ```
- **限制**：不适用于复杂或大数据量模板。

### 4. 报表分组数据服务

- **API路径**：`group/report/data`
- **API方法**：`GET`
- **配置参数**：同"报表数据服务"（`report`、`tag`）
- **请求示例**：
  ```
  GET http://localhost:8075/webroot/decision/sp/client/api/group/report/data
  Headers: client_id=xxx, secret=xxx
  ```
- **特点**：输出数据分为 `title` 和 `items` 两部分，数据内容与报表数据服务一致，仅格式不同。

### 5. 填报服务（免预览提交）

- **API路径**：`write/report/data`
- **配置参数**：
  - `report`：填报模板路径（相对于 `reportlets`）

**示例A：单行数据填报**
- 通过 **Params（URL参数）** 传值，模板中定义参数如 `a`、`b`、`c`、`d`：
  ```
  GET/POST http://localhost:8075/webroot/decision/sp/client/api/write/report/data?a=值1&b=值2...
  Headers: client_id=xxx, secret=xxx
  ```

**示例B：多行数据填报**
- 需配合**数据工厂数据集插件**使用。
- 通过 **Body** 传入JSON格式数据，实现批量填报：
  ```
  POST http://localhost:8075/webroot/decision/sp/client/api/write/report/data
  Headers: client_id=xxx, secret=xxx
  Body: <JSON格式数据>
  ```
- 数据工厂配置要点：装载方式为单参数，参数填写 `${body}`，解析方式选择 `json`。

## 使用前提与权限配置

在调用前必须完成以下三步：
1. **API管理**：在基础数据接口中确认或配置API信息，记录 **API路径** 和 **API方法**。
2. **应用管理**：新建应用并记录 **应用ID** 和 **密钥**。
3. **权限管理**：为指定应用开启对应API服务的访问权限。

## 重要注意事项

1. **参数名修正**：Headers 中的应用ID字段名必须为 `client_id`。
2. **避免直接使用Demo接口**：示例中的 `[demo]` 服务在决策系统重启后会重置默认数据。生产环境请通过**新增API**并选择对应数据服务的方式使用。
3. **填报限制**：报表数据服务与报表分组数据服务不适用于复杂模板或大数据量场景。
4. **多行填报依赖**：多行批量填报需要额外安装并配置**数据工厂数据集插件**。
