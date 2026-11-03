# 完整性校验与注册表

## 1. 校验口径：可见文件

所有统计（命中判定、文件数、字节数、`content_digest`）都只算**可见文件**：相对根目录的路径中每一段都不以 `.` 开头。

原因是 ModelScope SDK 会在缓存树里留下记账产物（`.lock/`、`._____temp/`、`.mdl`/`.msc`），HuggingFace 的 `local_dir` 布局会留 `.cache/huggingface/`，官网直链解包前后也可能残留归档——这些都不算可见文件。把这些算进去会让中断或空下载看起来"已就绪"，进而让下游拿到半截数据。实现见 `resource_paths.visible_files` / `is_visible_file`。

## 2. 校验项（`fetch_resource.verify`）

| check | 判据 | 何时生效 |
| --- | --- | --- |
| `populated` | 可见文件数 ≥ `max(min_files, 1)` | 恒生效 |
| `size_floor` | 可见文件总字节 ≥ `min_bytes` | `min_bytes > 0` |
| `required_file:<glob>` | 至少一个可见文件的相对路径或文件名匹配该通配式 | 每个 `--required-file` 一条 |

- 通配式按 posix 相对路径与文件名两个口径匹配（`*.nc` 命中任意层级，`train/0001.nc` 精确命中）。
- 全部通过才 `verification.passed=true`；任一项失败 → `blocked_reason=verification_failed`，**保留已落盘目录**（不删，供人工查看），把 `checks` 明细交回调用方决定换 `repo_id` 还是补 `revision`。
- `content_digest = sha256("<相对路径>:<大小>" 逐行拼接)`，用于让下游发现"同一个缓存目录两次运行内容变了"。它不是 provider 官方校验和，不等同于内容正确性证明，`limitations` 要如实说明校验边界。

### 建议的 required_files 用法

| 资源类型 | 建议必需项 |
| --- | --- |
| 气象 NetCDF 数据集 | `*.nc`，另加数据集说明文件（如 `README.md`） |
| MACE / 势模型 | `*.model` 或 `*.pth`；有配置随包发布时加 `*.yaml` |
| checkpoint 目录 | `*.safetensors` 或 `*.ckpt` 或 `*.pt` 任一（按模型卡指定） |
| 只有大小可观的资源 | `--min-bytes` 给一个"明显小于真实发布量"的下界即可，不要拍论文里的精确值 |

没有取证依据时**不要**臆造 `required_files`；缺省只校验"非空 + 有可见文件"，并在 `limitations` 里说明未做语义级校验。

## 3. 注册表 `~/.onescience/resource_registry.json`

路径跟着缓存根走：设了 `ONESCIENCE_RESOURCE_HOME` 时注册表就在该目录下（与 `datasets/`、`models/` 同根，不会出现缓存与索引分居两盘）。

```json
{
  "version": 1,
  "resources": {
    "dataset:era5-tutorial": {
      "name": "era5-tutorial", "kind": "dataset",
      "repo_id": "OneScience/era5-tutorial",
      "repo_id_source": "default_convention",
      "fetch_method": "sdk",
      "provider": "modelscope",
      "local_path": "/home/u/.onescience/datasets/era5-tutorial/raw",
      "files": 12, "bytes": 1073741824,
      "content_digest": "<sha256>", "verified": true,
      "domain": "earth",
      "updated_at": "2026-11-02T10:14:00+0800"
    }
  }
}
```

- 键为 `<kind>:<name>`；写入是幂等 upsert（合并字段、刷新 `updated_at`），只更新不删除历史条目。
- 原子写：先 `<path>.tmp.<pid>` 再 `os.replace`，避免并发写坏 JSON。
- 文件损坏或格式不认识时**重建**为空表继续工作，不阻塞物化流程（原文件已不可靠，静默重建比报错停摆更有用，但要在 `warnings` 里如实记录）。
- 注册表是"本地有什么"的加速索引，不是事实来源：段 2 命中仍要重新数文件、重算 digest，绝不凭注册表里的旧数字直接宣布可用。

## 4. 与其他状态文件的关系

| 文件 | 归属 | 内容 |
| --- | --- | --- |
| `~/.onescience/resource_registry.json` | 本技能 | 原始 dataset/model 的本地位置与指纹 |
| `~/.onescience/data_management.json` | `onescience-data-standardizer` | AI-Ready 标准化后的数据集登记 |
| `.onescience/task_state.json`、`.onescience/gaps.jsonl` | orchestrator | 任务状态与缺口，本技能不写 |

本技能只写第一个，不读写其余两个；需要把原始资源接到标准化链路时，把 `local_path` 作为 `source_dir` 交给调用方去调度（见 `provision_contract.md` 第 4 节）。
