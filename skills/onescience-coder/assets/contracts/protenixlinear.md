# Contract: ProtenixLinear

## 基本信息

- 组件名：`ProtenixLinear / ProtenixLinearNoBias / ProtenixBiasInitLinear`
- 所属模块族：`linear`
- 统一入口：`OneLinear`
- 注册名：`style="ProtenixLinear"`, `style="ProtenixLinearNoBias"`, `style="ProtenixBiasInitLinear"`

## 组件职责

ProtenixLinear family 提供 Protenix 模型内部使用的线性层和初始化策略，覆盖默认截断正态、ReLU 缩放、零初始化和 bias 初始化等场景。

补充说明：

- `ProtenixLinear` 继承 `nn.Linear`
- `ProtenixLinearNoBias` 固定 `bias=False`
- `ProtenixBiasInitLinear` 会把 weight 置零，并按 `biasinit` 初始化 bias

## 支持输入

- 2D 输入：`[..., in_features]`
- 3D 输入：`[..., in_features]`
- 任意前缀维度：支持，最后一维必须是 `in_features`

内部统一做法：

- 初始化阶段按 `initializer` 处理权重
- forward 阶段若传入 `precision`，内部关闭 autocast 并用指定 dtype 做 `F.linear`
- 否则直接使用普通 `F.linear`

## 构造参数

- `in_features`
- `out_features`
- `bias=True`
- `precision=None`
- `initializer="default"`
  - `default`
  - `relu`
  - `zeros`
- `biasinit=0.0`
  - 仅 `ProtenixBiasInitLinear` 使用

## 输出约定

- 输出 shape：`[..., out_features]`
- 若设置 `precision`，输出会转回输入 dtype

如果有明确边界条件，也写在这里：

- 非法 `initializer` 会抛 `ValueError`
- `ProtenixLinearNoBias` 不接受 bias 输出语义

## 典型调用位置

- Protenix input / pair 初始化
- Protenix relative position projection
- Protenix MSA projection
- Protenix Pairformer、diffusion、attention 内部投影

## 典型参数

- pair 初始化：
  - `style="ProtenixLinearNoBias"`
  - `in_features=c_s`
  - `out_features=c_z`
- 零初始化 residual：
  - `initializer="zeros"`
- ReLU 后投影：
  - `initializer="relu"`
- float32 精度投影：
  - `precision=torch.float32`

## 风险点

- 初始化方式是模型行为的一部分，替换为普通 `nn.Linear` 可能改变训练稳定性
- `precision` 路线涉及 autocast 行为，混合精度训练时不要随意删
- OneScience 中 `OneFC` 与 `OneLinear` 不是同一入口

## 源码锚点

- `./onescience/src/onescience/modules/linear/onelinear.py`
- `./onescience/src/onescience/modules/linear/protenixlinear.py`
