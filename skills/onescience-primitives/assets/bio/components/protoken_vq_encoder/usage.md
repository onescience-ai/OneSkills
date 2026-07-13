# launch

Python API 方式调用，通常在 ProToken inference/训练脚本中实例化：

```sh
python -c "from onescience.flax_models.protoken.model.encoder import VQ_Encoder, Feature_Initializer; print(VQ_Encoder.__name__, Feature_Initializer.__name__)"
```

# input_schema

准备 residue mask、aatype、residue_index、template atom positions/masks、pseudo beta、torsion angles 和 decoy affine。字段需与 ProToken 预处理输出一致。

# runtime_interfaces

- `Feature_Initializer.__call__`: 构造初始 single/pair 表征。
- `VQ_Encoder.__call__`: 执行 Evoformer/Transformer/StructureModule 更新。
- `MaskGITInverseFoldingModule.__call__`: 逆折叠与评分相关前向。

# main_functions

- `__call__`

# execution_resources

需要较高显存处理 residue pair 表征；资源随 residue 长度平方增长。

# operation_limits

缺少 template、torsion 或 affine 输入会影响结构表征质量。该模块不产生最终 codebook index，需接 bottleneck。
