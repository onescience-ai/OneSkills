# CFD验收评估鲁棒性设计与失败恢复

## 适用范围

面向CFD数据驱动模型的验收评估任务，定义评估脚本对上游产物的鲁棒性处理规范。适用于所有需要从上游JSON产物加载数据、执行统计评估并生成验收结论的CFD工作流。核心要求：评估脚本必须对上游JSON做schema校验和完整性检查，任何评估失败都必须产出PASS_REJECT_BLOCKED.txt，不得抛出未捕获异常导致整个评估阶段崩溃。

## 输入

- 任务目标：加载上游评估产物，执行验收评估，生成结论
- 数据需求：上游JSON产物（apriori_evaluation.json等）、模型预测结果、基准数据
- 格式要求：JSON格式，需通过schema校验

## 输出

- evaluation.json：完整评估结果
- worst_cases.csv：最差样本列表
- applicability_report.md：适用域报告
- PASS_REJECT_BLOCKED.txt：验收结论（任何情况下必须产出）

## 流程节点

1. **产物完整性校验** → 2. **JSON Schema验证** → 3. **类型安全加载** → 4. **评估执行** → 5. **结论生成**

### 步骤1：产物完整性校验
- 操作：检查上游产物文件是否存在、非空、可读
- 参数：文件路径、最小文件大小、文件格式
- 工具：文件系统检查
- 质量门禁：文件存在且非空

### 步骤2：JSON Schema验证
- 操作：验证JSON产物符合预定义schema
- 参数：schema定义、必填字段列表、字段类型约束
- 工具：jsonschema库或手动校验
- 质量门禁：schema验证通过

### 步骤3：类型安全加载
- 操作：使用try-except捕获所有解析异常，对numpy类型做显式转换
- 参数：JSON加载配置、类型转换规则
- 工具：json.load + 自定义类型转换
- 质量门禁：成功加载所有必要字段

### 步骤4：评估执行
- 操作：基于加载的数据执行统计评估
- 参数：评估指标、阈值、基准值
- 工具：评估脚本
- 质量门禁：评估完成，指标计算正确

### 步骤5：结论生成
- 操作：生成PASS/REJECT/BLOCKED结论
- 参数：评估指标、通过条件、阻塞原因
- 工具：结论生成器
- 质量门禁：结论文件存在且内容完整

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| manifest必填字段 | task_id, global_plan, step状态, 产物清单 | [1] | execution-manifest.json内容契约 |
| manifest生成时机 | 规划阶段完成后、执行步骤开始前 | [1] | 由orchestrator生成 |
| JSON schema校验 | 必填字段+类型约束 | [D1] | 所有JSON产物必须通过 |
| 异常捕获策略 | try-except包裹所有json.load | [用户案例] | 防止JSONDecodeError导致崩溃 |
| BLOCKED产出契约 | 任何评估失败必须产出PASS_REJECT_BLOCKED.txt | [标准规范] | 不得抛出未捕获异常 |
| numpy类型转换 | np.bool_->bool, np.float_->float | [标准规范] | JSON序列化前必须转换 |

### 校准数值（体系专属值）

以下数值来自典型CFD评估任务，供量级校准；其他体系需以自身证据重新锚定：

| 参数 | 典型值 | 来源 | 说明 |
|------|--------|------|------|
| manifest检查超时 | 30秒 | [典型值] | manifest生成超时阈值 |
| JSON产物最小大小 | >100字节 | [典型值] | 空文件或截断文件判定 |
| 评估脚本最大重试 | 3次 | [典型值] | 上游不稳定时的重试策略 |
| BLOCKED判定条件 | 上游缺失/类型错误/schema不符 | [用户案例] | 触发BLOCKED的条件列表 |

## 边界与分流

### 前提1：上游JSON产物存在且完整
- **不成立时转向**：生成BLOCKED结论，记录缺失产物清单，在PASS_REJECT_BLOCKED.txt中明确标注阻塞原因

### 前提2：JSON产物可通过schema校验
- **不成立时转向**：记录schema校验错误详情，生成BLOCKED结论，不继续执行后续评估

### 前提3：numpy类型已正确转换
- **不成立时转向**：在json.dump前增加类型转换层，对所有numpy标量调用bool()/float()/int()

### 前提4：评估指标可计算
- **不成立时转向**：记录不可计算的指标，使用默认值或N/A标记，生成部分评估结论

## 质量检查

1. **manifest完整性**：execution-manifest.json存在且包含所有必填字段
2. **JSON可解析性**：所有JSON产物可被json.load成功解析
3. **类型安全性**：无numpy类型导致的序列化异常
4. **结论文件存在性**：PASS_REJECT_BLOCKED.txt在任何情况下都存在
5. **异常捕获覆盖**：所有json.load调用都有try-except包裹

## 回退策略

1. **manifest缺失**：在planning阶段结束时校验manifest生成，缺失则阻断执行
2. **JSON截断**：检测文件大小与预期不符，生成BLOCKED结论
3. **类型序列化失败**：增加numpy类型转换层，使用自定义JSONEncoder
4. **评估脚本异常**：捕获所有异常，记录错误信息，生成BLOCKED结论

## 资源召回建议

- **何时召回本卡片**：当CFD任务需要执行验收评估或评估脚本需要处理上游JSON产物时
- **配套资源**：
  - cfd-model-validation-metrics：模型验收指标体系
  - general-cfd-task-artifacts：CFD任务产物清单
  - general-json-schema-report-delivery-contract：JSON Schema交付契约
  - general-numpy-json-serialization-rules：numpy类型序列化规则

## 证据来源

[1] report.json中CFD_S080任务归因：execution-manifest.json完全不存在，task_state.json显示status=planning但无global_plan，manifest应在规划阶段完成后由orchestrator生成。
[2] report.json中CFD_S080任务归因：apriori_evaluation.json在第32行截断，np.bool_类型未转换导致json.dump失败。
[3] report.json中CFD_S080任务归因：evaluation.py第56-66行直接json.load()未捕获JSONDecodeError，s04截断JSON导致整个s05崩溃。
[4] Abadía-Heredia R, et al. "An Adaptive Framework for Autoregressive Forecasting in CFD", arXiv:2505.01531, 2025. — 自回归预测框架中的交替预测-重训练策略，30-95%计算成本降低。
[5] Xu Z, Wang L, et al. "CFDagent: A Language-Guided, Zero-Shot Multi-Agent System", arXiv:2507.23693, 2025. — 多智能体CFD系统，88.2%成功率，鲁棒验证框架。
[D1] JSON Schema官方文档, https://json-schema.org/, 2020-12版本。
