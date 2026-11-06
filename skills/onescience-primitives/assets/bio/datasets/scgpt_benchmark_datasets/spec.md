## content_principle

scGPT 单细胞注释、整合与扰动基准集合。scGPT 本地单细胞基准数据原语，覆盖 BMMC、肺/COVID、胰腺、髓系/MS、PBMC 和 Adamson/Norman，区分 H5AD 表达层、子集标签及 reference/query、train/test 角色。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/scGPT`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。HDF5 只读检查已覆盖全部 13 个 H5AD 的 X 编码、维度、obs/var 列及 layers/obsm；未全量评估表达质量。卡片版本描述原语修订，不代表上游数据发布版本。

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

## directory_layout

```text
scGPT/
├── BMMC_processed.h5ad
├── Kim2020_Lung.h5ad
├── covid_subsampled.h5ad
├── Immune_ALL_human.h5ad                 # 0 字节，无效
├── annotation_pancreas/demo_{train,test}.h5ad
├── myeloid/{reference_adata,query_adata}.h5ad
├── ms/{c_data,filtered_ms_adata}.h5ad
├── pbmc10k/{pbmc4k,pbmc8k}/filtered_gene_bc_matrices/
└── perturbation/
    ├── Immune_ALL_human.h5ad             # 非空，独立入口
    ├── {adamson,norman}/perturb_processed.h5ad
    └── {gene2go.pkl,adamson.zip,norman.zip}
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

AnnData/HDF5：X 含 CSR 与 dense 两种存储。优先用 `anndata.read_h5ad(..., backed="r")` 做元数据与分块检查。10x 文件使用对应 Matrix Market 读取接口；压缩包、GO 映射和元数据不是额外的细胞样本。

## scale_spec

本轮核对 13 个 H5AD 路径，其中 12 个有效、1 个空文件。X 元数据：BMMC 90,261×14,087；肺 32,493×20,793；COVID 20,000×1,200；pancreas train 10,600×3,000、test 4,218×3,000；myeloid reference 9,748×3,000、query 3,430×3,000；MS 两文件分别 7,844×3,000 和 13,468×3,000；Adamson 68,603×5,060、Norman 91,205×5,045；perturbation/Immune 33,506×12,303。

## coverage_spec

细胞注释、批次整合、参考映射和单细胞扰动响应预测。BMMC 的 ADT/GEX 表示存在于 obsm，不能直接当作同一表达层；各数据集的基因数和特征筛选不同。

## label_spec

细胞类型列名严格按上表区分大小写；扰动的 `condition` 与 `control` 需共同解释，并保留组合扰动字符串。PBMC 元数据须按 barcode 连接。未核实的 X 归一化方式不得按文件名推断。

## split_strategy

保留 pancreas 的 demo_train/demo_test、myeloid 的 reference/query 与 BMMC 的 is_train。reference/query 不天然等价于监督 train/test。Adamson/Norman 应按扰动身份及组合泛化协议划分，不能简单随机拆细胞后宣称未见扰动评测。其余分割需明确协议。

## constraints

根部 Immune_ALL_human.h5ad 为 0 字节，必须排除；perturbation 下同名文件非空，但不能无说明地替换。不能将不同子集的 cell_type/Celltype/celltype 自动混为一列，或在未核查基因顺序时拼接矩阵。
