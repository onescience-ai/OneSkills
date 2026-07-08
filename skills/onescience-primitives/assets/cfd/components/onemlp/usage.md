# launch
Python API 启动，调用方按目标 style 传入底层实现参数：

``` sh
python -c "from onescience.modules.mlp.onemlp import OneMlp; m=OneMlp(style='StandardMLP'); print(type(m).__name__)"
```

在模型 pipeline 中通常由上层模型构造函数实例化，不单独提供 CLI。

# input_schema
按所选 style 的 forward 签名准备张量和辅助字段；wrapper 不做数据读取、字段映射或 shape 修正。

# runtime_interfaces
- 构造接口：`OneMlp(style, **kwargs)`。
- 调用接口：`module(*args, **kwargs)` 透传到底层 MLP。
- 若源码实现了属性转发，可直接访问底层实例属性。

# main_functions
- `forward`

# execution_resources
资源需求由底层实现决定；规则网格算子通常随空间分辨率增长，图/点云算子随节点边数量增长，训练建议使用 GPU。

# operation_limits
style 必须已注册；kwargs 与输入必须匹配底层实现；该 wrapper 不保证不同 style 的输入输出可互换。
