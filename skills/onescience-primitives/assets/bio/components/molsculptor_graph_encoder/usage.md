# launch

Python API 方式调用，通常在 MolSculptor 推理或训练管线中实例化：

```sh
python -c "from onescience.flax_models.MolSculptor.net.encoder import Encoder; print(Encoder.__name__)"
```

# input_schema

使用分子工具把 SMILES/SDF 转成 atom_features 和 bond_features 字典；字段类别编号必须与配置词表一致，mask 需要覆盖真实原子和 prefix 原子。

# runtime_interfaces

- `create_raw_feature`: 构造 atom/bond one-hot 原始特征并处理 prefix padding。
- `__call__`: 调用图编码主干并返回 prefix latent。

# main_functions

- `create_raw_feature`
- `__call__`

# execution_resources

资源开销取决于 batch size、最大原子数和 bond 矩阵大小；大分子全连接 bond feature 会明显增加内存。

# operation_limits

不负责蛋白口袋条件，也不做 SMILES 解码。原子类别、bond 类别或 mask 错误会导致 latent 表征无效。
