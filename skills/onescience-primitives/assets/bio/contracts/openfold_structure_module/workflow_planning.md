# description

该卡用于 OpenFold 结构恢复阶段的组件规划，判断是否应使用 StructureModule、调整 IPA/angle 参数或转向其他 decoder。

# when_to_use

- 已有 OpenFold Evoformer 输出，需要生成 atom coordinates。
- 需要修改 AF2-style IPA、backbone update 或 torsion angle 输出。
- 需要排查 atom14/atom37 坐标恢复问题。

# inputs

- `single`、`pair`、`aatype`、`mask`。
- OpenFold model config 中的 `structure_module` 参数。
- monomer/multimer 模式。

# outputs

- StructureModule 调用策略。
- 输出字段解释：positions、frames、angles、final_atom_positions。
- 风险与 shape 检查清单。

# procedure

1. 确认输入来自 OpenFold Evoformer。
2. 校验 `N_res`、`aatype` 和 mask 对齐。
3. 按 config 构造 StructureModule。
4. 使用最终 block 的 atom14 坐标并由外层转 atom37。

# constraints

- 不混用 Protenix diffusion decoder。
- 不忽略 monomer/multimer 分支差异。
- 不改变 `no_angles` 或 residue constants 而不同步检查 torsion 语义。

# next_phase_recommendation

若输入 trunk 还未生成，先读取 `openfold_evoformer`；若需要多样本 diffusion 结构生成，切换 Protenix 或 AF3 JAX diffusion 组件。

# fallback

若 atom14/atom37 转换失败，回查 `aatype` 编码、residue constants 和 mask；若 `OneDecoder` 不可用，沿用 OpenFold 原生 `AlphaFold.iteration`。
