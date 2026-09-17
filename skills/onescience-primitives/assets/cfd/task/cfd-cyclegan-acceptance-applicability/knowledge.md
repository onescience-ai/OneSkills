# CycleGAN无配对超分辨率重建任务验收与适用域判定

## 适用范围

**触发条件**：
- 已完成CycleGAN超分辨率重构并获得重构流场
- 需要评估统计误差、物理约束、泛化能力和计算收益
- 需要给出PASS/REJECT/BLOCKED工程可用性判定

**适用场景**：
- 湍流超分辨率重建的最终验收评估
- 统计误差与物理一致性联合评估
- 域外工况泛化测试与适用域判定
- 最差样本追溯与推理成本分析

**不适用场景**：
- 训练或推理过程中的中间评估
- 无需工程可用性判定的研究性探索

## 输入

- 验收指标（{METRICS}）：统计和物理指标列表
- 相对误差门限（{MAX_RELATIVE_L2}）：测试集放行阈值
- 外推测试开关（{RUN_OOD_TEST}）：是否测试域外工况
- s04产出的重构流场与误差场

## 输出

- evaluation.json：逐变量误差与综合评估
- worst_cases.csv：最差样本列表与可追溯信息
- applicability_report.md：适用域报告（含限制与复核建议）
- PASS_REJECT_BLOCKED.txt：最终判定结论

## 流程节点

### Step 1：统计误差评估
- **操作**：计算逐变量相对L2误差、均方误差等统计指标
- **参数**：{METRICS}中的relative_L2
- **质量门禁**：统计指标完整报告

### Step 2：物理约束评估
- **操作**：评估频谱误差、梯度误差、守恒误差等物理约束
- **参数**：{METRICS}中的spectrum_error, gradient_error, conservation_error
- **质量门禁**：物理指标同时报告

### Step 3：最差样本追溯
- **操作**：识别并记录最差样本，分析失败原因
- **参数**：evaluation结果
- **质量门禁**：最差样本可追溯

### Step 4：外推测试与适用域判定
- **操作**：若{RUN_OOD_TEST}为true，执行几何或工况外推测试
- **参数**：{RUN_OOD_TEST}、{MAX_RELATIVE_L2}
- **质量门禁**：结论含适用域限制与复核建议

### Step 5：综合判定
- **操作**：基于{MAX_RELATIVE_L2}及任务物理门限给出PASS、REJECT或BLOCKED
- **参数**：{MAX_RELATIVE_L2}（默认0.1）
- **质量门禁**：不得仅凭平均误差宣称工程可用

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 验收指标 | relative_L2, spectrum_error, gradient_error, conservation_error | 场景需求书 s05 | 统计与物理联合验收 |
| 相对L2门限 | 0.1 | 场景需求书 s05 | 放行阈值 |
| 外推测试 | 默认true | 场景需求书 s05 | 适用域判定必要条件 |

## 边界与分流

- 仅凭平均误差宣称工程可用：禁止，需同时报告最差样本与物理约束
- 域外工况未测试：不宣称工程可用，需补充外推评估
- 物理约束违反：即使统计误差合格也不通过

## 质量检查

- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

## 回退策略

- 验收REJECT：不输出工程可用结论，需调整模型或扩大训练数据
- 外推测试不通过：明确适用域边界，域外工况需CFD复核

## 资源召回建议

- 何时召回本卡片：CycleGAN超分辨率验收阶段、适用域判定、工程可用性评估
- 配套资源：cfd-cyclegan-super-resolution-reconstruction（流场重构）、cfd-cyclegan-les-to-dns-super-resolution-scenario（场景总卡）

## 证据来源

[1] "Unsupervised deep learning for super-resolution reconstruction of turbulence", arXiv:2007.15324, 2020
场景需求书 CFD_S099 workflow step s05 定义。
