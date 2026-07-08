# Datapipe: CfdbenchDatapipe

## 基本信息

- Datapipe 名称：`CfdbenchDatapipe`
- 数据类型：`cfd`
- 主要任务：`2d regular-grid CFD benchmark prediction`
- 数据组织方式：`case_directories_with_json_and_velocity_npy`

## pipeline_responsibility

负责把 CFDBench 的 case 目录数据转换为训练脚本可消费的普通字典 batch，支持二维规则网格上的静态场预测和自回归一步预测。

## 管道架构

```text
source.data_name
  -> problem: tube / cavity / cylinder / dam
  -> subset: prop / bc / geo / prop_bc

case 目录
  case.json
    -> 边界条件 / 几何参数 / 物性参数
  u.npy, v.npy
    -> 速度场时间序列

数据组织
  case 列表随机打乱
  -> train / val / test
  -> 静态模式: frame 展开
  -> auto 模式: 输入帧和目标帧配对
  -> collate_fn 整理 case_params、inputs、label、mask
```

## 数据加载

- 从 `source.data_dir/<problem>/<subset>/case*/` 枚举 case。
- 每个 case 读取 `case.json`、`u.npy`、`v.npy`。
- 根据 problem 类型构造特定 mask，例如圆柱障碍物或 dam 区域。
- `source.data_name` 的前缀用于推断 problem，后缀用于定位 subset。

## 采样策略

- 使用 `data.seed` 打乱 case 目录。
- 按 `data.split_ratios` 切出 train/val/test。
- 静态模式按时间帧展开样本。
- 自回归模式按 `delta_time` 换算时间步间隔，形成输入帧和目标帧配对。

## 数据转换

- 原始速度场组合为 `[u, v, mask]` 三通道。
- 可选对物性参数和边界条件归一化。
- 静态 collate 输出 `case_params`、`t`、`label`。
- 自回归 collate 输出 `inputs`、`case_params`、`label`、`mask`，并将 mask 从速度通道中拆出。
- `case_params` 会过滤 `rotated/dx/dy` 等非模型输入键。

## 输入规格

- `source.data_dir`: CFDBench 根目录。
- `source.data_name`: 如 `tube_prop`、`cavity_bc`、`cylinder_geo`、`dam_prop_bc`。
- `case.json`: 包含问题参数、边界条件、几何尺寸等。
- `u.npy`, `v.npy`: 时间序列速度场。
- `data.task_type`: `auto` 或静态模式值。

## 输出规格

- 静态样本 batch：
  - `case_params`: 定长参数张量。
  - `t`: 时间帧索引。
  - `label`: 单帧 `[u, v, mask]` 场张量。
- 自回归样本 batch：
  - `inputs`: 输入速度场。
  - `case_params`: 定长参数张量。
  - `label`: 目标速度场。
  - `mask`: 有效区域或障碍物标记。

## 约束条件

- problem 仅支持 `tube/cavity/cylinder/dam`。
- 当前只读取 `u.npy` 和 `v.npy`，不读取压力。
- train/val/test 是运行时随机切分，不是固定官方 split。
- `delta_time` 转为整数时间步，不能整除时存在近似。
- `task_type=auto` 与静态模式 batch 协议不同。

## 启动方式

Python API 启动示例：

```python
from omegaconf import OmegaConf
from onescience.datapipes.cfd import CFDBenchDatapipe

cfg = OmegaConf.load("conf/cfdbench.yaml")
datapipe = CFDBenchDatapipe(cfg.datapipe, distributed=False)
train_loader, train_sampler = datapipe.train_dataloader()
val_loader, val_sampler = datapipe.val_dataloader()
test_loader = datapipe.test_dataloader()
```

CLI 示例：

```sh
python train.py --config-name cfdbench datapipe.source.data_dir=/data/CFDBench datapipe.source.data_name=cylinder_geo datapipe.data.task_type=auto datapipe.data.delta_time=0.1 datapipe.dataloader.batch_size=16 datapipe.dataloader.eval_batch_size=8
```

## 输入规格

- 数据目录形如 `<data_dir>/<problem>/<subset>/case*/`。
- 每个 case 需要 `case.json`、`u.npy`、`v.npy`。
- `source.data_name` 必须能解析出受支持的 problem 和 subset。
- `split_ratios` 建议三段和为 1。

## 运行接口

- `CFDBenchDataset(config, mode="train"|"val"|"test")`: 构造单个 split。
- `CFDBenchDatapipe(config, distributed=False)`: 构造 train/val/test。
- `train_dataloader()`: 返回训练 loader 和 sampler。
- `val_dataloader()`: 返回验证 loader 和 sampler。
- `test_dataloader()`: 返回测试 loader，batch size 固定为 1。

## 主要函数

- `__getitem__`
- `train_dataloader`
- `val_dataloader`
- `test_dataloader`

## 执行资源

- 主要消耗 CPU 与内存读取 npy 时间序列。
- 规则网格张量 batch 可直接进入常规场模型训练。
- 分布式模式通过 sampler 支持训练/验证切分。

## 操作限制

- 自回归和静态模式不能共用同一训练脚本解包逻辑。
- 大量 case 或长时间序列会增加初始化和内存压力。
- 不提供图边、点云表面标记或三维几何特征。
- 若数据包含压力或更多变量，需要扩展读取和 collate 逻辑。

## 规划决策

### 描述

该原语用于在 CFD benchmark 编排中读取规则网格 case，并根据任务选择静态监督或自回归预测协议。

### 使用时机

- 数据是二维规则网格 CFD case 目录。
- 需要复用 CFD_Benchmark 训练路线。
- 任务关注速度场和 case 级物理参数。
- 需要同时构造 train/val/test。

### 输入

- CFDBench 根目录和 `data_name`。
- `task_type`、`split_ratios`、随机种子。
- 是否归一化物性参数和边界条件。
- 自回归任务的 `delta_time`。

### 输出

- train/val/test dataloader。
- 静态或自回归 batch 字典。
- case 参数张量、速度场张量和 mask。

### 执行步骤

1. 根据 `data_name` 判断 problem 与 subset 是否受支持。
2. 检查每个 case 是否含 `case.json/u.npy/v.npy`。
3. 根据任务选择静态或 `auto` 模式。
4. 设定 split 和随机种子以保证实验可复现。
5. 构造 datapipe，并在训练脚本中使用对应 collate 协议。

### 约束

- 只支持速度双通道加 mask。
- split 随运行配置生成，实验记录需保存 seed 和 ratios。
- problem 特定 mask 逻辑与 case.json 字段绑定。

### 下一阶段建议

若需要压力、温度等更多变量，先扩展 `_load_raw_*` 和 collate；若任务转为 PDEBench HDF5 格式，使用 PDENNEval；若数据是非结构网格或几何点云，使用 AirfRANS、ShapeNetCar 或 DrivAerML。

### 回退策略

- `data_name` 不匹配时手动整理目录到受支持命名。
- `delta_time` 不整除时改用数据原生时间步间隔。
- 内存压力大时降低 batch size 或缩短时间序列。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/cfdbench.py`
- `{onescience_path}/onescience/examples/cfd/CFD_Benchmark/train.py`
- `{onescience_path}/onescience/examples/cfd/CFD_Benchmark/conf/`
