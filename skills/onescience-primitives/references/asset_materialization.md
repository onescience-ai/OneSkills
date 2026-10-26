# 内容组织与资产物化细则（从 SKILL.md 剥离）

> 对应 SKILL.md 召回流程步骤 7 及输出格式中的资产规则。**当 `content_request` 非摘要（使用说明/规格说明/完整内容/参考资料等）或请求含 `include_execution_assets: true` 时，必须先读取本文再组织输出**。

## 步骤 7：逐个组织内容

对每个命中的资源，按 `content_request` 分别读取并填充该资源的 `content` 字段：

- 留空或 `"摘要"`：优先只读取 `metadata.json`，生成简短摘要，`description` 字段的关键信息不进行过度压缩
- `"使用说明"`：读取 `usage.md`（若存在）；若不存在且存在 `knowledge.md`，则读取 `knowledge.md`
- `"规格说明"`：读取 `spec.md`（若存在）；若不存在且存在 `knowledge.md`，则读取 `knowledge.md`
- `"工作流规划知识"`：读取 `workflow_planning.md`（若存在）；若不存在且存在 `knowledge.md`，则读取 `knowledge.md`
- `"完整知识正文"`：读取 `knowledge.md`（若存在）；这是灵活单文档形态卡片的完整正文
- `"参考资料"` / `"扩展知识"`：只读取 `metadata.json` 中 `knowledge_assets` 声明的 `references/` 文件，并按主题组织返回
- `"完整内容"`：读取 `metadata.json`、`spec.md`、`usage.md`、`workflow_planning.md` 及 `knowledge.md`（若存在）和 `knowledge_assets` 索引；不得因为请求完整内容而自动返回全部参考文件或任意脚本。当目录中仅有 `metadata.json` + `knowledge.md` 时，`knowledge.md` 即完整正文，必须读取
- `"完整参考资料"`：在路径、大小和 SHA-256 校验通过后，读取 `knowledge_assets` 声明的参考文件；大文件按物化规则处理

当且仅当 `include_execution_assets: true` 时，按以下子步骤物化受控执行资产：

a. 读取命中资源的 spec.md，定位唯一的一级标题 `# execution_assets`。读取该标题后紧邻的第一个 yaml 代码块，并从根字段 `execution_assets` 获取白名单数组。不得从其他章节、自然语言、表格或 scripts/ 目录推测资产。若章节不存在、代码块不存在、YAML 无法解析、根字段缺失或出现重复 `# execution_assets` 标题，则视为白名单不可用。
b. 遍历白名单中的每一项资产声明，以 primitive 目录（即 `skills/onescience-primitives/assets/<domain>/<category>/<resource_name>/`）为基准拼接相对路径，得到资产的绝对磁盘路径。
c. 对每个资产执行：
   ① 检查文件是否存在。不存在时，该资产的 `status` 标记为 `unavailable`，`reason` 填 `file_not_found`，跳过后续校验。
   ② 读取文件原始内容，计算 SHA-256 并与白名单中的 `sha256` 比对。不匹配时，`status` 标记为 `failed`，`reason` 填 `sha256_mismatch`（记录期望值与实际值），不返回该资产的内容，不挂载到结果。
   ③ 校验通过后：
      - 若文件内容 ≤ 64 KiB，直接将原文填充到该资产的 `content` 字段，`status` 标记为 `available`。
      - 若文件内容 > 64 KiB，将资产物化到当前工作区的 `.onescience_assets/<primitive_name>/<version>/` 目录（保留原始文件名），`status` 标记为 `materialized`，`materialized_path` 填写物化后的绝对路径，`content_size_bytes` 填写文件字节数。`content` 字段留空。
d. 遍历完成后，汇总所有资产的状态摘要：统计 `available`、`materialized`、`unavailable`、`failed` 四类计数。
e. 即使部分资产不可用或校验失败，也必须返回可用/已物化部分，并在结果中附完整的逐资产状态列表。不得因单个资产失败而丢弃全部可用资产。
f. 全部白名单资产均不可用时，该资源的 `execution_assets` 仍返回，但每一项 `status` 均为 `unavailable` 或 `failed`，并在 `limitations` 中明确说明原因。

## `content` 完整格式（仅当 `content_request` 为 `"完整内容"` 时）

```yaml
content:
  metadata: <metadata.json 内容>
  spec: <spec.md 内容>
  usage: <usage.md 内容>
  workflow_planning: <workflow_planning.md 内容>
  knowledge_assets:
    - path: <metadata.json 的 knowledge_assets 白名单中的相对路径>
      title: <参考资料标题>
      purpose: <该资料解决的问题>
      source: <来源文件或上游文档>
      sha256: <白名单声明的校验值>
      status: <available | materialized | unavailable | failed>
      content: <仅 status=available 且文件较小时填充原文>
      materialized_path: <仅 status=materialized 时填充物化后的绝对路径>
      content_size_bytes: <文件字节数>
  execution_assets:
    - path: < spec.md 的 `# execution_assets` 结构化白名单中声明的相对路径 >
      kind: <python_cli | template | javascript_runtime | license | other>
      media_type: <MIME type>
      sha256: <白名单声明的校验值>
      status: <available | materialized | unavailable | failed>
      reason: <unavailable/failed 时的原因，如 file_not_found | sha256_mismatch>
      content: <仅 status=available 且 ≤ 64 KiB 时填充原文>
      materialized_path: <仅 status=materialized 时填充物化后的绝对路径>
      content_size_bytes: <status=materialized 时填充文件字节数>
  execution_assets_summary:
    total: <白名单资产总数>
    available: <计数>
    materialized: <计数>
    unavailable: <计数>
    failed: <计数>
```

## 执行资产强制规则

- 只有请求显式包含 `include_execution_assets: true` 时才能返回。
- 只允许 `spec.md 的 # execution_assets 结构化白名单` 中逐项声明的相对路径；拒绝未声明文件、绝对路径、`..` 和路径穿越。
- 规范化后的路径必须仍位于当前 primitive 目录内。
- 返回前校验 SHA-256；不匹配时不返回该资产内容，逐资产标记 `status: failed` 及 `reason: sha256_mismatch`（记录期望值与实际值），但不应影响其他已通过校验的资产。
- 调用方只能消费 `content.execution_assets`，不得沿 `matched_resources[].path` 直接读取文件。
- 大文件处理：≤ 64 KiB 的文本文件直接内联到 `content` 字段；> 64 KiB 的文件（如 3Dmol.js ~150KB、HTML 模板 ~200KB）物化到工作区 `.onescience_assets/<primitive_name>/<version>/` 目录，`status` 设为 `materialized`，通过 `materialized_path` 传递绝对路径。
- 状态汇总：必须同时返回 `execution_assets_summary`，便于调用方在不解析全部资产明细的前提下快速判断整体可用性。
- 部分失败不阻塞全部：只要至少有一个核心资产（如 `render_complex_structure.py`）`available` 或 `materialized`，结果 `status` 可为 `partial` 而非 `failed`，让调用方自行降级决策。

## 知识资产强制规则

- `references/` 只承载可阅读的领域知识、API 参考、方法说明、示例和来源材料，不承载默认可执行代码。
- 每个参考文件必须在 `metadata.json` 的 `knowledge_assets` 白名单中声明 `path`、`title`、`purpose`、`source`、`sha256` 和 `media_type`。
- 只允许相对于当前 primitive 目录的路径；拒绝绝对路径、`..`、未声明文件和路径穿越。
- 默认摘要和完整内容只返回参考资料索引；只有 `content_request` 明确请求 `参考资料` 或 `完整参考资料` 时才读取其正文。
- 参考资料返回前校验 SHA-256；失败时标记 `status: failed`，不得静默使用未校验内容。
- 参考资料与执行资产分开统计、分开授权；读取参考资料不会授予执行权限。
