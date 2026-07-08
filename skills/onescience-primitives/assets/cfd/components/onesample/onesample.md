# Contract: OneSample

## 基本信息

- 组件名：`OneSample`
- 所属模块族：`sample`
- 统一入口：`OneSample`
- 注册名：`style="OneSample"`

## 组件说明
OneSample 位于 sample 模块，是多尺度模型中改变 token、特征图或图节点分辨率的统一入口。

## 用途
- 做什么：执行上采样、下采样或图节点空间采样。
- 解决问题：统一管理天气模型 token 采样、Fuxi 特征图采样和图空间采样。
- 适用场景：Pangu/Fuxi/FengWu 多尺度结构、图层级池化或恢复。
- 不适用场景：自动插值任意数据格式或替代 decoder。

## 输入规格
输入由 style 决定；Pangu/Fuxi 多为 token 或特征图；SpatialGraphDownsample/Upsample 需要节点特征、坐标、采样索引或邻域信息。

## 输出规格
输出为采样后的 token、特征图或图节点特征，尺度变化规则由底层 style 决定。

## 参数
- `style`：注册表名称，常见取值包括 `PanguDownSample`, `PanguUpSample`, `SpatialGraphDownsample`, `FuxiDownSample`。
- `**kwargs`：透传给目标 采样 实现。
- 常见参数：通道数、采样比例、邻居半径 `r`、`max_num_neighbors`、pool 方法和模型族特定尺寸配置。

## 关键依赖
- _lazy.py
- pangudownsample.py
- panguupsample.py
- fuxidownsample.py
- fuxiupsample.py
- SpatialGraphDownsample.py
- SpatialGraphUpsample.py

## 使用注意与风险
- Pangu、Fuxi 和图采样处理对象不同，不能只按名字替换。
- 图采样需要坐标、邻接或采样 id。
- wrapper 不检查上采样与下采样是否成对。
- 错误尺度会导致后续 skip 或 residual 失败。

## 启动方式
Python API 启动，调用方按目标 style 传入底层实现参数：

``` sh
python -c "from onescience.modules.sample.onesample import OneSample; m=OneSample(style='PanguDownSample'); print(type(m).__name__)"
```

在模型 pipeline 中通常由上层模型构造函数实例化，不单独提供 CLI。

## 输入规格
按所选 style 的 forward 签名准备张量和辅助字段；wrapper 不做数据读取、字段映射或 shape 修正。

## 运行接口
- 构造接口：`OneSample(style, **kwargs)`。
- 调用接口：`module(*args, **kwargs)` 透传到底层 采样。
- 若源码实现了属性转发，可直接访问底层实例属性。

## 主要函数
- `forward`

## 执行资源
资源需求由底层实现决定；规则网格算子通常随空间分辨率增长，图/点云算子随节点边数量增长，训练建议使用 GPU。

## 操作限制
style 必须已注册；kwargs 与输入必须匹配底层实现；该 wrapper 不保证不同 style 的输入输出可互换。

## 规划决策

### 描述
在规划中把 OneSample 作为多尺度转换阶段，先明确被采样对象是 token、grid feature 还是 graph nodes。

### 使用时机
当模型需要通过统一入口切换或复用不同 采样 实现时使用。

### 输入
- 数据拓扑与空间维度。
- 上下游模块的 shape/字段契约。
- 目标 style 的参数需求。
- 资源预算与失败容忍度。

### 输出
- 选定 style。
- 构造参数。
- 运行时输入字段映射。
- 输出语义和后续连接策略。

### 执行步骤
1. 从任务数据形态筛选候选 style。
2. 回到目标 style 源码确认构造参数与 forward 参数。
3. 准备最小 batch 验证 shape。
4. 接入上游和下游模块。
5. 记录限制条件和 fallback。

### 约束
不跨语义混用 style；不把 wrapper 当作数据适配层；新增底层实现后必须注册。

### 下一阶段建议
为被选 style 增加端到端 smoke test，并补充示例配置。

### 回退策略
若 style 不支持当前输入，改用同 family 更匹配实现；若无可用 style，先实现专用适配层或回退到底层模块直接调用。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/modules/sample/onesample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/pangudownsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/panguupsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/fuxidownsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/SpatialGraphDownsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/SpatialGraphUpsample.py`
