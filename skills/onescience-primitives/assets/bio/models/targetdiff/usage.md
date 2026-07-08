# launch

配体生成采样示例：

```sh
cd "$ONESCIENCE_DIR/examples/biosciences/targetdiff" && python scripts/sample_diffusion.py configs/sampling.yml --data_id 0 --device cuda:0 --batch_size 100 --result_path ./outputs/sample_0
```

属性预测示例：

```sh
cd "$ONESCIENCE_DIR/examples/biosciences/targetdiff" && python scripts/property_prediction/fixed_inference.py --ckpt_path "$ONESCIENCE_MODELS_DIR/targetdiff/pretrained_models/egnn_pdbbind_v2016.pt" --protein_path "$ONESCIENCE_DATASETS_DIR/targetdiff/examples/3ug2_protein.pdb" --ligand_path "$ONESCIENCE_DATASETS_DIR/targetdiff/examples/3ug2_ligand.sdf" --kind Kd --device cuda
```

训练扩散模型示例：

```sh
cd "$ONESCIENCE_DIR/examples/biosciences/targetdiff" && python scripts/train_diffusion.py configs/training.yml
```

# input_schema

- 采样 CLI：
  - `config`: sampling YAML 路径
  - `--data_id`: 测试集样本 ID
  - `--device=cuda:0`
  - `--batch_size=100`
  - `--result_path=./outputs`
- sampling YAML 默认参数：
  - `model.checkpoint=${ONESCIENCE_DATASETS_DIR}/targetdiff/pretrained_models/pretrained_diffusion.pt`
  - `sample.seed=2021`
  - `sample.num_samples=100`
  - `sample.num_steps=1000`
  - `sample.pos_only=false`
  - `sample.center_pos_mode=protein`
  - `sample.sample_num_atoms=prior`
- 数据集由 checkpoint 中的训练配置指定，通常包含：
  - CrossDocked pocket 数据目录
  - pose split 文件
  - protein atom featurizer
  - ligand atom and bond featurizer

# runtime_interfaces

- `sample_diffusion_ligand`: 上层采样函数，批量复制同一口袋并调用模型扩散采样。
- `ScorePosNet3D.forward`: 单步 score/clean sample 预测入口。
- `ScorePosNet3D.sample_diffusion`: 从噪声到配体的完整反向扩散采样入口。
- `ScorePosNet3D.get_diffusion_loss`: 训练损失入口。
- `ScorePosNet3D.fetch_embedding`: 固定坐标提取上下文嵌入。
- `UniTransformerO2TwoUpdateGeneral.forward`: 等变上下文图更新入口。
- `PropPredNet.forward`: 属性预测入口。

# main_functions

- `sample_diffusion_ligand`
- `forward`
- `sample_diffusion`
- `get_diffusion_loss`
- `fetch_embedding`

# execution_resources

- 推荐 GPU；默认 100 个样本、1000 步采样计算量较高。
- 需要 pretrained diffusion checkpoint、CrossDocked 数据集和可写 result path。
- 需要图构建、几何邻域和分子特征处理依赖。
- 采样结果以 PyTorch 对象保存，后续需要专门脚本转换为分子结构文件或评估格式。
- 保存轨迹会增加内存和磁盘占用。

# operation_limits

- TargetDiff 生成的是配体原子坐标和原子类型，不保证成键、价态和可合成性。
- `sample_num_atoms=prior` 是启发式原子数采样，可能需要后处理过滤。
- 生成模型不直接输出 docking 排序或实验亲和力；应后接 docking/score/性质筛选。
- 数据集 ID 驱动的采样适合 benchmark；真实新口袋推理需要准备兼容的数据对象。
- `pos_only=true` 只更新坐标，不适合从零生成完整新分子。
