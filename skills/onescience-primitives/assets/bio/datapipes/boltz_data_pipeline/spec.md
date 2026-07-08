# pipeline_responsibility

提供 Boltz 风格的生物分子数据处理能力，覆盖输入 schema 解析、FASTA/A3M/YAML/CSV 读取、静态/动态过滤、结构裁剪、蛋白 token 化、atom/token/symmetry 特征化，以及 PDB/mmCIF 写出。

# pipeline_architecture

```text
输入
  YAML / CSV / FASTA / A3M / Boltz schema
  polymer / ligand / atom / bond / residue / chain

类型系统
  types.py
    -> Structure / MSA / Record / Target / Manifest / Input

解析
  parse/fasta.py
  parse/a3m.py
  parse/yaml.py
  parse/csv.py
  parse/schema.py
    -> ParsedAtom / ParsedBond / ParsedResidue / ParsedChain

过滤
  filter/static
    -> ligand exclusion / polymer quality / clash
  filter/dynamic
    -> date / resolution / size / subset / max residues

裁剪
  crop/boltz.py
    -> random token / chain token / interface token
  crop/slice.py
    -> protein token slice

token 与特征
  tokenize/boltz_protein.py
    -> BoltzTokenizer
  feature/featurizer.py
    -> BoltzFeaturizer
  feature/symmetry.py
    -> chain / amino acid / ligand symmetry

写出
  write/pdb.py
  write/mmcif.py
  write/writer.py
```

# data_loading

- FASTA 由 `parse/fasta.py` 读取。
- A3M 由 `parse/a3m.py` 解析为 MSA。
- YAML/CSV 可作为输入配置、manifest 或 target 描述。
- `parse/schema.py` 将 schema 中的原子、键、残基和链转换为结构对象。
- CCD residue 和 3D conformer 生成由 schema 解析辅助完成。

# sampling_strategy

- Boltz pipeline 本身提供结构过滤和 crop 策略，不直接规定训练 split。
- 动态过滤按日期、分辨率、大小、subset、残基数筛样本。
- 静态过滤按 ligand、polymer 长度、未知残基、连续 CA、clash 等筛样本。
- cropper 可按随机 token、链 token、界面 token 或蛋白 slice 选择局部结构。

# data_transform

- 输入 schema 转换为结构、链、残基、原子和键。
- BoltzTokenizer 将蛋白/结构组织为 token 数据。
- BoltzFeaturizer 生成 token feature、atom feature 和 symmetry feature。
- symmetry 模块处理 ligand、氨基酸和链对称性，支持等价坐标选择。
- writer 将内部结构写出为 PDB 或 mmCIF。

# input_schema

```text
Input:
  structure: Structure
  msa: optional MSA
  target: Target
  manifest: optional Manifest

Schema:
  chains:
    residues:
      atoms
      bonds
  ligands: optional
  interfaces: optional

Filter config:
  date / resolution / size / subset / max_residues
  excluded_ligands / polymer quality
```

# output_schema

```text
Tokenized output:
  TokenData
  token features
  atom features
  symmetry features
  crop masks / subset indices

Written structure:
  PDB text/file
  mmCIF text/file
```

# constraints

- 需要输入符合 Boltz schema 或可转换为 Boltz 内部类型。
- 过滤和裁剪策略会改变样本覆盖范围，必须与训练目标一致。
- ligand 对称性和 3D conformer 依赖化学解析能力。
- 不等同于 OpenFold 或 Protenix feature dict。
- 不负责外部 MSA 搜索或模型推理。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/boltz_data_pipeline/types.py`
- `{onescience_path}/onescience/src/onescience/datapipes/boltz_data_pipeline/parse`
- `{onescience_path}/onescience/src/onescience/datapipes/boltz_data_pipeline/filter`
- `{onescience_path}/onescience/src/onescience/datapipes/boltz_data_pipeline/crop`
- `{onescience_path}/onescience/src/onescience/datapipes/boltz_data_pipeline/tokenize`
- `{onescience_path}/onescience/src/onescience/datapipes/boltz_data_pipeline/feature`
- `{onescience_path}/onescience/src/onescience/datapipes/boltz_data_pipeline/write`
