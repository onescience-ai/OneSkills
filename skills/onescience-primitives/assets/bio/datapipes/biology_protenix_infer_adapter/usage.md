# launch

Python API 示例：

```sh
python -c "from types import SimpleNamespace; from onescience.datapipes.biology.datasets.protein_dataset import ProteinDataset; extra=SimpleNamespace(use_pipeline=False,use_adapter=True,model_name='protenix_infer_adapter',use_msa=True,use_structure=True,max_msa_seqs=512,recursive=False,msa_dirs=[],structure_dirs=[],default_chain_id='A',allow_dummy_sample=False); data=SimpleNamespace(extra=extra); source=SimpleNamespace(path='/path/to/json_dir'); cfg=SimpleNamespace(source=source,data=data,input_json_path='/path/to/protenix_input.json'); ds=ProteinDataset(cfg); item=ds[0]; print(item['result']['sample_name'])"
```

# input_schema

```text
配置:
  input_json_path: Protenix/AF3 JSON
  data.extra.use_adapter: true
  data.extra.model_name: protenix_infer_adapter

JSON:
  sequences: 生物分子实体列表
  covalent_bonds: 可选共价键列表
```

# runtime_interfaces

- `get_adapter("protenix_infer_adapter")`: 从注册表获取 adapter 类。
- `ProtenixInferAdapter.process_json_sample(sample)`: 将 JSON 样本转为 Protenix 推理特征。
- `ProteinDataset.__getitem__(idx)`: 在 `input_json_path` 路径中调用 adapter 并返回 item。

# main_functions

- `get_adapter`
- `process_json_sample`
- `process_sample`
- `__getitem__`

# execution_resources

- 主要消耗 CPU、内存和分子解析依赖。
- ligand 和 CCD 处理可能需要额外化学工具库。
- 大复合物或多 ligand 样本会显著增加 token 和 atom 数量。

# operation_limits

- 只面向 Protenix/AF3 JSON 推理输入。
- 不支持任意自定义 JSON 字段自动映射。
- 不负责 MSA 搜索或模型 forward。
- ligand/非标准残基解析失败时需要先修复输入或补 CCD 信息。
