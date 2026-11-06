## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/foldbench`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/foldbench`。



已绑定的资源入口：

- `foldbench/foldbench_full1515_v20260821/canonical_input`
- `foldbench/foldbench_full1515_v20260821/targets`
- `foldbench/foldbench_full1515_v20260821/msa_registry`
- `foldbench/foldbench_full1515_v20260821/provenance`
- `foldbench/foldbench_ground_truths/ground_truth_20250520`

## data_schema

canonical JSON 首条含 `dialect,version,name,sequences,modelSeeds,bondedAtomPairs,userCCD`。单体 CSV 为 `pdb_id,chain_id`；一般界面 CSV 为 `pdb_id,interface_chain_id_1,interface_chain_id_2,interface_chain_type_1,interface_chain_type_2`；抗体表另有 `antibody_chain,antigen_chain`；配体表使用 **`native_chain_id_1/2,native_chain_type_1/2,ligand_id`**，不可套用一般界面列名。chain_id_mapping 为 `pdb_id,original_chain_id,inference_chain_id,remapped`。

## task_usage

从目标 CSV 选择评测单位，再定位 canonical input、链映射、MSA 和参考 CIF；指定结构/界面指标及工具版本后评测。

## integration_paths

目标类别/assembly → 原生与推理链映射 → 工具输入 adapter → 对应参考结构 → 分类别结构/界面评测。

## preparation_requirements

核对每类表头、canonical name、参考 CIF 与 assembly 后缀、链映射和 MSA 引用；固定配体/肽定义、对称映射及失败分母。

## consumption_interfaces

target_category、assembly pdb_id、目标链/界面、canonical input、chain mapping、MSA/reference 路径和验证状态；不默认所有目标可执行。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

manifest/foldbench_run_manifest.csv 与 manifest_metadata.json 当前权限不足，不能据此宣称完整运行清单验证成功。配体界面与其他界面的字段不同；MSA registry 只表示资源索引，引用存在性需逐项检查。
