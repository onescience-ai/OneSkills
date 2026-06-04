---
name: bio-assay-image-quantification
description: 实验图像定量 skill。用于 Western blot、gel electrophoresis、dot blot、plate image 等 band/lane/spot 定量、背景扣除、housekeeping/loading control 归一化、重复聚合和图表交接。
---

# 实验图像定量

## 使用边界

用于 Western blot、凝胶、斑点杂交或板式图像中的条带/点位定量。若图像是细胞/组织显微图像，读取 `../../cell-imaging-cytometry/bioimage-segmentation/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_protocol_templates/blot_quantification_layout.csv`：lane、band、target、loading control、condition 和 replicate 模板。
- `references/assay_quantification_rules.md`：背景扣除、归一化、饱和、重复和报告规则。

## 推荐流程

1. 明确图像和实验：Western blot、gel、dot blot、plate image；记录 exposure 和 replicate。
2. 定义 ROI：lane/band/spot、background region、target 和 loading control。
3. 定量：integrated density、local background subtraction、saturation flag。
4. 归一化：target/loading control，再相对 control condition 计算 fold change。
5. 统计：按 biological replicate 聚合，技术重复先汇总。
6. 输出：raw intensity、normalized value、QC flag、plot 和方法说明。

## 交接物

```yaml
bio_task_family: experimental-protocol-automation
experiment_task: assay-image-quantification
image_inputs:
layout_table:
roi_strategy:
background_subtraction:
normalization:
replicate_structure:
qc_flags:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要定量饱和条带并作为可靠线性信号。
- 不要把技术重复当作生物重复。
- 不要只给 fold change 而不给原始强度和归一化步骤。
