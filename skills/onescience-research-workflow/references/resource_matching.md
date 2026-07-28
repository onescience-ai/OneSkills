# Resource Matching

本文档定义如何在工作流规划中发现和选择资源。

## 资源获取

### 调用约束

- 工作流规划所需的资源知识只能通过调用 `type=resource` 技能获取。
- 规划阶段只能消费 `resource_retrieval_result.matched_resources[*].content` 中返回的内容。
- 不得使用 `Read` / `Glob` / `Grep` 直接访问任何 resource skill 的 `assets/` 目录，也不得把返回的 `path` 当作本地可读路径。

### 调用 type=resource 技能

设置 `content_request` 获取需要的内容：

```yaml
resource_retrieval_request:
  user_request: <用户科研目标>
  task_state_summary: <Task State 摘要>
  content_request: "完整内容，基础信息除外"  # 获取工作流规划知识
  filters:
    domain: <领域过滤，可选>
    keyword: <关键词过滤，可选>
```

### 接收输出

```yaml
resource_retrieval_result:
  status: success | partial | failed
  matched_resources:
    - type: <具体资源类型>
      path: <资源路径>
      name: <资源名称>
      why_matched: <匹配理由>
      limitations: <使用限制>
      content: <完整的结构化内容或文本>
```

## 强制召回与升级规则

1. **粗路由**：如果当前只需要判断大方向，且 orchestrator 已提供的 `matched_resources` 摘要足以支撑该判断，可以先复用摘要
2. **规划决策**：如果当前要做路线选择、节点设计、候选比较、风险判断、能力断言或限制断言，而摘要不足以支撑决定，则必须调用 `type=resource`，默认请求能支撑规划与决策的知识，而不是只取原语级局部摘要
3. **shortlist 深化**：如果已 shortlist 到个别候选，但仍缺少决定性接口、约束或适配信息，则升级到 `content_request: "完整内容"`
4. **禁止替代**：不得因为“对某个模型/工具/数据格式/模拟方法很熟”或“本地知识文件里提到过”就直接选资源；领域知识文件只能辅助理解，不能直接推导具体资源适用性
5. **来源可追溯**：每个 `selected_resource`、`why_selected`、`limitation`、`risk` 都必须能追溯到已有 `matched_resources` 或新的 `type=resource` 调用
6. **相关性不等于充分性**：`why_matched` 或“符合任务”的判断只表示资源可进入候选，不表示可以直接落入 proposal；如果缺少具体规划决策知识、领域决策知识、使用知识、接口契约、环境约束或验证规则，必须继续召回
7. **执行缺口升级**：如果计划中出现应用、命令行工具、库、数据管道、格式转换器、模拟器、算法/模型、分析脚本、建模/运行脚本、评估器或报告模板，而当前环境/Task State 未证明其已存在，必须召回足以规划安装、实现、适配或替代路线的知识

## 充分性检查清单

只有当资源内容可以支撑以下问题时，才能进入最终 proposal：

- 路线选择：为什么选该资源/路线，以及主要备选为何不选
- 领域决策：该领域任务需要哪些前置假设、质量指标、数据标准或科学约束
- 使用方式：应用/工具/数据管道/模拟器/模型/分析方法如何安装、调用、配置、传参、读取输入并生成输出
- 实现契约：如果需要生成代码，必须生成哪些文件、函数、CLI、配置、测试或 notebook
- 运行契约：数据契约、配置/参数、运行入口、预处理、后处理、输入 shape/单位、输出 schema 是否明确；若涉及模型，再检查模型资产和运行入口
- 验证与回退：怎样判断阶段成功，失败时何时切换 fallback

任一项会影响当前决策但无法回答时，输出 proposal 前必须补充 `type=resource` 调用；若补充后仍无法回答，写入 `missing_inputs`，不要编造。

## 资源选择原则

1. 优先使用匹配资源：使用 `matched_resources` 中的资源
2. 基于领域选择：根据 `domain_route` 选择适合的数据管道、工具、模拟器、算法/模型、分析方法和验证组件
3. 考虑限制条件：注意 `limitations` 中的使用限制
4. 最小资源集合：只选择必需的资源，不过度规划；但在当前决策范围内不能省略会影响路线、依赖、验证或回退判断的关键知识
5. 可执行性优先：当两个资源都相关时，优先选择能提供完整使用说明、接口契约、验证方式和 fallback 条件的资源；只有资源名、模型名或应用名而无使用细节的资源不得单独支撑执行阶段

## 冲突处理

- 多个候选 → 选择置信度最高的
- 资源不足 → 标记为 `missing_inputs`
- 版本冲突 → 记录到 `risks`
- 环境缺应用/入口 → 规划安装、适配或实现阶段，不得只写“使用该应用”
- 缺代码、脚本、配置或运行入口 → 规划实现/适配阶段，并明确接口、数据契约、参数语义和 smoke test；若涉及模型，再补充模型资产语义
