# onescience-orchestrator对expert技能的调度规则

## 适用范围

**触发条件**：
- intent_profile识别出材料科学（matchem）领域
- 任务需要专业工作流规划
- 需要领域专家知识支持

**适用场景**：
- 任务编排阶段的技能调度
- 领域识别后的专家技能调用
- planner proposal生成与融合

**不适用场景**：
- 非材料科学领域任务
- 已有明确工作流的任务
- 用户指定直接执行的任务

## 输入

**输入数据格式**：
- Task State：任务状态信息
- intent_profile：用户意图分析结果
- matched_resources：匹配的资源列表

**数据来源**：
- 用户输入的任务描述
- 系统分析的意图结果
- 资源检索的匹配结果

**预处理要求**：
- 意图分析完成
- 领域识别完成
- 资源检索完成

## 输出

**输出产物**：
1. **planner proposal**：专家技能生成的工作流规划
2. **调度记录**：记录expert技能调用过程
3. **融合计划**：多个proposal融合为全局计划

**格式要求**：
- JSON格式的proposal文件
- 文本格式的调度日志
- 结构化的全局计划

**验证标准**：
- proposal包含完整工作流节点
- 调度记录准确无误
- 融合计划逻辑一致

## 流程节点

### Step 1：领域识别
- **操作**：从intent_profile中识别材料科学领域
- **参数**：domain_hints, task_description
- **工具**：领域分类器
- **质量门禁**：领域识别准确

### Step 2：expert技能匹配
- **操作**：根据领域匹配expert技能
- **参数**：domain=matchem, skill_type=expert
- **工具**：技能匹配器
- **质量门禁**：匹配到合适的expert技能

### Step 3：expert技能调用
- **操作**：调用匹配的expert技能
- **参数**：Task State + intent_profile + matched_resources
- **工具**：技能调度器
- **质量门禁**：调用成功返回proposal

### Step 4：proposal融合
- **操作**：将多个proposal融合为全局计划
- **参数**：多个planner proposal
- **工具**：计划融合器
- **质量门禁**：融合计划无冲突

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 领域 | matchem | intent_profile | 材料科学领域 |
| 技能类型 | expert | 规则定义 | 专家规划技能 |
| 融合策略 | 优先级融合 | 框架规则 | 多proposal融合方法 |

## 边界与分流

**异常处理**：
- 领域识别失败：使用通用规划流程
- expert技能不可用：降级为直接步骤规划
- proposal冲突：人工干预或优先级排序

**降级策略**：
- expert技能不可用：使用direct_step规划模式
- 多proposal冲突：选择置信度最高的proposal

**分支条件**：
- 识别到matchem领域：调用onescience-research-workflow
- 未识别到特定领域：使用通用规划流程

## 质量检查

**验证点**：
1. 领域识别准确性
2. expert技能匹配正确性
3. proposal完整性
4. 融合计划一致性

**阈值**：
- 领域识别置信度 > 0.8
- proposal包含所有必要节点

**失败处理**：
- 重试领域识别
- 请求用户指定领域
- 降级为直接步骤规划

## 回退策略

**失败时的替代方案**：
- expert技能不可用：使用direct_step规划模式
- 领域识别失败：使用通用工作流模板
- proposal生成失败：请求用户指导

## 资源召回建议

**何时应召回本卡片**：
- orchestrator需要调度expert技能时
- 任务编排阶段需要专业规划时
- 领域识别后需要专家知识时

**配套资源**：
- matchem-crystal-structure-prediction-workflow：完整工作流
- matchem-blocked-trigger-rules：BLOCKED触发规则
- general-workflow-step-mapping：工作流步骤映射

## 证据来源

本知识卡片基于onescience框架内部规则，无法从公开学术论文中获取。阻塞原因：内部框架知识，需要参考onescience-orchestrator的SKILL.md文档。