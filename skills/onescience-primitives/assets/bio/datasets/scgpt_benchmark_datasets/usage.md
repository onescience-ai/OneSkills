## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/scGPT`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/scGPT`。



已绑定的资源入口：

- `scGPT/BMMC_processed.h5ad`
- `scGPT/Kim2020_Lung.h5ad`
- `scGPT/covid_subsampled.h5ad`
- `scGPT/annotation_pancreas`
- `scGPT/myeloid`
- `scGPT/ms`
- `scGPT/pbmc10k`
- `scGPT/perturbation`

## data_schema

样本单位为细胞，`X` 为 cells × genes；不能仅凭 H5AD 判定 X 为原始计数。

| 子集 | 关键 obs/var 与层 |
| --- | --- |
| BMMC | obs `cell_type,batch,is_train`；var `gene_id`；layers `counts` |
| Kim2020_Lung | obs `cell_type`；var `gene_name` |
| covid | obs `celltype,condition,batch,donor,batch_id`；var 含 `gene_name` |
| pancreas | obs **`Celltype`**；var **`Gene Symbol`** |
| myeloid | obs `cell_type,batch`；基因身份主要从 var 索引确认 |
| ms | obs `celltype,str_batch`；var `gene_name` |
| Adamson/Norman | obs `condition,condition_name,control,cell_type`；var `gene_name`；Norman 另有 `counts` |
| perturbation/Immune_ALL_human | obs `batch,final_annotation`；layers `counts` |

PBMC 为 10x Matrix Market、barcodes/genes 及配套 CSV/pickle，需先转为同一基因坐标体系。

## task_usage

按注释、整合或扰动预测选择子集和标签；先固定表达来源（X 或 counts），再决定模型所需归一化、HVG、分箱或基因 tokenization。

## integration_paths

子集与任务选择 → AnnData/10x 解析 → 基因标识及表达层核对 → scGPT adapter。GO 辅助文件与基因 ID 映射另行绑定，不能作为分类标签替代。

## preparation_requirements

检查 X/obs/var 维度、稀疏编码、基因唯一性、缺失标签与 batch；验证 reference/query 共享基因顺序，统计原始 split 类别交集。需要学习的预处理仅在训练部分拟合。

## consumption_interfaces

输入是有固定基因顺序的表达向量、所选基因标识和 batch；监督目标为对应细胞类型或扰动后的表达，附带 control/condition 与数据角色。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

根部 Immune_ALL_human.h5ad 为 0 字节，必须排除；perturbation 下同名文件非空，但不能无说明地替换。不能将不同子集的 cell_type/Celltype/celltype 自动混为一列，或在未核查基因顺序时拼接矩阵。
