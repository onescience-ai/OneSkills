# Component Contract: MACE Material Stack

## 适用场景

- 用户要训练、微调、评估或部署 MACE / ScaleShiftMACE。
- 任务涉及 `extxyz/.xyz`、`E0s`、`energy_key`、`forces_key`、`stress/virial`。
- 需要基于 foundation checkpoint 做元素筛选、readout 迁移或小数据 fine-tuning。
- 需要排查 MACE block、radial、product basis、loss、autograd 输出的 shape 或权重问题。
- 需要把训练好的 MACE 接到 ASE、MD 或 LAMMPS。
- 需要为后续材料模型抽取“模型卡 + 数据卡 + stack 卡 + 细粒度 contract”的样板。

## 不适用场景

- 只是判断材料任务该走 MACE 还是 UMA：先看 role 层 `matchem_task_index.md`。
- 只是准备 MACE 输入数据：先看 `../datapipes/materials_mace.md`。
- 只是写普通 PyTorch 模型或非原子图模型：不要从本 stack 开始。
- 只是使用已训练模型做单点推理：优先看 `./mace_calculator.md`。
- 只是修改 demo YAML：优先看模型卡 `../models/mace.md` 和数据卡。

## 下钻表

| 问题类型 | 先读文件 | 继续下钻 |
| --- | --- | --- |
| 模型路线与训练入口 | `../models/mace.md` | `../datapipes/materials_mace.md` |
| 参数生成 / 配置裁剪 | `./mace_parameter_policy.md` | `../models/mace.md` |
| foundation fine-tuning / checkpoint 迁移 | `./mace_finetuning_utils.md` | `./mace_symmetric_contraction.md` |
| block、readout、force/stress 输出 | `./mace_block.md` | `./mace_func_utils.md` |
| `r_max`、Bessel、cutoff、ZBL | `./mace_radial.md` | `../datapipes/materials_mace.md` |
| product basis / contraction 权重 | `./mace_symmetric_contraction.md` | `./mace_finetuning_utils.md` |
| 构图、scatter、autograd、batch | `./mace_func_utils.md` | `./mace_block.md` |
| energy/forces/stress/virial loss | `./mace_loss.md` | `../datapipes/materials_mace.md` |
| ASE/MD/LAMMPS 部署 | `./mace_calculator.md` | `./mace_func_utils.md` |

## 必读顺序

1. 先读 `../models/mace.md`，确认当前任务确实是 MACE 路线。
2. 再读 `../datapipes/materials_mace.md`，确认数据字段、单位、划分和 `E0s`。
3. 若需要写训练、fine-tuning、验证或部署参数，读 `./mace_parameter_policy.md`。
4. 若是训练或 fine-tuning，读 `./mace_finetuning_utils.md` 和 `./mace_loss.md`。
5. 若是源码级结构问题，按下钻表读 block/radial/contraction/func_utils。
6. 若是推理部署，读 `./mace_calculator.md`，再回到模型卡核对 checkpoint。

## 风险总览

- `node_attrs` 是 `AtomicNumberTable` one-hot，不是直接原子序数。
- `r_max` 同时影响 radial 和构图；fine-tuning 时不要随意改 foundation cutoff。
- `E0s=average` 是便捷策略，小数据或元素计数差异大时可能不稳。
- force/stress/virial 来自 autograd；positions/cell displacement 不能断梯度。
- `ScaleShiftMACE` 对 interaction energy 做 scale/shift，不等同普通 total energy 分解。
- contraction weights 数量与 `correlation/max_L` 有关，迁移代码不能写死长度。
- DDP loss 有样本数/原子数修正，不能用普通 `.mean()` 直接替换。
- LAMMPS 部署必须核对元素顺序、dtype、单位制和 legacy checkpoint alias。
- 混合 DFT 设置、stress 符号或单位不一致时，先处理数据，不要先改模型。
