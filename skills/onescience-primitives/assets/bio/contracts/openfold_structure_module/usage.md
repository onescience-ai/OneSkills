# launch

```sh
python -c "from onescience.models.openfold.structure_module import StructureModule; print(StructureModule.__name__)"
```

# input_schema

从 OpenFold Evoformer iteration 获取 `single` 和 `pair`，并提供同一 residue 轴上的 `aatype` 与 `mask`。输入 residue 编码需要匹配 OpenFold atom14/atom37 residue constants。

# runtime_interfaces

- `StructureModule.forward`: 从 single/pair 表征生成 atom14 坐标、frames 和 angles。
- `atom14_to_atom37`: 外层将 atom14 中间结构转换为 atom37。

# main_functions

- `forward`

# execution_resources

资源主要受 `N_res`、IPA 头数、block 数和 pair 表征尺寸影响。长序列通常需要配合 OpenFold 外层 trunk 的 chunk/offload 策略。

# operation_limits

`contract_only` 表示目标 style 不是已确认可运行的 `OneDecoder` registry 项。该模块依赖 OpenFold residue constants 和 atom order，不能直接喂任意 PDB 原子顺序；也不会输出 Protenix 那种多 sample denoised atom coordinates。
