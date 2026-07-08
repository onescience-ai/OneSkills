# Contract: GeoSpectral

## 基本信息

- 组件名：`GeoSpectral`
- 所属模块族：`fourier`
- 统一入口：`not_applicable`
- 注册名：`style="GeoSpectral"`

## 组件说明
GeoSpectral 位于 fourier 模块，是 Geo-FNO 风格的几何感知谱卷积实现，包含 2D/3D 谱卷积层和可选 IPHI 坐标变换网络。它直接实现业务算子，不是注册 wrapper。

## 用途
- 做什么：在非结构点、变形几何或规则网格上执行谱卷积。
- 解决问题：标准 FFT 难以直接处理不规则采样点，GeoSpectral 通过显式 DFT 将点坐标映射到谱域。
- 适用场景：2D/3D 不规则网格 CFD、Geo-FNO、点到规则潜网格或点到点谱映射。
- 不适用场景：超大点数的全量显式 DFT、缺少坐标的非结构数据、需要局部边消息的图网络。

## 输入规格
GeoSpectralConv2d
  u: (Batch, C_in, N) 或 (Batch, C_in, H, W)
  x_in: 可选 (Batch, N, 2)
  x_out: 可选 (Batch, M, 2)
  iphi: 可选坐标映射模块
  code: 可选条件编码

GeoSpectralConv3d
  u: (Batch, C_in, N) 或规则 3D 网格
  x_in/x_out: (Batch, N/M, 3)

IPHI
  x: (Batch, N, 2)
  code: 可选条件向量，源码中按 42 维线性层处理

## 输出规格
当 `x_out is None` 时输出规则网格 `(Batch, C_out, s1, s2[, s3])`；当提供 `x_out` 时输出非结构点特征 `(Batch, C_out, M)`；IPHI 输出变换后的坐标 `(Batch, N, 2)`。

## 参数
- GeoSpectralConv2d：`in_channels`、`out_channels`、`modes1`、`modes2`、`s1=32`、`s2=32`。
- GeoSpectralConv3d：`in_channels`、`out_channels`、`modes1`、`modes2`、`modes3`、`s1/s2/s3=32`。
- IPHI：`width=32`，控制 Fourier feature 与 MLP 隐宽。
- 典型值：2D CFD 可从 `modes1=modes2=12`、`s1=s2=64/96` 试起，按分辨率和显存调整。

## 关键依赖
- onefourier.py
- torch.fft
- numpy

## 使用注意与风险
- 显式 DFT 的内存约为点数乘以 modes 网格，点数过大时会显存爆炸。
- 坐标应归一化到稳定范围，`iphi` 的输出会影响相位计算。
- 2D IPHI 不能直接用于 3D 坐标。
- `modes*` 大于可表达频率或与 `s*` 不匹配会导致无效频域截断。

## 启动方式
Python API 启动示例：

``` sh
python -c "import torch; from onescience.modules.fourier.geo_spectral import GeoSpectralConv2d; m=GeoSpectralConv2d(32,64,12,12,s1=64,s2=64); u=torch.randn(2,32,1024); x=torch.rand(2,1024,2); print(m(u,x_in=x).shape)"
```

## 输入规格
准备 channel-first 特征 `u` 和归一化坐标 `x_in/x_out`；规则网格可省略坐标走 FFT；非结构点到点预测需同时提供 `x_out`。

## 运行接口
- `IPHI.forward(x, code=None)`：将物理坐标映射到计算坐标。
- `GeoSpectralConv2d.forward(u, x_in=None, x_out=None, iphi=None, code=None)`：2D 几何谱卷积。
- `GeoSpectralConv3d.forward(u, x_in=None, x_out=None, iphi=None, code=None)`：3D 几何谱卷积。
- `fft2d/ifft2d/fft3d/ifft3d`：内部显式 Fourier 变换辅助接口。

## 主要函数
- `forward`
- `fft2d`
- `ifft2d`
- `fft3d`
- `ifft3d`

## 执行资源
建议 GPU 运行；显存随 `Batch * Channels * Points * modes1 * modes2[*modes3]` 增长。规则网格 FFT 分支较省，非结构显式 DFT 分支更昂贵。

## 操作限制
仅覆盖源码实现的 2D/3D 谱卷积；IPHI 当前按 2D 坐标设计；不负责坐标归一化、点采样或边界条件处理。

## 规划决策

### 描述
GeoSpectral 是非结构几何进入谱域神经算子的桥接层，规划时必须同时考虑坐标质量、modes 截断和输出采样点。

### 使用时机
当 CFD 数据在不规则点、变形网格或需要点到规则潜网格映射时使用；规则网格标准 FNO 可优先使用普通 SpectralConv。

### 输入
- 输入特征通道与点数。
- `x_in/x_out` 坐标维度和归一化范围。
- 目标输出是规则网格还是非结构点。
- modes 与显存预算。
- 是否需要 IPHI 条件映射。

### 输出
- 2D 或 3D GeoSpectralConv 配置。
- `s*` 或 `x_out` 输出策略。
- 可选 IPHI 配置。
- 显存风险评估。

### 执行步骤
1. 判断是否确实需要非结构谱卷积。
2. 归一化坐标并确认维度。
3. 选择 modes 与输出网格尺寸。
4. 先用小 batch 运行 forward 检查 shape 和显存。
5. 再接入 FNO 主干或 decoder。

### 约束
坐标维度必须匹配 2D/3D 实现；modes 不能脱离输出分辨率设置；显式 DFT 不适合无限增大点数。

### 下一阶段建议
为目标数据集做 modes-sweep 和显存 profiling，必要时引入分块点集或改用图/局部算子。

### 回退策略
显存不足时降低 modes、降低点数、输出到规则潜网格，或回退到标准 FNO/图神经网络；坐标映射不稳定时暂时移除 IPHI。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/modules/fourier/geo_spectral.py`
