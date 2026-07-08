# Resource Contract

本文档定义所有技能调用 type=resource 技能时的统一输入输出格式。

## 核心原则

- **统一接口**：所有技能使用相同的输入输出格式
- **可扩展性**：支持未来新增资源类型和内容维度
- **按需获取**：通过 `content_request` 指定需要的内容类型

## 调用方合规约束

- **唯一入口**：资源知识只能通过调用 `type=resource` 技能获取。
- **禁止直读资产**：调用方不得使用 `Read` / `Glob` / `Grep` 直接访问任何 `type=resource` 技能的 `assets/` 目录。
- **只消费契约返回内容**：调用方只能消费 `resource_retrieval_result.matched_resources[*].content` 中承载的资源内容。
- **路径仅为元数据**：`path` / `name` / `type` / `why_matched` / `limitations` 仅用于标识、匹配说明和绑定，不构成直接读文件授权。
- **允许的本地读取例外**：技能可以读取自身的非资源参考文档或运行初始化资产；该例外不适用于任何 `type=resource` 技能的资源资产目录。

## 统一输入格式

```yaml
resource_retrieval_request:
  user_request: <用户需求描述>
  task_state_summary: <任务状态摘要，可选>
  content_request: <内容需求，可选>
  filters: <过滤条件，可选>
    domain: <领域过滤，可选>
    keyword: <关键词过滤，可选>
```

### 字段说明

- `user_request`：必填，用户的需求描述
- `task_state_summary`：可选，当前任务状态摘要
- `content_request`：可选，用中文自然语义描述需要的内容类型
  - 留空或不填：返回资源摘要（默认）
  - 自然语言描述示例：
    - `"使用说明"` / `"如何使用"` / `"使用方法"`
    - `"模型原理"` / `"实现原理"` / `"架构说明"`
    - `"接口规格"` / `"API 文档"` / `"参数说明"`
    - `"配置说明"` / `"如何配置"` / `"配置方法"`
    - `"工作流规划知识"` / `"规划决策"`
    - `"完整内容"` / `"全部内容"` / `"所有信息"`
  - resource 技能会理解中文自然语义并返回对应内容，不限于以上示例
- `filters`：可选，用于快速过滤资源
  - `domain`：可选，领域过滤，如 `"气象"` / `"生信"` / `"材料"` / `"流体"`，非该领域的资源将被快速排除
  - `keyword`：可选，关键词过滤，如 `"预报"` / `"蛋白质"` / `"势函数"`，不包含该关键词的资源将被排除

## 统一输出格式

```yaml
resource_retrieval_result:
  status: success | partial | failed
  query_summary: <需求摘要>
  detected_domain: <领域>
  task_intent: <任务意图>
  matched_resources:
    - type: <具体资源类型>
      path: <资源路径>
      name: <资源名称>
      why_matched: <匹配理由>
      limitations: <使用限制>
      content: <完整的结构化内容或文本>
```

### 字段说明

- `status`：召回状态（success/partial/failed）
- `matched_resources[].content`：resource 技能根据 `content_request` 组织的内容，格式灵活；这是调用方唯一允许直接消费的资源内容载体
- `matched_resources[].path`：资源标识或来源路径，仅用于追踪和绑定；调用方不得据此直接读取底层资源文件

### content 字段格式说明

`content` 的内容由 resource 技能根据 `content_request` 灵活组织：

**1. 默认（content_request 为空）**：返回简短摘要文本
```yaml
content: "Pangu-Weather 是一个基于 3D Earth-Specific Transformer 的全球气象预报模型，支持 1-7 天预报。"
```

**2. 请求特定内容**：返回对应的文本或结构化内容
```yaml
# content_request: "使用说明"
content: "使用 PanguModel.from_pretrained() 加载模型，输入 ERA5 格式的气象场数据..."

# content_request: "模型原理"
content: "Pangu-Weather 采用 3D Earth-Specific Transformer 架构，通过..."
```

**3. 请求完整内容（content_request: "完整内容"）**：返回结构化的多字段内容
```yaml
content:
  summary: "Pangu-Weather 全球气象预报模型"
  principle: "基于 3D Earth-Specific Transformer..."
  usage: "使用 PanguModel.from_pretrained()..."
  api: "输入: (batch, time, lat, lon, var), 输出: (batch, time, lat, lon, var)"
  config: "需要配置 model_path、input_variables、output_variables"
  limitations: "仅支持 0.25° 分辨率，需要 GPU 推理"
```

resource 技能可以根据资源类型自行决定 `content` 的组织方式，只要能清晰传达所需信息即可。

## 使用场景

### orchestrator 调用（获取摘要）

```yaml
resource_retrieval_request:
  user_request: <用户目标>
  task_state_summary: <Task State 摘要>
  content_request: "摘要"
  filters:
    domain: <领域过滤，可选>
```

## 资源使用

### 意图识别阶段

使用 `matched_resources[].content`（摘要形式）理解用户意图。

### 专家召回阶段

将 `matched_resources` 传递给专家技能作为上下文，专家基于资源摘要规划步骤。

### 资源绑定阶段

从 `matched_resources` 选择当前步骤需要的资源，记录到 `Task State.resource_bindings`：

```yaml
resource_bindings:
  - resource_type: <资源来源类型>
    path: <资源路径>
    name: <资源名称>
    purpose: <用于哪个步骤>
```

## 在 orchestrator 中使用资源

### 意图识别阶段

使用 `matched_resources[].content`、`type`、`why_matched` 理解用户意图：

```yaml
intent_profile:
  domain: <基于资源类型推断>
  task_goal: <基于资源摘要理解>
  intent_aspects: <基于资源匹配理由识别>
```

### 专家召回阶段

将 `matched_resources` 传递给专家技能作为上下文，专家基于资源摘要规划步骤。

### 资源绑定阶段

从 `matched_resources` 选择当前步骤需要的资源，记录到 `Task State.resource_bindings`：

```yaml
resource_bindings:
  - path: <资源路径>
    type: <资源类型>
    purpose: <用于哪个步骤>
    selected_by: <orchestrator | planner | executor>
```

### 执行交接阶段

将绑定的资源标识和已获取内容传递给执行技能；若执行技能需要更深内容，必须重新调用对应的 `type=resource` 技能获取，不得沿着 `path` 直接读取资源资产文件。

## 资源召回合规检查（阻塞性）

在 orchestrator 阶段一（资源召回与意图识别）中，调用方必须通过以下检查点后方可进入下一阶段：

- [ ] 已向 type=resource 技能发出 `resource_retrieval_request`
- [ ] 已收到 `resource_retrieval_result` 并确认 `status`
- [ ] 调用方未使用 `Read` / `Glob` / `Grep` 直接访问任何 resource 技能 `assets/` 下的文件
- [ ] 调用方只基于 `matched_resources[*].content` 消费资源内容，未在契约外引用、概括或拼接资源内容
- [ ] 调用方不得在输出 `resource_retrieval_request` 之前消费原语内容

## 资源冲突处理

- **多个候选**：保持为 candidate，交由专家融合阶段排序
- **契约冲突**：标记为 conflict，不要自行融合
- **需要详细内容**：在 handoff 中说明还缺少什么内容，由执行技能重新调用对应的 `type=resource` 技能获取

