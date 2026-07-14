# 阶段 7：结果验证

目标：验证输出存在、结构正确，并在用户请求范围内具备足够的科学合理性。验证标准必须来自 `step_handoff.completion_criteria`、阶段 1 的输出契约、阶段 3 的数据契约和模型官方示例，不把某个领域的指标作为通用默认。

## 输出字段检查

根据阶段 1 的输出契约进行验证：

- 必需文件存在且非空
- 必需字段、变量、坐标、metadata、样本 ID 或结构 ID 存在
- Shape、dimension、dtype、单位、坐标轴、索引和 batch 组织符合预期
- NaN、inf、mask、取值范围、缺失值和异常值行为可接受
- 输出格式符合请求目标或文档化的模型输出

领域附加检查仅在对应任务中启用：

- 气象/地球系统：变量单位、纬度顺序、经度约定、forecast initialization time、lead time、level、网格和投影。
- 生信：参考版本、坐标约定、样本/feature 对齐、ID 映射、批次标签、序列长度或结构字段。
- 材料：结构有效性、元素/组成一致性、晶胞和周期性、能量/力/性质单位、物理约束。
- 流体/CFD：mesh/field 对齐、边界条件、时间步、物理量单位、守恒量或残差检查。
- 通用科研模型：schema、单位、范围、单调性或任务定义中的 domain invariant。

## 可视化

在有用且可行时创建可视化：

- 空间场、结构、mesh 或图数据的可视化
- 时间序列、rollout 或批量指标曲线
- 与 baseline 对比的误差图、差值图或散点图
- 标量或 tensor 输出的直方图、范围摘要或 embedding 摘要

绘图代码应与推理入口分离。将图片保存到 `infer_workdir`，并在 `validation_report.md` 中引用；`validation_report.md` 本身也应保存在 `infer_workdir`，并引用本次验证所依据的知识文件与最终输出路径。 
## Baseline 对比

使用最合适的可用 baseline：

- 官方示例输出、期望 checksum 或文档中的数值范围
- 用户提供的 ground truth 或标注
- 同一工作目录中的历史 run
- 领域合理 baseline，例如气象 persistence/climatology、生信已知注释或公共 benchmark、材料已知性质/DFT 参考、流体解析解/数值基准
- 没有科学 baseline 时，使用 shape-only、schema-only 和 range-only 检查

说明容差和比较方法。不要把 shape-only、schema-only 或 range-only 验证描述成科学正确性验证。

## 验证报告

写入 `validation_report.md`：

- 汇总状态：success、partial、blocked 或 failed
- 输出清单
- Schema、字段和领域附加检查
- 已生成的可视化
- Baseline 对比和指标
- 已知假设和限制
- 推荐下一步

最终 `execution_result.observation` 应包含验证状态和最重要证据，而不只是报告路径。
