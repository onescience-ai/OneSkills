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

### 生信结构输出

当推理产物包含 `.pdb`、`.cif` 或 `.mmcif`，且用户请求结构可视化或该可视化对验证有用时：

1. 向 `onescience-primitives` 发出 `resource_retrieval_request`，使用 `filters.domain: bio`、`filters.keyword: complex structure visualization`、`content_request: 完整内容`；需要 bundled renderer 时设置 `include_execution_assets: true`。
2. 只消费 resource 返回的 `content` 与已校验的 `content.execution_assets`，不得沿 `matched_resources[].path` 直接读取 primitive 资产。
3. 将结构路径、结构来源、链/实体信息、pLDDT/PAE 来源、请求视图和输出格式交给 `onescience-data-analyzer`。
4. AF3 多样本通过 `samples_manifest_path` 交接；每个样本必须把同一 seed/sample 的 CIF、`confidences.json` 与 `summary_confidences.json` 原子配对，并记录三个文件的路径和 SHA-256。
5. 完整 PAE 只能来自 `confidences.json.pae`；summary 中的 `chain_pair_pae_min` 不能被扩展、插值或复制为 PAE matrix。数据缺失时必须标记 unavailable。
6. `single_file_compatibility: true` 保留旧结构路径调用；没有完整 confidence JSON 时只允许结构视图，PAE 验证不得伪成功。
7. 蛋白质单体和复合物都绑定 `complex_structure_visualization`；由 primitive 的 scene mode 决策区分。
8. 只有上游模型或文件契约明确说明 B-factor 承载 pLDDT 时，才把它标记为 pLDDT。
9. 在 `validation_report.md` 中记录 renderer、scene mode、sample count、provenance、PAE 状态、validation flags、输出文件、warnings 和质量检查。

建议 handoff 的必要字段：

```yaml
samples_manifest_path: <AF3 samples manifest；多样本首选>
single_file_compatibility: <true | false>
structure_path: <PDB/mmCIF/CIF>
confidence_path: <同一样本 *_confidences.json>
summary_confidences_path: <同一样本 *_summary_confidences.json>
structure_source: <model or experiment>
confidence_semantic: <plddt | b_factor | external | none>
confidence_source: <field or external file>
pae_source: <af3_confidences_json | none>
expected_sample_count: <integer>
validation_flags:
  - "--expect-samples <N>"
  - "--require-pae"
  - "--require-plddt-provenance"
requested_outputs: <html/png/pml/pse>
```

绘图代码应与推理入口分离。仅用于内部验证的图片保存到 `infer_workdir`；用户明确要求交付的可视化保存到 `code_save_dir` 或上游指定的结果目录，并在 `validation_report.md` 中引用。`validation_report.md` 本身保存在 `infer_workdir`，并引用本次验证所依据的知识文件与最终输出路径。

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

如果仍有未执行的候选、未落盘的输出或未完成的批量结果，“推荐下一步”只表示后续路由，不代表当前步骤结束；应先补齐剩余项或将状态标记为 `partial` / `blocked`。

最终 `execution_result.observation` 应包含验证状态和最重要证据，而不只是报告路径。
