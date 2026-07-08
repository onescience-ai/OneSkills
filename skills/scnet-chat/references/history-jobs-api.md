# 历史作业列表接口 v3

## 概览

用于查询已归档的历史作业。该接口是跨区域聚合接口，不需要逐区域遍历。

- 服务地址：`https://api.scnet.cn/api/job`
- 接口路径：`POST /v3/jobs/history-job`
- 完整 URL：`https://api.scnet.cn/api/job/v3/jobs/history-job`
- 认证方式：请求头 `token: <ac_token>`，token 来自 `clusterName == "ac"` 的认证信息
- 超时建议：5-15 秒，遇到 SSL EOF/timeout 可重试 2-3 次

## 请求

Headers:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `token` | string | 是 | AC token |
| `Content-Type` | string | 是 | `application/json` |

Body:

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `page` | integer | 是 | 页码，从 1 开始 | `1` |
| `size` | integer | 是 | 每页条数，最大 100 | `10` |
| `clusterId` | long/string | 否 | 区域/集群 ID | `11250` |
| `queue` | string | 否 | 队列名称 | `kshctest` |
| `state` | string | 否 | 作业状态 | `statC` |
| `clusterUserName` | string | 否 | 集群侧用户名 | `helei01` |
| `name` | string | 否 | 作业名称过滤 | `orca-probe` |
| `startTime` | string | 否 | 开始时间，`YYYY-MM-DD HH:MM:SS` | `2026-06-01 00:00:00` |
| `endTime` | string | 否 | 结束时间，`YYYY-MM-DD HH:MM:SS` | `2026-06-30 23:59:59` |

最小请求：

```json
{
  "page": 1,
  "size": 10
}
```

## 响应

成功响应：

```json
{
  "code": "0",
  "msg": "success",
  "data": {
    "total": 19,
    "pages": 10,
    "records": [
      {
        "clusterId": 11250,
        "clusterName": "华东一区【昆山】",
        "id": "116181778",
        "name": "orca-probe-ks",
        "managerId": 1573088268,
        "queue": "kshctest",
        "state": "statC",
        "submitTime": "2026-06-29 12:25:09",
        "startTime": "2026-06-29 12:25:09",
        "endTime": "2026-06-29 12:25:21",
        "source": "history"
      }
    ]
  }
}
```

## 相关接口

### 作业详情

```text
GET /v3/job/{clusterId}/{managerId}/{source}/{id}
```

`source` 允许值：

| 值 | 说明 |
|----|------|
| `active` | 只查实时作业 |
| `history` | 只查历史作业 |
| `all` | 同时覆盖实时和历史作业 |

推荐详情查询使用 `source=all`，例如：

```text
GET /v3/job/11250/1573088268/all/116181778
```

### 批量简要查询

```text
POST /v3/jobs/brief-job
```

请求体按 `clusterId + managerId` 分组，`ids` 为该调度器下的作业 ID 列表，最多 100 个作业标识：

```json
{
  "jobs": [
    {
      "clusterId": 11250,
      "managerId": 1573088268,
      "ids": ["116181778", "116181929"]
    }
  ]
}
```

成功时 `data` 直接返回作业简要信息数组，字段与列表接口一致。

## 注意

- `page` 和 `size` 是 v3 必填参数，不能使用 `pageNo/pageSize`。
- 缓存 token 过期时会返回 `code=402, msg=auth_fail`，应刷新 AC token 后重试一次。
