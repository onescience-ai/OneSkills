# Contract: mace_radial.py

## 基本信息

- 组件名：`MACE Radial Family`
- 所属模块族：`materials / mace / layer`
- 统一入口：`direct_import`
- 注册名：`not_applicable`
- 主源码：`./onescience/src/onescience/modules/layer/mace_radial.py`

## 组件职责

提供 MACE 的边距离展开、平滑截断、短程 ZBL 排斥和距离变换。

覆盖组件：

- `BesselBasis`
- `GaussianBasis`
- `ChebychevBasis`
- `PolynomialCutoff`
- `ZBLBasis`
- `AgnesiTransform`
- `SoftTransform`

## 输入契约

- 基函数输入：边距离 `r`，通常形态为 `(NumEdges, 1)` 或 `(NumEdges,)`
- ZBL 输入：距离、`edge_index`、`node_attrs`、`atomic_numbers`
- 距离单位默认按 Angstrom 语义使用

`r_max` 必须和构图 cutoff 保持一致；只改模型里的 radial cutoff 而不改 datapipe 构图会造成训练和推理不一致。

## 输出契约

- 径向基输出：`(NumEdges, NumBasis)`
- cutoff envelope：可广播到边特征的 `(NumEdges,)`
- `ZBLBasis` 输出：逐原子短程能量贡献

## 关键参数

- `r_max`
- `num_basis`
- `num_bessel`
- `num_polynomial_cutoff`
- `p`
- `trainable`
- `radial_type`
- `distance_transform`

OneScience demo 常见值：

- `r_max=4.0~6.0`
- `num_bessel=8`
- `num_polynomial_cutoff=5/6`
- `radial_type="bessel"`

## 典型调用位置

- `RadialEmbeddingBlock`
- `MACE` / `ScaleShiftMACE` 边特征构造阶段
- `pair_repulsion=True` 时的 ZBL 分支

## 常见修改点

- 改 cutoff：同时检查 foundation checkpoint 的 `r_max`，fine-tuning 默认不要随意改。
- 改径向基类型：确认 checkpoint 是否可兼容加载。
- 启用 ZBL：确认 `atomic_numbers` 和 `node_attrs` 的元素映射正确。
- 改距离变换：检查极短距离和高压/碰撞构型的数值稳定性。

## 风险点

- `r_max` 与数据单位不一致会导致近邻图过稀或过密。
- foundation fine-tuning 改 cutoff 会改变图结构和 receptive field，通常不是首选。
- `ZBLBasis` 依赖元素 one-hot 映射；元素表错位会产生错误排斥能。
- 距离接近 0 时数值稳定性需要额外检查。

## 下钻关系

- MACE 主干：`./mace_block.md`
- 构图与距离：`./mace_func_utils.md`
- 数据 cutoff：`../datapipes/materials_mace.md`

## 源码锚点

- `./onescience/src/onescience/modules/layer/mace_radial.py`
- `./onescience/src/onescience/modules/block/mace_block.py`
