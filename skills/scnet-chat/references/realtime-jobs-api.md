# 实时作业列表接口 v3

## 概览

用于查询当前内存中的活跃作业（运行、排队、挂起等非归档作业）。该接口是跨区域聚合接口，不需要逐区域遍历。

- 服务地址：`https://api.scnet.cn/api/job`
- 接口路径：`POST /v3/jobs/active-job`
- 完整 URL：`https://api.scnet.cn/api/job/v3/jobs/active-job`
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
| `state` | string | 否 | 作业状态 | `statR` |
| `clusterUserName` | string | 否 | 集群侧用户名 | `helei01` |
| `name` | string | 否 | 作业名称过滤 | `qe_si_scf` |
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
    "total": 0,
    "pages": 0,
    "records": []
  }
}
```

作业记录字段以 v3 返回为准，常见字段包括：

```text
clusterId, clusterName, id, name, managerId, clusterUserName,
queue, appType, state, submitTime, startTime, runTime, workDir,
source, endTime, exitCode, usedProcNum
```

## 注意

- `page` 和 `size` 是 v3 必填参数，不能使用 `pageNo/pageSize`。
- 缓存 token 过期时会返回 `code=402, msg=auth_fail`，应刷新 AC token 后重试一次。
- 终态作业通常查询 `POST /v3/jobs/history-job`。
