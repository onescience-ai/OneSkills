# launch
Python API 启动，调用方按目标 style 传入底层实现参数：

``` sh
python -c "from onescience.modules.attention.oneattention import OneAttention; m=OneAttention(style='LinearAttention'); print(type(m).__name__)"
```

在模型 pipeline 中通常由上层模型构造函数实例化，不单独提供 CLI。

# input_schema
准备底层 style 需要的张量、mask、坐标或 shape 配置；若来自 datapipe，应在进入 attention 前完成 batch 拼接、窗口化或点云坐标归一化。

# runtime_interfaces
- 构造接口：`OneAttention(style, **kwargs)` 选择并实例化目标注意力。
- 调用接口：`module(*args, **kwargs)` 将所有运行时输入透传给底层实现。
- 属性访问：未在 wrapper 上找到的属性会转发到底层 attention 实例。

# main_functions
- `forward`

# execution_resources
依赖张量计算环境；全局注意力和显式物理注意力通常需要 GPU，显存随 token 数、窗口数、head 数或 DFT/attention 矩阵规模增长。

# operation_limits
不负责注册表外 style、mask 生成、网格 reshape、邻接构建或跨 style 参数兼容；常见失败模式是 style 未注册、kwargs 名称不匹配、输入维度与底层实现不一致。
