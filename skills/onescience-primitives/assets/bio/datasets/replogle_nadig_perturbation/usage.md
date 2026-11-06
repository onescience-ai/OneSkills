## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/State_dataset/Replogle-Nadig-Preprint`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/State_dataset/Replogle-Nadig-Preprint`。



已绑定的资源入口：

- `State_dataset/Replogle-Nadig-Preprint/GSE264667_hepg2_raw_singlecell_01.h5ad`
- `State_dataset/Replogle-Nadig-Preprint/GSE264667_jurkat_raw_singlecell_01.h5ad`
- `State_dataset/Replogle-Nadig-Preprint/K562_essential_normalized_singlecell_01.h5ad`
- `State_dataset/Replogle-Nadig-Preprint/rpe1_normalized_singlecell_01.h5ad`
- `State_dataset/Replogle-Nadig-Preprint/replogle.h5ad`

## data_schema

X 均为 dense cells × genes。obs 共有 `gene,gene_id,transcript,gene_transcript,sgID_AB,cell_line,gem_group,UMI_count` 等；K562/RPE1 还含 `core_scale_factor,core_adjusted_UMI_count`。四个单细胞系文件 var 含 `gene_name,chr,start,end,class,strand` 等；汇总 replogle.h5ad 的 var 是 HVG 统计列，obsm 有 `X_hvg`。

## task_usage

根据所需细胞系、表达处理视图和泛化目标选择文件；先核查 perturbation/control 和基因 ID，再对接扰动预测模型。

## integration_paths

文件和视图选择 → var 基因轴映射 → 遗传扰动与控制定义 → held-out gene/cell_line 划分 → State/扰动 adapter。

## preparation_requirements

检查 sgID_AB/gene 映射、control 值、cell_line 和基因索引；验证 dense 分块数值、源视图重叠及训练/评测条件互斥。

## consumption_interfaces

基因表达向量、固定基因轴、扰动 gene/sgID、控制状态、细胞系、原始细胞索引和显式 split。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

raw 与 normalized 文件不可在未统一处理口径时直接合并。各文件基因维度不同，汇总文件也不能被当成四个文件的简单拼接。所有尺度拟合和 HVG 选择应明确训练来源。
