# 编排智能体直接执行模式

## 适用范围
- **触发条件**：专家技能调用失败或无法触发（如onescience-research-workflow未返回planner_proposal）
- **适用场景**：OneScience编排流程中的备选规划路径，当专家规划路径不可用时自动降级
- **不适用场景**：专家规划路径正常工作时（优先使用专家规划）

## 输入
- **已召回原语**：从onescience-primitives获取的工作流节点定义（如cmip6-basin-runoff-long-term-projection的6节点工作流）
- **任务上下文**：用户目标、约束条件、相关产物
- **executor技能列表**：所有可用的type=executor技能标识

## 输出
- **Global Plan**：包含所有工作流节点及其执行顺序的全局计划
- **Next Step Spec**：下一个待执行步骤的详细规范
- **execution-manifest.json**：执行清单文件

## 流程节点
1. **跳过专家规划** → 识别到专家技能调用失败后，直接进入直接执行模式
2. **提取原语工作流节点** → 从已召回的原语中提取workflow_nodes
3. **枚举executor技能** → 遍历所有type=executor技能的SKILL.md，建立能力台账
4. **构建Global Plan** → 基于原语工作流节点和executor能力，生成包含所有步骤的全局计划
5. **选择Next Step Spec** → 按节点顺序选择第一个待执行步骤
6. **生成execution-manifest.json** → 输出执行清单供后续流程使用

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 原语工作流节点 | cmip6-basin-runoff-long-term-projection的s01-s06 | 归因报告 | agent-events.log:56-65显示成功召回原语 |
| executor技能类型 | type=executor | OneScience SKILL.md | 承载具体执行任务的技能 |
| Global Plan格式 | 包含所有节点的有序列表 | 最佳实践 | 每个节点绑定具体executor技能 |
| execution-manifest.json | 执行清单文件 | OneScience规范 | 记录所有待执行步骤 |

## 边界与分流
- **专家规划路径**：orchestrator→expert skill→planner_proposal→Global Plan→executor steps（优先）
- **直接执行路径**：orchestrator→基于原语workflow_nodes→executor inventory→Global Plan→executor steps（备选）
- **降级触发条件**：expert_recall连续失败（如3次相同无效调用）

## 质量检查
- **Global Plan完整性**：包含原语定义的所有工作流节点
- **executor绑定正确性**：每个节点绑定的executor技能具有执行该节点的能力
- **execution-manifest.json生成**：文件格式正确，包含所有必要字段

## 回退策略
当直接执行模式也失败时：
1. 记录详细的失败原因和上下文
2. 向用户报告任务无法自动恢复
3. 提供手动配置execution-manifest.json的入口

## 资源召回建议
- **召回时机**：当专家技能调用失败且需要继续推进任务时
- **配套资源**：onescience-primitives（原语召回）、onescience-runtime（任务执行）

## 证据来源
[1] 归因报告 Issue 3：任务产物目录完全为空，agent-events.log:56-65
[2] agent-events.log:56-65：编排智能体成功召回原语（cmip6-basin-runoff-long-term-projection），但从未进入executor枚举和Global Plan生成阶段
[3] 归因报告知识边界：OneScience编排体系支持两种规划路径，当路径(1)不可用时应自动降级为路径(2)
