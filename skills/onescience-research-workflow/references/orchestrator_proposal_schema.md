# Orchestrator Proposal Schema

本文档定义返回给 `onescience-orchestrator` 的 `planner_proposal` 格式。规划输出必须能被 orchestrator 融合为 executor handoff，不能只停留在“使用哪个技能/资源”的表层说明。

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
    - action: <节点要执行的操作，用自然语言描述；必须写清具体执行步骤、入口/脚本/配置/参数要求>
      purpose: <节点目的>
      selected_resource: <选择的资源>
      inputs: <输入列表；包含格式、shape、单位、路径或 artifact 约束>
      outputs: <输出列表；包含格式、schema、保存要求>
      depends_on: <依赖节点列表>
      checks: <检查项列表；包含运行、静态、格式、数值、日志或产物证据>
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
- 不得只写“使用 XX 应用/模型/技能/方法”；必须在 `workflow_nodes[].action`、`inputs`、`outputs`、`checks`、`risks` 和 `fallback_options` 中写清输入、输出、参数、环境、实现或运行要求、验证证据和 fallback
- 如果资源只是“匹配”但缺少具体使用或决策知识，必须先补充资源召回；仍缺时写入 `missing_inputs`

## 节点字段说明

### action 字段

用自然语言描述节点要执行的操作，例如：
- "校验输入数据的字段、单位、坐标系和缺失值，并生成质量控制报告"
- "根据领域约束完成格式转换和参数配置，输出可供后续计算使用的标准化数据"
- "准备模拟或计算任务的初始条件、边界条件、网格/结构文件和运行配置"
- "运行分析、模拟、建模或数据处理入口，并保存日志、主要产物和失败证据"
- "按指定指标汇总结果，生成表格、图件或报告，并标记异常样本"

**不要使用固定的类型名称**（如 `data.process`、`model.infer` 等），这样可以根据不同领域和任务灵活扩展。

### 依赖关系

- **depends_on**：列出必须先完成的节点 ID
- 独立节点可以并行执行
- 有依赖的节点必须按顺序执行

## 节点执行细节要求

### 代码实现节点

当节点需要生成或修改代码时，`action`、`inputs`、`outputs`、`checks` 至少包含：

- 目标文件/目录、模块边界、函数或 CLI 名称
- 输入输出 schema、数据格式、shape、单位、异常处理
- 需要实现的数据转换、算法/模型接口、模拟适配、分析逻辑、配置读取和日志行为
- 最小静态检查或 smoke test 要求
- 不允许 executor 自行猜测的缺失契约

### 安装准备节点

当节点需要安装应用、库、运行时或外部工具时，`action`、`inputs`、`outputs`、`checks` 至少包含：

- 应用/库名称、版本/后端约束、安装来源或资源中的使用说明依据
- 依赖和硬件/系统前置条件
- 安装后验证命令或可执行入口检查
- 安装失败时的 fallback，例如改为生成等价脚本、使用替代库或标记 blocked

### 运行计算节点

当节点需要运行应用、脚本、数据管道、模拟器、分析程序、模型相关入口或 pipeline 时，`action`、`inputs`、`outputs`、`checks` 至少包含：

- 入口命令或函数、参数、配置文件、工作目录和输出目录
- 输入 artifact 绑定、配置/参数文件绑定、batch/shape/单位要求；如涉及模型，再说明模型资产/权重绑定
- 预处理、后处理、日志、错误处理和可重跑要求
- 完成后必须收集的运行证据

### 建模或参数化节点

当节点需要训练/微调模型、拟合统计模型、估计参数、标定模拟器或构建 surrogate 时，`action`、`inputs`、`outputs`、`checks` 至少包含：

- 数据切分、目标变量/状态变量、损失/指标/目标函数、训练或标定配置、参数/模型产物保存语义
- 模型/方法实现或导入方式、初始化/预训练/先验参数要求
- 最小训练可行性检查和失败回退
- 产物如何交给后续预测、模拟、分析或评估节点

### 验证评估节点

当节点需要验证、评估或汇总结果时，`action`、`inputs`、`outputs`、`checks` 至少包含：

- 评价指标、阈值、统计口径、报告格式
- 输入结果的 schema 和完整性检查
- 可接受失败范围、人工复核点和 fallback 条件

## 通用规划约束

- **环境缺入口**：如果环境没有目标应用、脚本、库、模拟器、数据管道、分析程序或模型入口，计划必须先增加安装、准备、适配或实现节点，不能直接写“使用该应用/方法”。
- **缺数据契约**：如果后续节点依赖数据格式、字段、单位、坐标、shape、采样频率或质量规则，必须先规划数据检查/转换节点；缺失且无法推断时写入 `missing_inputs`。
- **缺配置或参数**：如果计算、模拟、训练、分析或评估依赖配置文件、边界条件、势函数、阈值、统计口径或运行参数，必须在对应节点写清来源、默认策略和验证方式；缺失时写入 `missing_inputs`。
- **缺实现资产**：如果任务需要代码、脚本、CLI、notebook、模板、模型实现或模拟适配器而当前没有，计划必须增加实现/适配节点，并说明接口、输入输出、日志和最小验证。
- **模型相关缺口**：只有当任务确实包含训练、推理、预测、评分或模型评估时，才要求规划模型代码、模型资产、运行脚本、预处理、后处理和输出 schema；缺失时写入 `missing_inputs` 或规划实现/训练/替代 baseline。
- **多阶段依赖**：数据准备、资源准备、实现/适配、运行/计算、验证/评估、汇总/报告等动作如前置条件或产物不同，必须拆成独立节点并用 artifact 依赖串接。
