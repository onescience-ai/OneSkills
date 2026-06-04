# Contract: OneLinear

## 基本信息

- 组件名：`OneLinear`
- 所属模块族：`linear`
- 统一入口：`direct_import`
- 注册名：`style="<LinearStyle>"`

## 组件职责

为 linear 类组件提供统一注册入口，目前主要服务 Protenix 的线性层变体。

补充说明：

- 调用层通过 `style` 选择具体 linear 实现
- wrapper 本身不改变输入输出 shape
- 真实初始化策略、bias 行为和 precision 行为来自具体 linear 实现

## 支持输入

- 2D 输入：`depends_on_style`
- 3D 输入：`depends_on_style`
- 任意前缀维度：通常支持，最后一维应等于 `in_features`

内部统一做法：

- 检查 `style` 是否在 `_LINEAR_REGISTRY`
- 实例化对应 linear 类
- forward 时把 `*args, **kwargs` 透传给具体实现

## 构造参数

- `style`
  - 具体 linear 实现的注册名
- `**kwargs`
  - 透传给具体实现，常见为 `in_features`, `out_features`, `initializer`, `precision`

## 输出约定

- 输出最后一维为 `out_features`
- 其它前缀维度保持不变

如果有明确边界条件，也写在这里：

- `style` 必须已在 `linear/onelinear.py` 注册
- Protenix 初始化风格目前支持 `default`, `relu`, `zeros`

## 典型调用位置

- Protenix `s_init` 和 `z_init`
- Protenix token bond pair feature
- Protenix recycling residual projection
- Protenix 模块内部的无 bias 投影

## 典型参数

- Protenix 无 bias 线性层
  - `style="ProtenixLinearNoBias"`
  - `in_features=<dim_in>`
  - `out_features=<dim_out>`
- Protenix bias 初始化输出层
  - `style="ProtenixBiasInitLinear"`
  - `biasinit=<float>`

## 风险点

- 不要把 `OneLinear` 与已有 `OneFC` 混用；`OneLinear` 当前服务 Protenix 风格线性层，`OneFC` 是 weather 等模型中的 fc wrapper
- 若使用 `precision=torch.float32`，内部会关闭 autocast 做线性计算，再转回输入 dtype
- 新增 linear 风格后必须更新 `_LINEAR_REGISTRY`

## 源码锚点

- `{onescience_path}/onescience/src/onescience/modules/linear/onelinear.py`
- `{onescience_path}/onescience/src/onescience/modules/linear/protenixlinear.py`
