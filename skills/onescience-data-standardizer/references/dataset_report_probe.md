# `dataset_report` 工具探测与调用协议

## 背景

宿主 Agent（如 Claude Code / Codex / OpenCode / Trae / Qoder 等）可能提供名为 `dataset_report` 的工具，用于把本地生成的 AI-Ready 数据集元信息上报到 OneScience 平台。本技能在完成注册后**自动探测并调用**该工具，不假设其一定存在。

## 探测方式

`scripts/report_probe.py::probe()` 按优先级尝试：

### 路径 1：宿主 Agent 工具清单自省

若运行环境暴露工具清单（例如通过 `list_tools` / `available_tools` / MCP `tools/list`），查找 `name == "dataset_report"` 的条目。命中即认为可用。

### 路径 2：约定环境变量

检查 `ONESCIENCE_DATASET_REPORT_ENDPOINT`：
- 存在且非空 → 视为 HTTP 上报端点，走 REST 调用路径。
- 不存在 → 跳过。

### 路径 3：约定 CLI

检查 `PATH` 中是否存在 `onescience-dataset-report` 可执行文件：
- 存在 → 走 subprocess 调用路径。
- 不存在 → 跳过。

### 路径 4：Python 模块

尝试 `import onescience.report.dataset_report`：
- 成功且模块含 `report(name, target_dir, source_dir)` 函数 → 走 Python 直调路径。
- 失败 → 跳过。

四条路径全部未命中 → `dataset_report_called: false`，主流程不阻断。

## 调用 Payload

固定为三字段（对齐用户示例，`source_dir` 为**附加**字段以便平台追溯）：

```json
{
  "name": "ERA5",
  "target_dir": "/home/user/onedata/era5-ai-ready",
  "source_dir": "/public/share/onestore/onedatasets/ERA5"
}
```

- `name` / `target_dir`：**必需**，来自 `execution_result.artifacts`。
- `source_dir`：**始终携带**，即使原始用户示例中未强制要求；平台侧可选择忽略。

## 调用方式

### 路径 1（宿主工具）

通过宿主 Agent 提供的工具调用机制触发。本技能不直接持有工具句柄，而是**在 `execution_result.observation.next_recommendation` 中建议 orchestrator 或宿主立即调用**，同时把 payload 序列化到 `artifacts.dataset_report_payload`。

若宿主 Agent 支持在 skill 内部直接调用工具（例如通过 MCP client），`report_probe.py` 会尝试直调；失败降级为"建议模式"。

### 路径 2（HTTP 端点）

```python
requests.post(
    os.environ["ONESCIENCE_DATASET_REPORT_ENDPOINT"],
    json=payload,
    timeout=30,
    headers={"Authorization": f"Bearer {os.environ.get('ONESCIENCE_API_TOKEN', '')}"}
)
```

响应 `2xx` 视为成功；其他视为失败但不阻断主流程。

### 路径 3（CLI）

```bash
onescience-dataset-report --name <name> --target-dir <target> --source-dir <source>
```

退出码 0 视为成功。

### 路径 4（Python 模块）

```python
from onescience.report.dataset_report import report
report(name=payload["name"], target_dir=payload["target_dir"], source_dir=payload["source_dir"])
```

无异常视为成功。

## 失败处理

- 探测失败（工具不存在）：`dataset_report_called: false`，`observation.next_recommendation` 追加 `"dataset_report tool not available on this host; registry entry has been written locally"`。
- 探测成功但调用失败：`dataset_report_called: false`，`observation.dataset_report_error: <异常字符串>`，主流程仍返回 `status=success`（因为 AI-Ready 数据集与本地注册均已完成）。
- 调用超时（30s）：视为失败，同上。

## 幂等

- 同一 `(name, target_dir)` 多次上报由平台侧去重；本技能不做客户端幂等控制。
- 若用户重跑转换（例如 raw 数据更新），本技能会重新注册并重新上报，`updated_at` 递增。

## 观测输出

`execution_result.observation` 必须包含：

```yaml
dataset_report:
  available: <bool>
  probe_method: <host_tool|env_endpoint|cli|python_module|none>
  called: <bool>
  payload:
    name: <...>
    target_dir: <...>
    source_dir: <...>
  response: <可选，成功时的返回值摘要>
  error: <可选，失败时的异常字符串>
```

## 安全与隐私

- Payload 中只包含路径与数据集名，**不含**任何用户凭据、token、文件内容。
- 若 `ONESCIENCE_DATASET_REPORT_ENDPOINT` 使用 HTTP（非 HTTPS），在 `observation.risks` 中标注 `insecure_transport`，但仍执行调用（由用户/平台自行判断）。
- 本技能不缓存、不转发上报响应中的任何敏感字段。
