# launch

Python API 示例：

```sh
python -c "from onescience.datapipes.boltz_data_pipeline.parse.fasta import parse_fasta; from onescience.datapipes.boltz_data_pipeline.parse.a3m import parse_a3m; seqs=parse_fasta('/path/to/input.fasta'); msa=parse_a3m('/path/to/input.a3m'); print(len(seqs), type(msa).__name__)"
```

# input_schema

```text
基础输入:
  fasta_path: 可选蛋白序列
  a3m_path: 可选 MSA
  yaml_path/csv_path: 可选配置或 manifest
  schema_input: Boltz schema 结构输入

处理配置:
  filters: 静态/动态过滤条件
  crop: crop 策略和 token 数
  output_format: pdb | mmcif
```

# runtime_interfaces

- `parse_fasta`: 读取 FASTA。
- `parse_a3m`: 读取 A3M。
- `parse_yaml` / `parse_csv`: 读取输入配置或 manifest。
- `parse_boltz_schema`: 将 schema 转为结构对象。
- `BoltzTokenizer`: 生成 token 数据。
- `BoltzFeaturizer`: 生成模型特征。
- `BoltzWriter`: 写出 PDB/mmCIF。

# main_functions

- `parse_fasta`
- `parse_a3m`
- `parse_yaml`
- `parse_csv`
- `parse_boltz_schema`
- `tokenize`
- `process_token_features`
- `process_atom_features`
- `process_symmetry_features`
- `to_pdb`
- `to_mmcif`

# execution_resources

- 解析、过滤、裁剪和特征化主要消耗 CPU 与内存。
- ligand conformer 和 symmetry 处理可能依赖化学工具。
- 大复合物和深 MSA 会增加内存占用。
- 写出 PDB/mmCIF 需要目标路径具备写权限。

# operation_limits

- 输入必须能映射到 Boltz 内部结构类型。
- 不生成 OpenFold/Protenix batch。
- 不自动执行外部 MSA 搜索。
- crop 和 filter 可能丢弃重要结构区域，需要与任务目标核对。
