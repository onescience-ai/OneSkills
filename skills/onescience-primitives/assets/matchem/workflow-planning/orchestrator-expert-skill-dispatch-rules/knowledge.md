# orchestrator对expert技能的调度规则

## 适用范围
本工作流规划卡适用于所有涉及领域识别和专业规划的科研计算任务。当orchestrator识别出用户意图属于特定领域（如材料科学、生物信息学、气候科学等）时，必须按照本规则调用相应的expert技能进行专业规划。适用于所有需要领域专业知识支撑的任务规划场景。

## 触发条件

### 领域识别
根据intent_profile中的domain_hints判断领域：

| 领域关键词 | 目标领域 | 对应expert技能 |
|------------|----------|----------------|
| 材料/晶体/催化/电池/MXene/material | matchem | onescience-research-workflow |
| 基因/蛋白/生物/序列/细胞/组学 | bio | onescience-data-profile |
| 气象/气候/天气/降水/温度 | climate | onescience-research-workflow |
| 流体/流场/空气动力/涡/网格/CFD | cfd | onescience-research-workflow |

### 调度时机
1. **intent_profile生成后**：立即检查domain_hints
2. **资源检索完成后**：根据matched_resources判断是否需要expert
3. **直接规划前**：在planning_mode=direct_step前强制检查

## expert技能输入格式

### 标准输入
```yaml
step_handoff:
  step_id: planning
  execution_skill: onescience-research-workflow
  step_goal: 为指定领域任务生成专业工作流规划
  task_context:
    user_goal: <用户最终目标>
    constraints: <约束列表>
    relevant_artifacts: <相关产物路径>
  inputs:
    intent_profile:
      domain_hints: [<领域关键词>]
      task_type: <任务类型>
      complexity: <复杂度>
    matched_resources:
      - <资源列表>
  expected_outputs:
    required_files: [planner_proposal]
    cards_required: true
```

### 输出格式
```yaml
planner_proposal:
  workflow_nodes:
    - step_id: <步骤ID>
      step_name: <步骤名称>
      dependencies: [<依赖步骤>]
      resources: [<绑定资源>]
      quality_gates: [<质量门禁>]
  dependencies:
    - from: <步骤A>
      to: <步骤B>
      type: <依赖类型>
  resource_bindings:
    - step_id: <步骤ID>
      resource_type: <资源类型>
      resource_name: <资源名称>
  execution_suggestions:
    - <建议1>
    - <建议2>
```

## proposal融合流程

### 步骤1：收集所有proposal
```json
{
  "planner_proposals": [
    {"source": "onescience-research-workflow", "proposal": "<proposal内容>"},
    {"source": "onescience-data-profile", "proposal": "<proposal内容>"}
  ]
}
```

### 步骤2：冲突检测与解决
1. **步骤冲突**：两个proposal包含相同步骤但定义不同
   - 解决：选择更详细的定义，合并参数
2. **资源冲突**：同一资源被绑定到不同步骤
   - 解决：根据优先级选择，或标记为用户确认
3. **依赖冲突**：依赖关系形成环或矛盾
   - 解决：重新排序或标记为BLOCKED

### 步骤3：生成Global Plan
```yaml
global_plan:
  workflow_nodes: <合并后的步骤列表>
  dependencies: <合并后的依赖关系>
  resource_bindings: <合并后的资源绑定>
  conflicts_resolved: <已解决的冲突列表>
  pending_confirmations: <待用户确认项>
```

## 跳过专家规划的风险

### 风险类型
1. **方向错误**：如将晶体结构预测误解为模型训练
2. **步骤缺失**：遗漏关键步骤（如s01-s04）
3. **资源误用**：选择不合适的模型或工具
4. **质量门禁缺失**：未设置必要的验证点

### 处置规则
- **强制调用**：当domain_hints匹配到特定领域时，必须调用expert技能
- **用户确认**：如用户明确要求跳过expert，需记录确认信息
- **事后补救**：如已跳过expert，在后续步骤中增加领域专家审查

## 质量检查
- **proposal完整性**：是否包含所有必要字段
- **冲突检测**：是否识别并解决所有冲突
- **领域匹配**：expert技能是否与领域匹配
- **用户确认**：关键选择是否获得用户确认

## 资源召回建议
- **召回时机**：当orchestrator需要调用expert技能时
- **配套资源**：
  - 技能卡：onescience-research-workflow、onescience-data-profile
  - 场景卡：所有需要专业规划的场景卡
  - 工作流卡：所有包含expert调度的工作流卡

## 证据来源
（本卡基于orchestrator编排规则和expert技能调度逻辑生成，无直接论文证据）
