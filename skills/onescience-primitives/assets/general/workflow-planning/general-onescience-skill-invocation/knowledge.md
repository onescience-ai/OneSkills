# OneScience技能调用规范

## 适用范围
本卡片规范OneScience技能体系中executor技能的调用方式，适用于任何领域任务（材料科学、生物信息、气候、CFD等）的技能调度。当orchestrator识别出任务需要调用具体执行技能时，必须按本规范执行。

## 输入
- step_handoff：orchestrator传递的步骤交接信息
- task_context：任务上下文（用户目标、约束、相关产物）
- inputs：技能所需的具体输入参数
- expected_outputs：期望的输出产物

## 输出
- execution_result：技能执行结果，包含状态、产物、观察和建议
- artifacts：生成的文件、报告、模型等
- observation：执行观察、质量说明、后续建议

## 流程节点

### 1. 技能选择
- **操作**：根据任务需求和技能描述选择合适的executor技能
- **参数**：任务类型、领域、所需能力
- **工具**：orchestrator的技能注册表
- **质量门禁**：确认技能与任务匹配

### 2. 输入准备
- **操作**：按技能SKILL.md定义的输入契约准备数据
- **参数**：step_handoff格式、必要字段
- **工具**：orchestrator的输入验证逻辑
- **质量门禁**：输入格式正确性检查

### 3. 技能调用
- **操作**：调用目标技能并等待执行完成
- **参数**：超时设置、重试策略
- **工具**：onescience技能调用接口
- **质量门禁**：执行状态监控

### 4. 结果验证
- **操作**：检查技能输出是否符合契约
- **参数**：输出格式、产物完整性
- **工具**：orchestrator的输出验证逻辑
- **质量门禁**：产物存在性和格式检查

## 关键参数

### 通用判据（方法层）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 调用格式 | step_handoff YAML | [1] | 标准化的输入格式 |
| 输出格式 | execution_result YAML | [1] | 标准化的输出格式 |
| 超时时间 | 300-3600秒 | [1] | 根据任务复杂度设置 |
| 重试次数 | 0-3次 | [1] | 根据失败类型决定 |

### 校准数值（多孔材料体系）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据标准化技能 | onescience-data-standardizer | [1] | 将原始数据转为AI-Ready格式 |
| 模型训练技能 | onescience-trainer | [1] | 训练基础模型 |
| 代码生成技能 | onescience-coder | [1] | 生成执行代码 |
| 数据分析技能 | onescience-data-analyzer | [1] | 执行统计分析和可视化 |

## 边界与分流
- **技能不存在**：记录缺失原因，回退到手动实现或报告任务无法完成
- **技能执行失败**：根据失败类型决定重试、降级或终止
- **输入不匹配**：调整输入格式或联系orchestrator重新规划

## 质量检查
- **契约一致性**：输出必须符合SKILL.md定义的输出契约
- **产物完整性**：所有必需文件必须存在且非空
- **可追溯性**：记录每次调用的输入、输出、状态和耗时

## 回退策略
- 若技能调用失败，可尝试：(1) 检查输入格式；(2) 降低任务复杂度；(3) 使用替代技能或手动实现

## 资源召回建议
- 当orchestrator需要调用executor技能时召回本卡片
- 配套资源：具体领域技能（如onescience-trainer、onescience-data-standardizer）

## 证据来源
[1] Scalable Infrastructure Supporting Reproducible Nationwide Healthcare Data Analysis toward FAIR Stewardship, Scientific Data, 2023, DOI: 10.1038/s41597-023-02580-7