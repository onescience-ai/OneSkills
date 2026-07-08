# component_info
OneSample 位于 sample 模块，是多尺度模型中改变 token、特征图或图节点分辨率的统一入口。

# purpose
- 做什么：执行上采样、下采样或图节点空间采样。
- 解决问题：统一管理天气模型 token 采样、Fuxi 特征图采样和图空间采样。
- 适用场景：Pangu/Fuxi/FengWu 多尺度结构、图层级池化或恢复。
- 不适用场景：自动插值任意数据格式或替代 decoder。

# input_schema
输入由 style 决定；Pangu/Fuxi 多为 token 或特征图；SpatialGraphDownsample/Upsample 需要节点特征、坐标、采样索引或邻域信息。

# output_schema
输出为采样后的 token、特征图或图节点特征，尺度变化规则由底层 style 决定。

# parameters
- `style`：注册表名称，常见取值包括 `PanguDownSample`, `PanguUpSample`, `SpatialGraphDownsample`, `FuxiDownSample`。
- `**kwargs`：透传给目标 采样 实现。
- 常见参数：通道数、采样比例、邻居半径 `r`、`max_num_neighbors`、pool 方法和模型族特定尺寸配置。

# key_dependencies
- _lazy.py
- pangudownsample.py
- panguupsample.py
- fuxidownsample.py
- fuxiupsample.py
- SpatialGraphDownsample.py
- SpatialGraphUpsample.py

# usage_and_risks
- Pangu、Fuxi 和图采样处理对象不同，不能只按名字替换。
- 图采样需要坐标、邻接或采样 id。
- wrapper 不检查上采样与下采样是否成对。
- 错误尺度会导致后续 skip 或 residual 失败。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/sample/onesample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/pangudownsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/panguupsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/fuxidownsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/SpatialGraphDownsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/SpatialGraphUpsample.py`
