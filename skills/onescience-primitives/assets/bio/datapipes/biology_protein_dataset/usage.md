# launch

Python API 示例：

```sh
python -c "from types import SimpleNamespace; from onescience.datapipes.biology.dataloader import get_protein_dataloader; extra=SimpleNamespace(use_pipeline=True,use_adapter=True,model_name='protenix_infer_adapter',use_msa=True,use_structure=True,max_msa_seqs=512,recursive=True,msa_dirs=[],structure_dirs=[],default_chain_id='A',allow_dummy_sample=False); data=SimpleNamespace(extra=extra); source=SimpleNamespace(path='/path/to/protein_inputs'); cfg=SimpleNamespace(source=source,data=data,input_json_path='/path/to/input.json',num_workers=0); loader=get_protein_dataloader(cfg); print(next(iter(loader)))"
```

# input_schema

```text
必备:
  source.path: 蛋白输入根目录或文件

Protenix 推理优先路径:
  input_json_path: Protenix/AF3 JSON
  data.extra.use_adapter: true
  data.extra.model_name: protenix_infer_adapter

通用蛋白路径:
  data.extra.use_pipeline: true
  data.extra.use_msa: true | false
  data.extra.use_structure: true | false
  data.extra.msa_dirs: MSA 目录列表
  data.extra.structure_dirs: 结构目录列表
```

# runtime_interfaces

- `get_protein_dataloader(configs)`: 构建蛋白数据加载器。
- `get_multimer_dataloader(configs)`: 构建多链/复合物数据加载器。
- `ProteinDataset(configs)`: 发现和组织蛋白样本。
- `MultimerDataset(configs)`: 在蛋白样本基础上增加多链元信息。

# main_functions

- `get_protein_dataloader`
- `get_multimer_dataloader`
- `process_sample`
- `process_json_sample`
- `__getitem__`

# execution_resources

- 主要消耗 CPU、内存和文件 I/O。
- 解析结构文件、MSA 和 Protenix JSON 时依赖生物结构处理相关库。
- 若使用分布式采样，调用方需要在外部初始化分布式环境。
- 大规模 MSA 和结构文件会增加内存占用，建议先用小样本确认输出协议。

# operation_limits

- 非 JSON 训练路径目前不是完整稳定实现。
- 不负责自动生成 MSA、模板搜索或结构修复。
- Protenix adapter 依赖 Protenix 数据特征化模块，缺少依赖会失败。
- batch size 固定为 1 的约定适合复杂结构样本，若要合并 batch 需另写 collate。
