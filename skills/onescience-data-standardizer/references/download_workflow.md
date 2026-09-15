# ModelScope 下载工作流

本文档定义段 3（ModelScope 下载）的完整流程、缓存约定与失败降级策略。

## 触发条件

- 段 1（显式路径）与段 2（本地探测）均未命中；
- **且** `task_context.allow_download == true` 或 `execution_flags.autonomous_mode == true`；
- 交互式确认（非 autonomous_mode 时）：向用户展示推断的 `repo_id` 与目标缓存目录，等待确认后继续。

## Repo ID 推断

优先级从高到低：

1. `task_context.modelscope_repo_id` 显式提供 → 直接使用。
2. 从 primitives 的 `spec.md` / `usage.md` 中提取（若返回内容包含 `modelscope.cn/datasets/<org>/<name>` 或 `repo_id: <...>` 等模式）。
3. 从 `metadata.json` 的 `provider` / `source` / `provenance` 字段提取。
4. 默认约定：`OneScience/<dataset_name>`（组织名固定为 `OneScience`，与 [marketplace.json](file:///e:/works/zhognkeshuguang/data_management/oneskills-work/.claude-plugin/marketplace.json) 一致）。

推断结果必须记录到 `observation.source_resolution.download_details.repo_id_source`（`explicit | spec_extract | metadata_extract | default_convention`）。

## 缓存目录约定

固定为：`~/.onescience/datasets/<dataset_name>/raw/`

- 若目录已存在且非空 → 视为已下载，跳过下载直接使用（幂等）。
- 若目录存在但为空 → 删除后重新下载。
- 下载过程使用**临时目录**（`~/.onescience/datasets/<dataset_name>/.raw.tmp.<pid>/`），完成后 `os.rename` 到最终位置，避免半完成状态污染缓存。

## 下载执行

### 首选路径：ModelScope Python SDK

```python
from modelscope.hub.snapshot_download import snapshot_download
local_path = snapshot_download(
    repo_id=repo_id,
    repo_type='dataset',
    cache_dir=str(cache_root),   # ~/.onescience/datasets/<name>/
    revision=revision,           # 可选，来自 task_context
)
```

依赖：`pip install modelscope`。SDK 未安装时抛出可诊断异常并降级到 CLI 路径。

### 降级路径：ModelScope CLI

```bash
modelscope download --repo-type dataset --repo-id <repo_id> --local_dir <cache_dir>
```

依赖：`modelscope` CLI 在 `PATH` 中。

### 二级降级：Git LFS

若 SDK 与 CLI 均不可用，且 `repo_id` 能推断出 ModelScope 网页地址：

```bash
git lfs install
git clone https://www.modelscope.cn/datasets/<repo_id>.git <cache_dir>
```

此路径仅在 `task_context.allow_git_lfs_fallback == true` 时启用（默认 false，避免大文件不受控下载）。

## 认证与凭据

- 公开数据集：无需凭据。
- 私有/受限数据集：需要 `MODELSCOPE_API_TOKEN` 环境变量或 `~/.modelscope/credentials`。
- 本技能**不管理凭据**，仅在下载失败且错误信息含 `401/403/authentication` 时，在 `blocked_details` 中提示用户配置凭据。

## 失败降级

| 失败类型 | 处理 |
|---|---|
| SDK/CLI 都不可用 | `status=blocked, blocked_reason=download_failed, blocked_details="modelscope sdk/cli not available; install with: pip install modelscope"` |
| Repo 不存在（404） | `status=blocked, blocked_reason=download_failed, blocked_details="repo not found: <repo_id>"`；同时在 `observation.next_recommendation` 中建议用户核对 repo_id 或手工提供 source_dir |
| 认证失败（401/403） | `status=blocked, blocked_reason=download_failed, blocked_details="authentication required; set MODELSCOPE_API_TOKEN"` |
| 网络中断/超时 | 重试最多 3 次，指数退避（1s / 4s / 16s）；仍失败 → `status=blocked, blocked_reason=download_failed` |
| 磁盘空间不足 | `status=blocked, blocked_reason=download_failed, blocked_details="insufficient disk space; required=<X>, available=<Y>"` |
| 部分文件损坏（checksum mismatch） | 删除缓存目录并重试 1 次；仍失败 → `status=blocked` |

## 幂等与并发

- 同一 `dataset_name` 的下载**必须幂等**：缓存命中即跳过。
- 并发保护：下载前尝试独占创建 `~/.onescience/datasets/<name>/.download.lock`；已被占用时轮询等待最多 30 分钟，超时后 `status=blocked`。

## 观测输出

`observation.source_resolution.download_details` 必须包含：

```yaml
download_details:
  repo_id: <...>
  repo_id_source: explicit | spec_extract | metadata_extract | default_convention
  repo_type: dataset | model
  cache_dir: <绝对路径>
  method: sdk | cli | git_lfs
  bytes_downloaded: <int>
  duration_seconds: <float>
  files_count: <int>
  retries: <int>
```
