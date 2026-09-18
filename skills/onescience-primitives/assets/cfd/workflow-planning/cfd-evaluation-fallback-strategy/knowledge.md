# 湍流生成模型评估失败降级策略

## 适用范围
本规范适用于湍流生成模型评估过程中出现的失败情况，定义降级策略，包括部分评估、错误报告和恢复机制，确保评估任务可追溯且不因局部失败而完全中断。适用于需要生成 `evaluation.json`、`worst_cases.csv`、`applicability_report.md` 和 `PASS_REJECT_BLOCKED.txt` 等评估文件的场景。不适用于非生成模型评估。

## 输入
- 生成的湍流场样本（可能为空或部分无效）
- 评估指标定义（如统计误差、物理约束满足度）
- 错误处理配置（如异常捕获、日志记录）

## 输出
- `evaluation.json`：评估结果（可能部分指标缺失）
- `worst_cases.csv`：最差样本列表（可能为空）
- `applicability_report.md`：适用性报告（包含错误说明）
- `PASS_REJECT_BLOCKED.txt`：状态标记文件（根据评估结果）

## 流程节点
1. **异常捕获** → 使用 try-except 捕获评估过程中的异常
2. **部分评估** → 若部分指标计算失败，跳过失败指标，计算可用指标
3. **错误记录** → 记录异常类型、错误信息、失败步骤
4. **状态标记** → 根据评估结果生成状态标记文件（PASS/REJECT/BLOCKED）
5. **报告生成** → 生成评估报告，包含成功和失败指标的说明
6. **恢复尝试** → 若可能，尝试使用降级评估方法（如简化指标）

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 异常捕获范围 | Exception（Python 基类） | [D1] | 捕获所有非系统退出异常 |
| 部分评估阈值 | 至少 50% 指标成功 | 领域知识 | 避免完全失败 |
| 错误日志格式 | JSON 结构化日志 | 领域知识 | 便于解析 |
| 状态标记规则 | 无失败=PASS，部分失败=REJECT，完全失败=BLOCKED | 领域知识 | 明确状态 |

## 边界与分流
- **生成数据为空**：直接标记为 BLOCKED，生成错误报告
- **评估指标计算异常**：跳过该指标，在报告中注明
- **资源不足**：使用简化评估方法，减少计算量
- **依赖缺失**：使用替代库或降级方法

## 质量检查
- 验证评估文件已生成（即使部分指标缺失）
- 检查错误日志包含足够信息用于调试
- 确保状态标记文件正确反映评估结果
- 验证报告包含失败原因和恢复建议

## 回退策略
- 若评估完全失败，使用默认值或空值填充评估文件
- 若部分指标无法计算，使用可用指标的平均值作为近似
- 若资源不足，减少评估样本数量或使用简化模型

## 资源召回建议
当任务涉及湍流生成模型评估、错误处理、鲁棒性测试时，应召回本卡片。配套资源：`cfd-turbulence-physical-constraint-threshold`（物理约束筛选）、`cfd-turbulence-data-contract-specification`（数据契约生成）。

## 补充证据（开源文档/用户自有，可选）
[D1] Python Errors and Exceptions documentation, Python Software Foundation, version 3.14.7, URL: https://docs.python.org/3/tutorial/errors.html（accessed_at: 2026-09-17，权威文档）

## 证据来源
[1] Python Errors and Exceptions documentation, Python Software Foundation, 2026