# Component Contract: UMA Material Stack

## 适用场景

- 用户要训练、微调、评估或部署 UMA / HydraModel / eSCNMDBackbone。
- 任务涉及 OC20、OMAT、OMOL、ASE DB/LMDB、Hydra、`elem_refs`、`normalizer_rmsd`。
- 需要处理 energy、forces、stress、多任务 head、dataset-specific head 或 MoE。
- 需要排查 UMA 的 `Jd.pt`、PBC 图构建、charge/spin、dataset embedding。
- 需要把 UMA checkpoint 接到 ASE calculator、结构弛豫、MD、spin gap 或批推理。
- 需要理解 UMA 源码组件，而不是只改外层 demo 配置。

## 不适用场景

- 只是判断材料任务该走 MACE 还是 UMA：先看 role 层 `matchem_task_index.md`。
- 只是准备 UMA 训练数据：先看 `../datapipes/materials_uma.md`。
- 只是 MACE/extxyz/foundation fine-tuning：不要从 UMA stack 开始。
- 只是普通 ASE 单点推理：先看 `./uma_calculator.md`。
- 只是新增未登记材料模型：参考本卡结构，但不要套用 UMA 的 Hydra/AtomicData 协议。

## 下钻表

| 问题类型 | 先读文件 | 继续下钻 |
| --- | --- | --- |
| 模型路线与 Hydra 入口 | `../models/uma.md` | `../datapipes/materials_uma.md` |
| 参数生成 / 配置裁剪 | `./uma_parameter_policy.md` | `../models/uma.md` |
| HydraModel / checkpoint / heads 装配 | `./uma_hydra_model.md` | `./uma_head.md` |
| train/eval unit、tasks、scheduler | `./uma_mlip_unit.md` | `./uma_loss.md` |
| charge/spin/dataset/edge degree embedding | `./uma_embedding.md` | `./uma_moe.md` |
| eSCNMD block / SO3 消息传递 | `./uma_escn_md_block.md` | `./uma_radial.md` |
| 高斯径向基、edge MLP、cutoff | `./uma_radial.md` | `./uma_graph_compute.md` |
| PBC 近邻图、otf graph、max_neighbors | `./uma_graph_compute.md` | `../datapipes/materials_uma.md` |
| `Jd.pt` 路径解析 | `./uma_path_utils.md` | `./uma_hydra_model.md` |
| energy/forces/stress loss | `./uma_loss.md` | `./uma_normalization.md` |
| elem_refs / normalizer_rmsd | `./uma_normalization.md` | `../datapipes/materials_uma.md` |
| MoE / dataset routing | `./uma_moe.md` | `./uma_embedding.md` |
| ASE/relax/MD/batch inference | `./uma_calculator.md` | `./uma_graph_compute.md` |

## 必读顺序

1. 先读 `../models/uma.md`，确认当前任务确实是 UMA/Hydra 路线。
2. 再读 `../datapipes/materials_uma.md`，确认 ASE DB/LMDB、dataset、charge/spin、pbc。
3. 若需要写训练、fine-tuning、验证或推理参数，读 `./uma_parameter_policy.md`。
4. 若是训练，读 `./uma_hydra_model.md`、`./uma_mlip_unit.md`、`./uma_loss.md`。
5. 若是归一化或参考能问题，读 `./uma_normalization.md`。
6. 若是源码级结构问题，按下钻表读 embedding/block/radial/graph/path/MoE。
7. 若是推理部署，读 `./uma_calculator.md`，再回到数据卡核对任务条件。

## 风险总览

- `Jd.pt` 是运行依赖；新环境优先显式设置 `jd_path` 或 `ONESCIENCE_UMA_JD_PATH`。
- UMA 数据协议是 `custom_stack AtomicData`，不能直接复用 MACE extxyz batch。
- `dataset_name`、dataset embedding、head wrapper、normalizer 必须同源。
- `elem_refs` 元素索引错位会造成系统性能量偏移。
- `normalizer_rmsd` 复用错误会让 loss 和 metric 失真。
- 分子任务必须确认 charge/spin；晶体/吸附任务必须确认 cell/pbc/tags/fixed。
- batch 内混合 PBC 可能触发图构建或 calculator 错误。
- `direct_forces`、energy-gradient forces、stress reshape 必须和 head/loss 配置一致。
- MoE checkpoint 与普通 eSCNMD checkpoint 通常不能直接互换。
