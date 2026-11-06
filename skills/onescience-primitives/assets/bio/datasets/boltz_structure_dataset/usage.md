## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/Boltz_dataset`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/Boltz_dataset`。



已绑定的资源入口：

- `Boltz_dataset/training/rcsb/targets/manifest.json`
- `Boltz_dataset/training/rcsb/msa`
- `Boltz_dataset/training/openfold/targets/manifest.json`
- `Boltz_dataset/training/openfold/msa`
- `Boltz_dataset/ccd.pkl`
- `Boltz_dataset/mols`
- `Boltz_dataset/infer_input_data/foldbench_full1515_v20260821/input`

## data_schema

Manifest 为 JSON 记录数组；抽查记录含 `id,structure,chains,interfaces,affinity,md`（来源间可选字段不同）。structure 含 method/resolution/日期；chains 含 chain_id、chain_name、mol_type、cluster_id、msa_id、template_id、num_residues、valid。

结构 NPZ 抽查键：`atoms,bonds,residues,chains,connections,interfaces,mask,coords,ensemble`，为带 dtype 的结构化数组；MSA NPZ 为 `sequences,deletions,residues`。结构原子坐标及 is_present 不是普通监督 label。YAML 推理输入包含 `version,sequences`，每个实体按 protein/ligand 等类型提供 id、sequence、msa 或 ccd。

## task_usage

训练资源消费按来源 manifest/record 定位结构与 MSA；推理消费选择明确 YAML 和其 A3M/CCD 依赖，不能仅将数据根目录直接交给模型。

## integration_paths

Manifest/Record → Structure/MSA/化学组件 → Boltz 特征 adapter；推理为 YAML 实体/链和 MSA 映射 → 对应版本解析器。可复用已有 boltz_data_pipeline，但需保留本地来源约束。

## preparation_requirements

核对 manifest ID、结构文件、chain/residue/atom 索引与 mask，验证 MSA 行/残基编码、缺失 MSA 政策及 ccd/mols 依赖；对迁移 YAML 检查链 ID 与所有路径。

## consumption_interfaces

结构任务输入 Manifest/Record 和对应 Structure/MSA/CCD；推理任务输入所选 YAML/A3M/化学实体。输出特征必须绑定具体 Boltz 数据类型版本。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

必须验证结构→chain→MSA 的引用一致性及化学字典版本。YAML 中 MSA 有绝对本地路径，迁移时在输入副本中重定位并核对存在性。validation/boltz_adapter_report.json 当前无读取权限，因此不能宣称整个适配包已验证通过。
