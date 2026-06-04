# Contract: OpenFoldStructureModule

## 基本信息

- 组件名：`StructureModule`
- 所属模块族：`decoder`
- 统一入口：`OneDecoder`
- 注册名：`style="OpenFoldStructureModule"`
- 注册状态：`contract_only`

## 组件职责

OpenFold StructureModule 负责把 Evoformer 输出的 single/pair 表征转换为蛋白质三维结构，是 AF2-style folding 中的坐标恢复模块。

补充说明：

- 契约层统一收束到 `OneDecoder`，源码当前仍在 `onescience.models.openfold` 内部直接实例化
- 该模块使用 Invariant Point Attention、backbone update 和 angle resnet
- monomer 与 multimer 会走不同 IPA / backbone update 分支
- 输出的是 atom14 中间结构，再由 `atom14_to_atom37` 转成 final atom37 坐标

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- 主输入：
  - `evoformer_output_dict["single"]`: `[*, N_res, C_s]`
  - `evoformer_output_dict["pair"]`: `[*, N_res, N_res, C_z]`
  - `aatype`: `[*, N_res]`
  - `mask`: `[*, N_res]`

内部统一做法：

- 对 single 与 pair 表征分别 LayerNorm
- 初始化每个 residue 的刚体 frame
- 多轮执行 IPA、dropout、transition、backbone rigid update
- 用 AngleResnet 预测 torsion / angle
- 根据 frames 和 torsions 生成 atom14 positions

## 构造参数

- `c_s`
- `c_z`
- `c_ipa`
- `c_resnet`
- `no_heads_ipa`
- `no_qk_points`
- `no_v_points`
- `dropout_rate`
- `no_blocks`
- `no_transition_layers`
- `no_resnet_blocks`
- `no_angles`
- `trans_scale_factor`
- `epsilon`
- `inf`
- `is_multimer=False`

## 输出约定

- `positions`: 多个结构模块 block 的 atom14 坐标
- `frames`: 多个 block 的 backbone frames
- `unnormalized_angles`
- `angles`
- AlphaFold 外层会转出：
  - `final_atom_positions`: `[*, N_res, 37, 3]`
  - `final_atom_mask`
  - `final_affine_tensor`

如果有明确边界条件，也写在这里：

- `mask` 应与 `single[..., N_res, :]` 对齐
- `pair` 必须保留与 single 相同的 `N_res`
- multimer 模式下 backbone update 与 IPA 实现不同，不能只复用 monomer 权重

## 典型调用位置

- `AlphaFold.iteration` 中 Evoformer 输出之后
- OpenFold pretrained inference 最终结构恢复阶段

## 典型参数

- 具体参数来自 OpenFold model config 的 `structure_module`
- 长序列推理时可配合外层 `_offload_inference`
- 契约层目标调用：
  - `OneDecoder(style="OpenFoldStructureModule", ...)`

## 风险点

- `style="OpenFoldStructureModule"` 是 skill 契约归一名，不表示当前源码已经在 `OneDecoder` registry 中可直接实例化
- StructureModule 依赖 OpenFold 的 atom14/atom37 residue constants，不能直接喂任意 PDB 原子顺序
- 输出 `positions[-1]` 才是外层转 atom37 的最终 block 坐标
- 该模块不是 Protenix diffusion decoder，不能输出多 sample denoised atom coordinates
- 修改 `no_angles`、residue constants 或 aatype 编码会影响 torsion 和 atom frame 语义

## 源码锚点

- `./onescience/src/onescience/models/openfold/structure_module.py`
- `./onescience/src/onescience/models/openfold/model.py`
- `./onescience/src/onescience/utils/openfold/rigid_utils.py`
- `./onescience/src/onescience/utils/openfold/feats.py`
