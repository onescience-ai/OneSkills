# pipeline_responsibility

负责把 CFDBench 的 case 目录数据转换为训练脚本可消费的普通字典 batch，支持二维规则网格上的静态场预测和自回归一步预测。

# pipeline_architecture

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

# data_loading

- 从 `source.data_dir/<problem>/<subset>/case*/` 枚举 case。
- 每个 case 读取 `case.json`、`u.npy`、`v.npy`。
- 根据 problem 类型构造特定 mask，例如圆柱障碍物或 dam 区域。
- `source.data_name` 的前缀用于推断 problem，后缀用于定位 subset。

# sampling_strategy

- 使用 `data.seed` 打乱 case 目录。
- 按 `data.split_ratios` 切出 train/val/test。
- 静态模式按时间帧展开样本。
- 自回归模式按 `delta_time` 换算时间步间隔，形成输入帧和目标帧配对。

# data_transform

- 原始速度场组合为 `[u, v, mask]` 三通道。
- 可选对物性参数和边界条件归一化。
- 静态 collate 输出 `case_params`、`t`、`label`。
- 自回归 collate 输出 `inputs`、`case_params`、`label`、`mask`，并将 mask 从速度通道中拆出。
- `case_params` 会过滤 `rotated/dx/dy` 等非模型输入键。

# input_schema

- `source.data_dir`: CFDBench 根目录。
- `source.data_name`: 如 `tube_prop`、`cavity_bc`、`cylinder_geo`、`dam_prop_bc`。
- `case.json`: 包含问题参数、边界条件、几何尺寸等。
- `u.npy`, `v.npy`: 时间序列速度场。
- `data.task_type`: `auto` 或静态模式值。

# output_schema

- 静态样本 batch：
  - `case_params`: 定长参数张量。
  - `t`: 时间帧索引。
  - `label`: 单帧 `[u, v, mask]` 场张量。
- 自回归样本 batch：
  - `inputs`: 输入速度场。
  - `case_params`: 定长参数张量。
  - `label`: 目标速度场。
  - `mask`: 有效区域或障碍物标记。

# constraints

- problem 仅支持 `tube/cavity/cylinder/dam`。
- 当前只读取 `u.npy` 和 `v.npy`，不读取压力。
- train/val/test 是运行时随机切分，不是固定官方 split。
- `delta_time` 转为整数时间步，不能整除时存在近似。
- `task_type=auto` 与静态模式 batch 协议不同。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/cfdbench.py`
- `{onescience_path}/onescience/examples/cfd/CFD_Benchmark/train.py`
- `{onescience_path}/onescience/examples/cfd/CFD_Benchmark/conf/`
