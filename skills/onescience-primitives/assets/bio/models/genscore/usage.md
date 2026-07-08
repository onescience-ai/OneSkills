# launch

常规打分示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/genscore/genscore.py -p "$ONESCIENCE_DATASETS_DIR/GenScore/genscore_data/inferdata/1qkt_p_pocket_10.0.pdb" -l "$ONESCIENCE_DATASETS_DIR/GenScore/genscore_data/inferdata/1qkt_decoys.sdf" -e gatedgcn -m "$ONESCIENCE_DATASETS_DIR/GenScore/trained_models/GatedGCN_0.5_1.pth" -o examples/biosciences/genscore/out --batch_size 8 --num_workers 0
```

从全蛋白和参考配体生成口袋后打分：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/genscore/genscore.py -p "$ONESCIENCE_DATASETS_DIR/GenScore/genscore_data/inferdata/1qkt_p.pdb" -l "$ONESCIENCE_DATASETS_DIR/GenScore/genscore_data/inferdata/1qkt_decoys.sdf" -rl "$ONESCIENCE_DATASETS_DIR/GenScore/genscore_data/inferdata/1qkt_l.sdf" -gen_pocket -c 10.0 -e gt -m "$ONESCIENCE_DATASETS_DIR/GenScore/trained_models/GT_0.0_1.pth" -o examples/biosciences/genscore/out --batch_size 8 --num_workers 0
```

训练示例：

```sh
cd "$ONESCIENCE_DIR" && python -m onescience.models.genscore.train --data_dir "$ONESCIENCE_DATASETS_DIR/GenScore/genscore_data/train" --data_prefix v2020_train --model_path genscore.pth --encoder gt --num_epochs 5000 --batch_size 64
```

# input_schema

- 推理必需参数：
  - `--prot`: 蛋白或口袋 PDB
  - `--lig`: 配体 SDF/MOL2
- 推理默认参数：
  - `--model`: 默认指向 examples 中的 `GT_0.0_1.pth`
  - `--encoder=gt`
  - `--outprefix=out`
  - `--gen_pocket=false`
  - `--cutoff=10.0`
  - `--reflig=None`
  - `--parallel=false`
  - `--atom_contribution=false`
  - `--res_contribution=false`
  - `--batch_size=128`
  - `--num_workers=10`
  - runtime 默认 `device=cuda`，无 GPU 时回退 `cpu`
- 训练默认参数：
  - `--num_epochs=5000`
  - `--batch_size=64`
  - `--aux_weight=0.001`
  - `--affi_weight=-0.5`
  - `--patience=70`
  - `--encoder=gt`
  - `--mode=lower`
  - `--valnum=1500`
  - `--seeds=126`
  - `--hidden_dim0=128`
  - `--hidden_dim=128`
  - `--n_gaussians=10`
  - `--dropout_rate=0.15`
  - `--dist_threhold=7.0`
  - `--dist_threhold2=5.0`

# runtime_interfaces

- `scoring`: Python API 推理入口，构造数据集、加载模型并返回 score 或贡献分析结果。
- `_build_encoder`: 根据 `gt` 或 `gatedgcn` 创建配体和蛋白图编码器。
- `GenScore.forward`: 主模型前向，输出混合密度参数和辅助预测。
- `GraphTransformer.forward`: 图 Transformer 编码入口。
- `GatedGCN.forward`: GatedGCN 编码入口。
- `train.main`: 训练入口，负责数据划分、训练循环、验证和早停。
- `inference.main`: CLI 推理入口，负责保存 CSV。

# main_functions

- `scoring`
- `forward`
- `_build_encoder`
- `main`

# execution_resources

- 推荐 GPU；CPU 可跑小批量推理但图构造和评估较慢。
- 需要蛋白/口袋 PDB、配体 SDF/MOL2、对应 encoder 的 checkpoint。
- `--gen_pocket` 需要参考配体，且会依赖分子空间邻域截断。
- 输出 CSV 写入当前工作目录或 `--outprefix` 指定位置。
- 训练需要预处理后的 PDBbind 数据张量和足够磁盘空间保存 checkpoint。

# operation_limits

- GenScore 是打分器，不生成新的配体构象。
- 输入若是全蛋白且未生成口袋，评分会受到远离口袋区域干扰；建议提供口袋 PDB 或启用 `--gen_pocket`。
- 贡献分析是模型内归因信号，不等同于严格物理能量分解。
- checkpoint 与 encoder 不匹配时无法可靠运行。
- 多配体 SDF 批量推理时应检查输出 `id` 与原始构象顺序是否一致。
