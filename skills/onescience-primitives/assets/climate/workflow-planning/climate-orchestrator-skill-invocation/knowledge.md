# skill工具接口契约与调用模式

## 适用范围
- **触发条件**：编排智能体需要调用type=expert技能（如onescience-research-workflow）进行任务规划时
- **适用场景**：OneScience编排流程中的expert_recall阶段，需要获取专家规划方案
- **不适用场景**：调用type=executor技能时（executor技能直接执行任务，不需要planning_request）

## 输入
- **skill名称**：type=expert技能的标识符，如"onescience-research-workflow"
- **planning_request负载**：结构化请求对象，包含以下必填字段：
  - `from_skill`：调用来源技能标识
  - `task_state_summary`：任务状态摘要
  - `intent_profile`：用户意图分析
  - `matched_resources`：已召回的资源列表
  - `assigned_aspect`：分配给专家的方面/领域

## 输出
- **planner_proposal**：专家技能返回的规划方案，包含工作流节点、资源绑定、依赖关系和执行建议
- **失败响应**：当planning_request未正确传递时，skill工具仅返回技能文档摘要，不执行规划逻辑

## 流程节点
1. **准备planning_request** → 构造包含所有必填字段的结构化请求
2. **调用skill工具** → 传递skill名称和planning_request负载
3. **验证返回内容** → 检查返回的是planner_proposal还是文档摘要
4. **错误处理** → 若返回文档摘要，说明调用参数不正确，需修正后重试

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| skill工具调用格式 | `skill(name="xxx", planning_request={...})` | 归因报告 | 完整调用需同时传name和planning_request |
| 仅传name时行为 | 返回技能文档摘要 | 归因报告 | 不触发规划逻辑 |
| planning_request必填字段 | from_skill, task_state_summary, intent_profile, matched_resources, assigned_aspect | onescience-research-workflow SKILL.md | 缺少任一字段可能导致规划失败 |

## 边界与分流
- **type=expert技能**：必须传递planning_request负载，否则退化为文档加载
- **type=executor技能**：直接传name即可，executor不参与规划流程
- **skill工具行为**：在仅有name参数时仅加载技能文档内容，不执行技能逻辑

## 质量检查
- **调用成功验证**：返回内容包含planner_proposal结构
- **调用失败检测**：返回内容为技能文档摘要文本
- **连续失败计数**：连续3次相同无效调用应触发降级策略

## 回退策略
当skill工具连续返回文档摘要时：
1. 检查planning_request字段是否完整
2. 若字段完整仍失败，跳过专家召回，进入直接执行模式
3. 基于已召回的原语工作流节点构建Global Plan

## 资源召回建议
- **召回时机**：当编排智能体需要调用type=expert技能进行任务规划时
- **配套资源**：onescience-research-workflow（规划专家）、onescience-primitives（资源召回）

## 证据来源
[1] 归因报告 Issue 1：skill工具的接口契约与调用模式，agent-events.log:97-1205
[2] agent-final.txt:24：编排智能体在reasoning中构造了planning_request但从未将其格式化为工具调用参数
