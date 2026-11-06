## content_principle

FoldBench full1515 多分子结构评测资源。FoldBench 本地 full1515_v20260821 结构评测原语，绑定 AF3 canonical inputs、目标/链映射、MSA registry 和 ground_truth_20250520，区分单体与各类界面评测及权限受限的 manifest。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/foldbench`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。完整读取九类目标 CSV 的表头/行数及 canonical JSON 的记录数/唯一 name，抽查 chain mapping，记录 manifest 权限错误。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

canonical JSON 首条含 `dialect,version,name,sequences,modelSeeds,bondedAtomPairs,userCCD`。单体 CSV 为 `pdb_id,chain_id`；一般界面 CSV 为 `pdb_id,interface_chain_id_1,interface_chain_id_2,interface_chain_type_1,interface_chain_type_2`；抗体表另有 `antibody_chain,antigen_chain`；配体表使用 **`native_chain_id_1/2,native_chain_type_1/2,ligand_id`**，不可套用一般界面列名。chain_id_mapping 为 `pdb_id,original_chain_id,inference_chain_id,remapped`。

## directory_layout

```text
foldbench/
├── foldbench_full1515_v20260821/
│   ├── canonical_input/{alphafold3_inputs_full.json,chain_id_mapping.csv}
│   ├── targets/{monomer_*,interface_*}.csv
│   ├── manifest/{foldbench_run_manifest.csv,manifest_metadata.json}
│   ├── msa_registry/{seq_to_pdb_index.json,mmcif_msa/}
│   └── provenance/{input_generation.csv,input_generation_summary.json,assembly_audit/}
└── foldbench_ground_truths/ground_truth_20250520/*.cif
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

JSON 输入、CSV 目标与映射、CIF 生物学 assembly 参考和 MSA 注册表。外层 boost/openstructure_install 为工具安装目录，不是数据样本。

## scale_spec

9 类 CSV 的本地行数：monomer protein/DNA/RNA=334/14/15；interface antibody-antigen/protein-DNA/protein-ligand/protein-peptide/protein-protein/protein-RNA=172/330/558/51/279/70。行是链或界面目标，不等于独立 assembly 数；full1515 为包名，canonical JSON 完整读取发现 1,522 条记录且 name 均唯一，与 full1515 包名不同；尚未通过受限 manifest 核对这 7 项差异，不能据包名删减输入。

## coverage_spec

蛋白、DNA、RNA 单体及蛋白复合物、配体、肽和抗体相关界面。ground_truth_20250520 是单独的参考快照名称，不能与 full1515_v20260821 的输入打包日期混同。

## label_spec

监督/评测目标为参考 assembly 中指定链或界面的坐标。pdb_id 包含 assembly 后缀，不能只取四字符 PDB ID；需要保留原生链与推理链映射。

## split_strategy

本包是评测资源，不提供本轮已验证的 train/test 划分。按目标类别和 assembly 分组，多个链/界面共享 assembly 时保留关联，避免将类别行随机拆分当独立样本。

## constraints

manifest/foldbench_run_manifest.csv 与 manifest_metadata.json 当前权限不足，不能据此宣称完整运行清单验证成功。配体界面与其他界面的字段不同；MSA registry 只表示资源索引，引用存在性需逐项检查。
