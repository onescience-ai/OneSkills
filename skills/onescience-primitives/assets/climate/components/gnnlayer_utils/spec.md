# component_info
`gnnlayer_utils` 属于 `utils` 模块族，核心实现类/函数包括 模块级工具函数。它的定位是图构建与工具模块，由上层 OneScience 模型或流水线通过 Python API 调用。

# purpose
提供图构建、邻接关系和特征加工工具，适用于 GraphCast 图神经网络流水线。

# input_schema
- 图节点特征：`(N_nodes, feature_dim)`
- 图边特征：`(N_edges, feature_dim)`
- 图结构：DGL 图或等价的源/目标索引关系。

# output_schema
- 输出为变换后的张量特征或预测场，空间尺度、token 数和通道数由构造参数及上游模型配置共同决定。

# parameters
- 源码未声明显式构造参数，通常作为工具函数或轻量封装按需调用。

# key_dependencies
- `graph`

# usage_and_risks
- 输入张量维度必须与构造参数中的通道数、网格分辨率、patch 大小或图特征维度一致。
- 该组件通常依赖上层模型完成数据标准化、变量排序和设备迁移，单独调用时需显式准备。
- 图结构、节点顺序和边特征语义必须在 encoder、processor、decoder 阶段保持一致。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/utils/gnnlayer_utils.py`
