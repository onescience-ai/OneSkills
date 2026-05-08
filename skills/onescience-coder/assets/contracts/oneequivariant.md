# Contract: OneEquivariant

## 基本信息

- 组件名：`OneEquivariant`
- 所属模块族：`equivariant`
- 统一入口：`direct_import`
- 注册名：`style="<EquivariantStyle>"`

## 组件职责

为群等变卷积层提供统一注册入口。

补充说明：

- 调用层通过 `style` 选择具体等变实现
- 当前 CFD 神经算子中主要用于 `GFNO`
- 常与 `OneFourier(style="GSpectralConv*d")` 和 `OneMlp(style="GroupEquivariantMLP*d")` 配合使用

## 支持输入

- 2D 输入：`(B, C, H, W)` 或底层 group conv 约定的等变通道布局
- 3D 输入：`(B, C, D, H, W)` 或底层 group conv 约定的等变通道布局

内部统一做法：

- 先检查 `style` 是否已注册
- 再将构造参数透传给具体等变层
- forward 时不改变 batch 语义，主要在通道和群维度上执行变换

## 构造参数

- `style`
  - 具体等变层注册名，例如 `GroupEquivariantConv2d`
- `in_channels`
  - 输入通道数
- `out_channels`
  - 输出通道数
- `kernel_size`
  - 卷积核大小
- `reflection`
  - 是否启用反射群扩展
- `first_layer`
  - 是否作为等变 stem 的第一层使用

## 输出约定

- 2D 输出：通常保持空间分辨率，改变通道或群通道布局
- 3D 输出：通常保持空间分辨率，改变通道或群通道布局

额外约束：

- 与普通卷积相比，等变层内部可能展开 group 维度，后续层必须使用兼容的 `GSpectralConv*d` 或 `GroupEquivariantMLP*d`
- `reflection` 设置需要在同一 GFNO stem 中保持一致

## 典型调用位置

- `GFNO` 的 lifting layer
- `GFNO` 的 residual 1x1 group convolution

## 典型参数

- GFNO 2D stem
  - `style="GroupEquivariantConv2d"`
  - `in_channels=args.n_hidden`
  - `out_channels=width`
  - `kernel_size=1`
  - `reflection=False`

## 风险点

- `OneEquivariant` 不适合直接替代普通 CNN 卷积；它要求后续层理解 group 通道布局
- structured 与 unstructured 分支的输入形态不同，只有进入规则网格 stem 后才适合使用 group equivariant conv
- 如果只想做普通 FNO 对比，不应默认打开 GFNO 的等变组件

## 源码锚点

- `./onescience/src/onescience/modules/equivariant/oneequivariant.py`
- `./onescience/src/onescience/modules/equivariant/group_conv.py`
- `./onescience/src/onescience/models/cfd_benchmark/GFNO.py`
