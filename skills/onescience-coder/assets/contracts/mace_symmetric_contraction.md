# Contract: mace_symmetric_contraction.py

## 基本信息

- 组件名：`MACE Symmetric Contraction`
- 所属模块族：`materials / mace / equivariant`
- 统一入口：`direct_import`
- 注册名：`not_applicable`
- 主源码：`./onescience/src/onescience/modules/equivariant/mace_symmetric_contraction.py`

## 组件职责

实现 MACE 高阶 many-body product basis 的对称收缩，并通过 wrapper 在 e3nn 和 cuEquivariance 路径之间切换。

覆盖组件：

- `SymmetricContraction`
- `Contraction`
- `mace_wrapper_ops.Linear`
- `mace_wrapper_ops.TensorProduct`
- `mace_wrapper_ops.FullyConnectedTensorProduct`
- `mace_wrapper_ops.SymmetricContractionWrapper`

## 输入契约

- 等变节点特征：`(NumAtoms, IrrepsDim)` 或 wrapper 约定形态
- `node_attrs`: 元素 one-hot
- `irreps_in` / `irreps_out`
- `correlation`: 高阶收缩阶数
- `num_elements`: 元素数

## 输出契约

- product basis 后的等变节点特征
- 输出 irreps 必须与后续 readout/interaction 预期一致

## 关键参数

- `correlation`
- `num_elements`
- `use_sc`
- `cueq_config`
- `layout`
- `shared_weights`
- `internal_weights`

## 典型调用位置

- `EquivariantProductBasisBlock`
- `MACE` / `ScaleShiftMACE` 每层 interaction 后
- e3nn <-> cuEquivariance 转换脚本

## 常见修改点

- 改 `correlation`：同步检查 contraction weights 数量和 checkpoint 加载。
- 启用 cuEquivariance：确认依赖是否可用，且 checkpoint 是否需要转换。
- 改 irreps：同步检查 `hidden_irreps`、readout 和 product basis。
- 多元素 fine-tuning：确认 weights 的元素维度是否按新元素表筛选。

## 风险点

- 旧 fine-tuning 代码若写死 `range(2)` 复制 weights，会在 `correlation=2` 模型上越界。
- cuEquivariance 与 e3nn state_dict key 不完全一致，转换要走专用脚本。
- 元素表筛选时只复制部分元素权重，`indices_weights` 必须和 `AtomicNumberTable` 一致。

## 下钻关系

- MACE 主干：`./mace_block.md`
- fine-tuning 权重迁移：`./mace_finetuning_utils.md`
- wrapper/性能路径：源码 `mace_wrapper_ops.py`

## 源码锚点

- `./onescience/src/onescience/modules/equivariant/mace_symmetric_contraction.py`
- `./onescience/src/onescience/modules/equivariant/mace_wrapper_ops.py`
- `./onescience/src/onescience/utils/mace/cli/convert_e3nn_cueq.py`
- `./onescience/src/onescience/utils/mace/cli/convert_cueq_e3nn.py`
