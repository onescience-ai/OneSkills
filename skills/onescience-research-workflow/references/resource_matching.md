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
2. **规划决策**：如果当前要做节点设计、候选比较、风险判断、能力断言或限制断言，而摘要不足以支撑决定，则必须调用 `type=resource`，默认请求 `工作流规划知识`
3. **shortlist 深化**：如果已 shortlist 到个别候选，但仍缺少决定性接口、约束或适配信息，则升级到 `content_request: "完整内容"`
4. **禁止替代**：不得因为“对某个模型很熟”或“本地知识文件里提到过”就直接选资源；领域知识文件只能辅助理解，不能直接推导具体资源适用性
5. **来源可追溯**：每个 `selected_resource`、`why_selected`、`limitation`、`risk` 都必须能追溯到已有 `matched_resources` 或新的 `type=resource` 调用

## 资源选择原则

1. 优先使用匹配资源：使用 `matched_resources` 中的资源
2. 基于领域选择：根据 `domain_route` 选择适合的模型和数据管道
3. 考虑限制条件：注意 `limitations` 中的使用限制
4. 最小资源集合：只选择必需的资源，不过度规划

## 冲突处理

- 多个候选 → 选择置信度最高的
- 资源不足 → 标记为 `missing_inputs`
- 版本冲突 → 记录到 `risks`
