# launch

label mask 测量示例：

```sh
python script/bio_cell_imaging_tools/label_mask_measurements.py --mask labels.tif --output measurements.csv
```

cytometry 表 QC 示例：

```sh
python script/bio_cell_imaging_tools/cytometry_table_qc.py --input cytometry.csv --output qc.json
```

# input_schema

图像任务需要图像路径、通道、像素大小、ROI、mask 或分割计划。流式任务需要 marker panel、event table、补偿/转换说明和 gating 策略。所有路径通过 CLI 或模板字段提供。

# runtime_interfaces

- CLI 工具：`label_mask_measurements.py`、`cytometry_table_qc.py`
- 模板入口：`flow_panel_metadata.csv`、`image_dataset_manifest.csv`、`imc_analysis_plan.yaml`、`segmentation_plan.yaml`、`wsi_tile_plan.yaml`
- 适用任务标签：`flow-cytometry-analysis`、`imaging-mass-cytometry`、`bioimage-segmentation`、`digital-pathology-wsi`、`microscopy-image-management`

# main_functions

- measure label masks
- summarize cytometry table
- emit segmentation plan
- emit WSI tile plan
- emit IMC and image manifest

# execution_resources

表格 QC 为 CPU 任务。大图、WSI tile、IMC 或深度学习分割需要额外内存/GPU 评估。

# operation_limits

该卡不直接执行复杂图像分割模型训练，不替代人工审核，不保证 FCS 原始文件解析；需要 FCS 专用读取时应扩展执行脚本。
