## content_principle

Boltz 结构训练与推理输入资源包。Boltz 本地 RCSB/OpenFold 结构及 MSA 资源原语，绑定 Manifest、结构 NPZ、MSA NPZ、CCD/mols 和 FoldBench YAML 推理输入，区分下载缓存与可用训练资源。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/Boltz_dataset`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。读取两份 manifest 的首条完整记录、两份结构和两份 MSA 的 NPZ 数组头，抽查推理 YAML；未扫描全部引用。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

Manifest 为 JSON 记录数组；抽查记录含 `id,structure,chains,interfaces,affinity,md`（来源间可选字段不同）。structure 含 method/resolution/日期；chains 含 chain_id、chain_name、mol_type、cluster_id、msa_id、template_id、num_residues、valid。

结构 NPZ 抽查键：`atoms,bonds,residues,chains,connections,interfaces,mask,coords,ensemble`，为带 dtype 的结构化数组；MSA NPZ 为 `sequences,deletions,residues`。结构原子坐标及 is_present 不是普通监督 label。YAML 推理输入包含 `version,sequences`，每个实体按 protein/ligand 等类型提供 id、sequence、msa 或 ccd。

## directory_layout

```text
Boltz_dataset/
├── training/
│   ├── {rcsb,openfold}/
│   │   ├── targets/{manifest.json,structures/}
│   │   └── msa/*.npz
│   └── symmetry.pkl
├── ccd.pkl
├── mols/*.pkl
├── infer_input_data/foldbench_full1515_v20260821/
│   ├── input/{yaml,msa}/
│   ├── validation/boltz_adapter_report.json
│   └── {context,logs,provenance}/
└── official_train_download/.cache/
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

JSON manifest、NumPy NPZ 结构化数组、YAML/A3M 和化学组分 pickle。Manifest 大文件采用流式或分段解析；本次读取前缀第一条记录和 NPZ 数组头，未加载完整结构库。化学 pickle 必须由匹配 Boltz/化学工具版本读取。

## scale_spec

RCSB/OpenFold manifest 分别约 772 MB/108 MB，本轮未统计全部记录或检查全部引用文件。示例 4gpn 结构头记录 7,898 个 atom、966 个 residue、6 条 chain。official_train_download 当前仅见 .cache，不能据此声明完整官方训练集下载完成。

## coverage_spec

RCSB 与 OpenFold 来源结构及 MSA、CCD/分子字典、对称性资源和 FoldBench 到 Boltz 的 YAML 输入适配。预测结果与评测对另由 boltz_structure_benchmark 描述。

## label_spec

原子坐标、存在性掩码和结构/链 metadata 形成结构学习目标。mol_type/元素/残基枚举按匹配 Boltz 版本解释，msa_id=-1 等占位符不可当文件名。OpenFold 来源质量/日期占位值不能伪装为实验分辨率或真实发表日期。

## split_strategy

本地 manifest 未在本轮核实官方 train/validation/test 协议；记录来源、cluster_id 和时间筛选规则，由消费配置绑定。FoldBench 推理输入是评测来源，不能无说明混入训练。

## constraints

必须验证结构→chain→MSA 的引用一致性及化学字典版本。YAML 中 MSA 有绝对本地路径，迁移时在输入副本中重定位并核对存在性。validation/boltz_adapter_report.json 当前无读取权限，因此不能宣称整个适配包已验证通过。
