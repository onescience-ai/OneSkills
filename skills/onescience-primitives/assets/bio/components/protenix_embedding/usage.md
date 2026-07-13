# launch

```sh
python -c "from onescience.modules import OneEmbedding; m=OneEmbedding(style='ProtenixFourierEmbedding', c=256, seed=42); print(type(m).__name__)"
```

# input_schema

准备 Protenix feature dict，不要传普通 FASTA 或 OpenFold batch。输入 embedder 需要 atom 参考特征、atom-token 映射和 token 级 `restype/profile/deletion_mean`；template embedder 还需要 `z`；Fourier embedding 只需要 noise level tensor。

# runtime_interfaces

- `OneEmbedding(style="ProtenixInputFeatureEmbedder", ...)`: 构造 token 输入。
- `OneEmbedding(style="ProtenixTemplateEmbedder", ...)`: 构造 template pair update。
- `ProtenixFourierEmbedding(c, seed)`: 构造 diffusion noise embedding。

# main_functions

- `forward`

# execution_resources

输入 embedder 和 template embedder 会产生 token/pair 级张量，长复合物场景主要受 `N_token^2` pair 表征和 atom 局部窗口影响。

# operation_limits

只支持 Protenix/AF3 风格特征。template 分支不是独立 template search；缺少 atom reference 字段或 `atom_to_token_idx` 会直接破坏输入特征构造。
