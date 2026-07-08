# architecture_overview

该应用卡覆盖细胞层面的图像、流式和空间表型数据交接。任务必须明确图像类型、通道/marker panel、preprocessing、segmentation 或 gating 策略、QC checkpoint 和定量输出；不得把图像文件当普通矩阵处理。

# parameter_scale

非固定模型规模。数据规模由图像像素、tile 数、channel 数、mask label 数、FCS 事件数和 marker 数决定。

# architecture_structure

- `segmentation_plan.yaml`：记录图像、通道、分割策略、mask QC 和输出。
- `wsi_tile_plan.yaml`：记录 WSI tile 尺寸、倍率、重叠、染色标准化和 QC。
- `imc_analysis_plan.yaml`：记录 IMC/MIBI marker、分割、phenotyping 和 spatial neighborhood。
- `flow_panel_metadata.csv`：记录流式 marker、通道、补偿和门控信息。
- `image_dataset_manifest.csv`：记录图像路径、通道、像素大小、ROI 和批次。
- `label_mask_measurements.py`：从 label mask 计算面积、质心等 region measurements。
- `cytometry_table_qc.py`：检查 cytometry marker 表结构和基础摘要。

# input_schema

输入包括 TIFF/OME-TIFF/WSI/FCS 派生表、mask、marker panel、channel metadata、pixel size、tile 设置、gating 或 segmentation strategy、QC 图和输出目录。

# output_schema

输出包括图像 manifest、分割计划、tile 计划、IMC 分析计划、mask measurement 表、cytometry QC 摘要和人工审核清单。

# shape_transformations

image: channels x height x width 或 z/time x channels x height x width
  -> preprocessing/tile
  -> segmentation mask: height x width label map
  -> region measurements: labels x features

cytometry table: events x markers
  -> marker QC summary
  -> gating/phenotype handoff

# key_dependencies

- 图像通道和像素尺度元数据。
- mask label 与原始图像的配准关系。
- cytometry marker panel 和补偿/转换说明。
- pandas/scikit-image 风格表格和区域测量约定。

# common_modification_points

- WSI tile 尺寸、倍率、重叠和 stain normalization。
- 分割模型或算法从模板计划升级到 Cellpose/scikit-image/OpenCV。
- marker panel 字段、补偿矩阵和 transformation。
- mask QC 指标和人工审核图。

# implementation_risks

- 不可跳过 compensation、transformation、stain normalization、mask QC。
- 不可在没有人工审核或 QC 图时把自动门控/自动分割当最终生物学结论。
- mask 与图像尺寸、通道和像素尺度不一致会导致定量错误。

# code_references

- primitive 脚本目录：`assets/bio_cell_imaging_cytometry_app/script/`
- 模板资源目录：`assets/bio_cell_imaging_cytometry_app/script/bio_cell_imaging_templates/`
- 脚本资源目录：`assets/bio_cell_imaging_cytometry_app/script/bio_cell_imaging_tools/`
- 语义来源标签：`cell-imaging-cytometry`
