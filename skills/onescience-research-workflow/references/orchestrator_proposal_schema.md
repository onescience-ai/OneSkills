# Orchestrator Proposal Schema

本文档定义返回给 `onescience-orchestrator` 的 planner proposal 格式。

## 标准格式

```yaml
planner_proposal:
  planner_skill: onescience-research-workflow
  covered_aspect: <覆盖的意图方面>
  confidence: <high | medium | low>
  
  # 科研目标
  research_goal: <科研目标描述>
  domain_route: <earth | biology | materials | cfd | general-science>
  domain_task_family: <具体任务类型>
  
  # 起始和目标
  starting_artifacts:
    - artifact: <起始产物>
      protocol: <协议/格式>
      status: <provided | inferred | missing>
  
  desired_outputs:
    - output: <期望输出>
      format: <输出格式>
      required: <true | false>
  
  # 计划说明
  why_this_plan:
    - <选择此计划的理由>
  
  # 支持资源
  supported_resources:
    - id: <资源ID>
      type: <data_resource | generator_resource | scoring_resource | validator_resource>
      key_info: <关键信息，1-2句话>
      why_selected: <选择理由>
      limitation: <使用限制>
  
  # 工作流节点
  workflow_nodes:
    - action: <节点要执行的操作，用自然语言描述>
      purpose: <节点目的>
      selected_resource: <选择的资源>
      inputs: <输入列表>
      outputs: <输出列表>
      depends_on: <依赖节点列表>
      checks: <检查项列表>
      preserve_on_failure: <true | false>
  
  # 资源绑定
  resource_bindings:
    models: <模型列表>
    datapipes: <数据管道列表>
    validators: <验证器列表>
  
  # 缺失信息
  missing_inputs:
    - field: <缺失字段>
      why_needed: <为什么需要>
      can_continue_without_it: <true | false>
  
  # 假设和风险
  assumptions:
    - <假设条件>
  
  risks:
    - risk: <风险>
      mitigation: <缓解措施>
  
  # 备选方案
  fallback_options:
    - option: <备选方案>
      when_to_use: <使用条件>
```

## 输出规则

- key_info：控制在 1-2 句话
- why_selected：必须说明选择理由
- missing_inputs：不确定信息写入此处，不要编造
- confidence：根据资源完整性和领域匹配度评估
- action：用自然语言描述节点要执行的操作，不使用固定类型名称
- 保持输出简洁，完整资源内容用于内部规划依据

## 节点字段说明

### action 字段

用自然语言描述节点要执行的操作，例如：
- "预处理 PDB 文件并验证骨架原子完整性"
- "使用 ProteinMPNN 生成候选氨基酸序列"
- "运行模型推理并输出预测结果"
- "对候选序列进行结构验证"
- "汇总评分结果并生成排序表"

**不要使用固定的类型名称**（如 `data.process`、`model.infer` 等），这样可以根据不同领域和任务灵活扩展。

### 依赖关系

- **depends_on**：列出必须先完成的节点 ID
- 独立节点可以并行执行
- 有依赖的节点必须按顺序执行
