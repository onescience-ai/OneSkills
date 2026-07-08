# launch

OpenFold 用于 AlphaFold2 风格的蛋白结构预测。用户说“用 OpenFold/AF2 风格预测蛋白结构”“我有 FASTA、MSA 或 template，想跑结构推理”“用 OpenFold 验证一批设计序列结构”时召回。

预训练推理示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/openfold/run_pretrained_openfold.py "$RUN_DIR/openfold_fasta" "$ONESCIENCE_DATA_DIR/pdb_mmcif/mmcif_files" --output_dir "$RUN_DIR/openfold_out" --config_preset model_1_ptm --openfold_checkpoint_path "$ONESCIENCE_MODELS_DIR/openfold/openfold_params.pt" --data_random_seed 0 --model_device cuda:0 --jackhmmer_binary_path jackhmmer --hhblits_binary_path hhblits --hhsearch_binary_path hhsearch --kalign_binary_path kalign --uniref90_database_path "$ONESCIENCE_DB_DIR/uniref90/uniref90.fasta" --mgnify_database_path "$ONESCIENCE_DB_DIR/mgnify/mgy_clusters.fa" --bfd_database_path "$ONESCIENCE_DB_DIR/bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt" --uniclust30_database_path "$ONESCIENCE_DB_DIR/uniclust30/uniclust30_2018_08" --pdb70_database_path "$ONESCIENCE_DB_DIR/pdb70/pdb70" --max_template_date 2022-01-01
```

已预计算特征的 API 推理适合由执行脚本加载 `feature_dict` 后调用模型：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/openfold/run_pretrained_openfold.py "$RUN_DIR/openfold_features" "$ONESCIENCE_DATA_DIR/pdb_mmcif/mmcif_files" --output_dir "$RUN_DIR/openfold_feature_out" --config_preset model_1_ptm --openfold_checkpoint_path "$ONESCIENCE_MODELS_DIR/openfold/openfold_params.pt" --data_random_seed 0 --model_device cuda:0
```

# input_schema

- 输入对象：蛋白 FASTA 目录、OpenFold feature dict、MSA/template 数据库、checkpoint、输出目录和运行设备。
- FASTA 目录中每条序列应有稳定 ID；设计流程中来自 ProteinMPNN 的候选序列建议拆分为单条 FASTA 或按候选批次组织。
- OpenFold 实现中的 `AlphaFold.forward(batch)` 是 OpenFold 模型类 API，不是 AlphaFold JAX 入口；`batch` 必须是 OpenFold 特征字典，且多数特征最后一维为 recycling cycle。
- 常用默认/显式参数：`config_preset=model_1_ptm`，`data_random_seed=0`，`model_device=cuda:0`，`max_template_date` 必须按任务时间窗给出。
- 需要显式绑定的外部资源：`jackhmmer`、`hhblits`、`hhsearch`、`kalign`，以及 UniRef、MGnify、BFD/UniClust、PDB70、mmCIF/template 库。
- 智能体召回时建议记录：`usage_mode=structure_prediction | design_validation`，`entrypoint=run_pretrained_openfold.py | OpenFold AlphaFold.forward`，`input_artifacts=fasta_dir | feature_dict`，`output_artifacts=pdb | pkl | confidence`，`preflight_checks=database_paths | checkpoint | preset | recycling_dim`。

# runtime_interfaces

- `run_pretrained_openfold.py`：FASTA/MSA/template 到结构结果的预训练推理入口。
- OpenFold `AlphaFold.forward`：接收 OpenFold batch，执行多轮 recycling 并返回结构与置信度相关输出；模型选择仍然是 OpenFold，不是 AlphaFold JAX。
- OpenFold `AlphaFold.iteration`：单轮 embedding、template、extra MSA、Evoformer、StructureModule 计算。
- `FeaturePipeline`：把 FASTA、MSA 和 template 搜索结果转换为模型特征。

# main_functions

- `forward`
- `iteration`

# execution_resources

- 需要 OpenFold checkpoint、蛋白序列数据库、template 数据库、alignment/template 搜索工具和可写输出目录。
- 推荐 GPU；长序列、多 template、多 MSA 命中会明显增加显存和运行时间。
- 长序列或低显存场景可减少 template/MSA、调整 preset、启用低内存 attention 或拆分候选批次。
- 观察项应包含：是否生成 PDB、是否生成 pickle/置信度文件、pLDDT/PAE 是否可解析、失败是否来自数据库、feature、checkpoint 或显存。

# operation_limits

- 不用于核酸、配体或蛋白-核酸-小分子复合物预测；这类任务优先召回 Protenix。
- 不把 RFdiffusion 输出的骨架直接当作 OpenFold 输入；需要先经 ProteinMPNN 或其他方法给出氨基酸序列。
- 不把 AlphaFold3/Protenix JSON、ESM embedding 或普通 FASTA tensor 直接塞给 OpenFold `AlphaFold.forward`。
- 数据库、alignment 工具或 template 资源缺失会导致特征流水线失败；此时应改用预计算特征或切换单序列折叠模型。
