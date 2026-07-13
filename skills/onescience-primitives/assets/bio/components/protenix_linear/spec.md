# component_info

`protenix_linear` 是 Protenix 内部线性层与初始化策略组件族，统一入口为 `OneLinear`。

# purpose

为 Protenix input/pair 初始化、relative position projection、MSA projection、attention、Pairformer 和 diffusion 提供一致线性投影和初始化语义。

# input_schema

```text
x: [..., in_features]
```

# output_schema

```text
y: [..., out_features]
```

# parameters

- `in_features`
- `out_features`
- `bias=True`
- `precision=None`
- `initializer="default" | "relu" | "zeros"`
- `biasinit=0.0`

# key_dependencies

- `onelinear.py`
- `protenixlinear.py`

# usage_and_risks

`ProtenixLinearNoBias` 固定无 bias；`ProtenixBiasInitLinear` 会把 weight 置零并初始化 bias。初始化方式是模型行为的一部分，替换为普通 `nn.Linear` 可能改变稳定性。

# code_references

- `{onescience_path}/onescience/src/onescience/modules/linear/onelinear.py`
- `{onescience_path}/onescience/src/onescience/modules/linear/protenixlinear.py`
