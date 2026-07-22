# 阶段 6：结果验证

目标：验证训练脚本、配置、日志、checkpoint 和指标存在、结构正确，并在用户请求范围内具备足够的工程合理性。验证标准必须来自 `step_handoff.completion_criteria`、阶段 1 的训练契约、阶段 2 的数据契约、阶段 3 的训练计划和项目原生示例，不把某个领域的指标作为通用默认。

## 输出字段检查

根据阶段 1 到阶段 5 的输出契约进行验证，并确认 trainer 定义的训练契约与 runtime 返回的真实执行证据一致：

- 必需文件存在且非空
- 必需脚本、配置、checkpoint、日志和 metrics 字段存在，并与 trainer 先前定义的训练入口、评测频率、checkpoint 规则和输出约定一致
- shape、dimension、dtype、单位、坐标轴、索引和 batch 组织符合预期
- NaN、inf、loss 爆炸、异常值和空日志行为可接受
- checkpoint 和 best model 规则符合训练计划
- 输出格式符合请求目标或文档化的训练输出

领域附加检查仅在对应任务中启用：

- 气象/地球系统：变量单位、纬度顺序、经度约定、历史窗口、lead time、level、网格和投影。
- 生信：参考版本、坐标约定、样本/feature 对齐、ID 映射、批次标签、序列长度或结构字段。
- 材料：结构有效性、元素/组成一致性、晶胞和周期性、能量/力/性质单位、物理约束。
- 流体/CFD：mesh/field 对齐、边界条件、时间步、物理量单位、守恒量或残差检查。
- 通用科研模型：schema、单位、范围、单调性或任务定义中的 domain invariant。

## 日志与指标检查

在有用且可行时检查：

- train / val / test 指标曲线或摘要
- checkpoint 保存频率、best checkpoint 选择和恢复点记录
- loss、学习率、梯度或吞吐量日志
- 与 baseline、历史 run 或用户目标的差异

如果只有 shape-only、schema-only 或文件存在性验证，不要把它描述成训练质量验证。

## 验证报告

写入 `validation_report.md`：

- 汇总状态：success、partial、blocked 或 failed
- 代码、配置、日志、checkpoint 和 metrics 清单
- schema、字段和领域附加检查
- 指标、日志或 baseline 对比
- 已知假设和限制
- 推荐下一步

`validation_report.md` 应保存在 `trainer_workdir`，并引用本次验证所依据的知识文件、训练脚本路径、日志路径、checkpoint 路径和结果路径。

最终 `execution_result.observation` 应包含验证状态和最重要证据，而不只是报告路径。
