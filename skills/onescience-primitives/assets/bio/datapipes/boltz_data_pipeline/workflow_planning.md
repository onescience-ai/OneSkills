# description

该原语用于规划 Boltz 风格生物分子结构数据处理。决策重点是输入处于序列/MSA/schema/manifest 哪个层级，任务目标是解析、过滤、裁剪、token 化、特征化还是结构写出，并确认是否需要 ligand/对称性处理。

# when_to_use

- 输入或目标协议是 Boltz 风格。
- 需要解析 Boltz schema、FASTA、A3M、YAML 或 CSV manifest。
- 需要结构 crop、filter、tokenize 或 symmetry feature。
- 需要将内部结构写出为 PDB/mmCIF。

# inputs

- 输入文件类型和路径。
- schema 中的 chain、residue、atom、bond 信息。
- MSA 是否存在。
- 过滤条件：日期、分辨率、大小、ligand、clash 等。
- 裁剪策略：随机、链、界面或 slice。
- 输出格式需求。

# outputs

```text
datapipe_choice:
  name: boltz_data_pipeline
  action: parse | filter | crop | tokenize | featurize | write | reject

data_contract:
  input_protocol: fasta | a3m | yaml | csv | boltz_schema
  output_protocol: boltz_tokens | boltz_features | pdb | mmcif
  handles_symmetry: true

risk_flags:
  - schema_incomplete
  - ligand_conformer_failed
  - crop_removes_target_region
  - filter_too_strict
  - protocol_mismatch
```

# procedure

1. 确认任务是否需要 Boltz 协议。
2. 识别输入类型：FASTA、A3M、YAML、CSV 或 schema。
3. 若是结构任务，先解析 schema 并检查 atom/bond/residue/chain。
4. 按任务目标选择 filter、crop、tokenize、feature 或 writer。
5. 对 ligand 和 symmetry 相关样本做额外校验。
6. 小样本检查 token 数、atom 数、crop mask 和输出格式。

# constraints

- 不要把 Boltz feature 当作 OpenFold 或 Protenix feature。
- 不要在未检查目标区域时使用 aggressive crop。
- 不要忽略 ligand 对称性和等价原子映射。
- 过滤配置必须能解释样本被丢弃的原因。

# next_phase_recommendation

- 模型训练：固定 filter/crop 策略并生成样本统计。
- 推理输入：先完成 schema 解析和 token 化。
- 结构写出：先验证 atom/bond annotation 完整性。
- ligand-heavy 数据：先检查 conformer 和 symmetry 处理。

# fallback

- schema 解析失败：退回 FASTA/A3M 层级或修复 atom/bond 字段。
- ligand conformer 失败：替换 ligand 表示或补充化学信息。
- crop 丢失关键区域：改用界面 token 或固定 target token。
- writer 失败：先输出内部结构摘要，再定位缺失 annotation。
