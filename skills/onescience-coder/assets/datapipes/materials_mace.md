# Datapipe Card: Materials MACE

## 基本信息

- Datapipe 名：`MaterialsDatapipe / MACE extxyz pipeline`
- 领域：`materials / MLIP`
- 典型任务：MACE 训练、fine-tuning、评估、MD 前模型准备
- 主要源码：`./onescience/src/onescience/datapipes/materials/pyg_stack/`

## 数据定位

MACE 路线的首选数据格式是 `.xyz` / `.extxyz`。OneScience 的 MACE demo 训练入口通常直接把文件路径传给 `examples/matchem/mace/train.py`，由 MACE 工具链读取、划分、构图并生成 `AtomicData`。

本卡也是材料模型数据卡的当前标准样板。新增模型的数据卡应沿用本卡的组织方式，但必须替换为新模型自己的原始格式、样本返回协议、关键字段和训练配置桥接。

当需要写新 datapipe 或接入主库时，优先复用：

- `pyg_stack.core.utils.load_from_xyz`
- `pyg_stack.core.utils.config_from_atoms`
- `pyg_stack.core.atomic_data.AtomicData.from_config`
- `pyg_stack.storage.text_dataset.TextDataset`

## 输入文件约定

### extxyz / xyz

每帧至少需要：

- 原子种类
- 原子坐标
- cell / pbc，周期体系必须正确
- system-level energy
- atom-level forces
- 可选 stress / virial

字段 key 必须与训练参数一致：

- `energy_key`
- `forces_key`
- `stress_key`
- `virials_key`

新数据建议避免直接使用裸 `energy` / `forces` 字段，优先使用 `REF_energy` / `REF_forces` 这类明确参考标签。

### DeepMD 数据

DeepMD `npy/raw` 数据不能直接喂给 MACE。推荐路径：

1. 用 dpdata 读取 DeepMD 数据目录
2. 指定 `type_map`
3. 写出单目录 extxyz
4. 合并为 `total_mace.xyz`
5. 再划分 train/valid/test

参考：`mace-ft-tutorial-main/examples/LiGePS-SSE-PBE/deepmd2mace.py`

## 样本返回协议

`AtomicData.from_config` 生成 PyG 风格样本，核心字段：

- `edge_index`: `(2, NumEdges)`
- `node_attrs`: `(NumAtoms, NumElements)`
- `positions`: `(NumAtoms, 3)`
- `shifts`: `(NumEdges, 3)`
- `unit_shifts`: `(NumEdges, 3)`
- `cell`: `(3, 3)`
- `forces`: `(NumAtoms, 3)`
- `energy`: scalar
- `stress`: `(1, 3, 3)`，可选
- `virials`: `(1, 3, 3)`，可选

构图由 `cutoff/r_max` 控制，元素表由 `AtomicNumberTable` 控制。

## 训练配置桥接

demo YAML 中最常改：

- `train_args.train_file`
- `train_args.test_file`
- `train_args.valid_file` 或 `valid_fraction`
- `train_args.energy_key`
- `train_args.forces_key`
- `train_args.stress_key`
- `train_args.E0s`
- `train_args.r_max`
- `train_args.batch_size`
- `train_args.energy_weight`
- `train_args.forces_weight`
- `train_args.stress_weight`

若是 fine-tuning，再补：

- `train_args.foundation_model`
- `train_args.scaling`
- `train_args.lr`
- `train_args.num_samples_pt`
- `train_args.ema`
- `train_args.swa`

## 推荐数据策略

- 入门或已有高质量数据：直接 extxyz + `valid_fraction`
- 固态晶体/缺陷：随机原子扰动 + 必要的小应变扰动
- 液体/无定形/界面：AIMD/MC/增强采样抽帧
- 大候选池：用多 seed ensemble 或力不确定性筛选，再加结构多样性过滤
- 下游 MD：验证集必须覆盖目标温度、密度、缺陷/界面构型

## 风险点

- `valid_fraction` 太大或测试集与训练集同源太强，会高估泛化。
- `E0s=average` 对小数据或元素计数相关数据可能不稳；高精度任务优先给显式 E0s。
- stress/virial 符号和单位必须查数据来源，不能只看字段名。
- 混合 DFT 设置的数据不应直接合并，除非明确做多头或重新归一化。
- 训练脚本和模型都依赖 `r_max` 构图；改 cutoff 会改变样本图结构。

## 源码锚点

- `./onescience/src/onescience/datapipes/materials/pyg_stack/core/utils.py`
- `./onescience/src/onescience/datapipes/materials/pyg_stack/core/atomic_data.py`
- `./onescience/src/onescience/datapipes/materials/pyg_stack/core/neighborhood.py`
- `./onescience/src/onescience/datapipes/materials/pyg_stack/storage/text_dataset.py`
- `./onescience/src/onescience/datapipes/materials/tools/utils.py`
- `./onescience/examples/matchem/mace/train.py`
- `./onescience/examples/matchem/mace/demo/configs/*.yaml`
