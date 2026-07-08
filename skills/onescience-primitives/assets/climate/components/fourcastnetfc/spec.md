# component_info
在最后一个特征维度上执行两层前馈映射，完成逐位置通道混合。

补充说明：

- 该组件通常位于 `FourCastNetFuser` 中的 AFNO 之后
- 它不关心前面的 batch 或空间维度
- 本质上是一个作用在最后一维上的 MLP

该组件的核心实现包括 `FourCastNetFC`，定位为全连接/投影模块，由上层 OneScience 模型或流水线通过 Python API 调用。

# purpose
对通道或 token 表示做线性投影、展开或重排，适用于模型头尾连接。

# input_schema
- 2D 输入：`(..., in_features)`
- 3D 输入：`(..., in_features)`

内部统一做法：

- 对最后一个特征维度执行 `Linear -> Act -> Dropout -> Linear -> Dropout`
- 保持前面的所有维度不变

# output_schema
- 2D 输出：`(..., out_features)`
- 3D 输出：`(..., out_features)`

明确约束：

- 该组件不依赖固定空间 shape
- 主要约束来自最后一维的特征维度匹配

# parameters
- `in_features`
  - 输入特征维度
- `hidden_features`
  - 隐层特征维度
- `out_features`
  - 输出特征维度
- `act_layer`
  - 激活函数类型
- `drop`
  - dropout 比例

# key_dependencies
- `fc` 模块族内的相邻组件

# usage_and_risks
- 该组件不是空间算子，不能直接把它当作 embedding 或 fuser 使用
- 主要检查点是最后一维是否与调用层一致

# code_references
- `{onescience_path}/onescience/src/onescience/modules/fc/fourcastnetfc.py`
- `{onescience_path}/onescience/src/onescience/modules/fc/onefc.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/fourcastnetfuser.py`
