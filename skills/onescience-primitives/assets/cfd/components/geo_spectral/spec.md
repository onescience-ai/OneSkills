# component_info
GeoSpectral 位于 fourier 模块，是 Geo-FNO 风格的几何感知谱卷积实现，包含 2D/3D 谱卷积层和可选 IPHI 坐标变换网络。它直接实现业务算子，不是注册 wrapper。

# purpose
- 做什么：在非结构点、变形几何或规则网格上执行谱卷积。
- 解决问题：标准 FFT 难以直接处理不规则采样点，GeoSpectral 通过显式 DFT 将点坐标映射到谱域。
- 适用场景：2D/3D 不规则网格 CFD、Geo-FNO、点到规则潜网格或点到点谱映射。
- 不适用场景：超大点数的全量显式 DFT、缺少坐标的非结构数据、需要局部边消息的图网络。

# input_schema
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

# output_schema
当 `x_out is None` 时输出规则网格 `(Batch, C_out, s1, s2[, s3])`；当提供 `x_out` 时输出非结构点特征 `(Batch, C_out, M)`；IPHI 输出变换后的坐标 `(Batch, N, 2)`。

# parameters
- GeoSpectralConv2d：`in_channels`、`out_channels`、`modes1`、`modes2`、`s1=32`、`s2=32`。
- GeoSpectralConv3d：`in_channels`、`out_channels`、`modes1`、`modes2`、`modes3`、`s1/s2/s3=32`。
- IPHI：`width=32`，控制 Fourier feature 与 MLP 隐宽。
- 典型值：2D CFD 可从 `modes1=modes2=12`、`s1=s2=64/96` 试起，按分辨率和显存调整。

# key_dependencies
- onefourier.py
- torch.fft
- numpy

# usage_and_risks
- 显式 DFT 的内存约为点数乘以 modes 网格，点数过大时会显存爆炸。
- 坐标应归一化到稳定范围，`iphi` 的输出会影响相位计算。
- 2D IPHI 不能直接用于 3D 坐标。
- `modes*` 大于可表达频率或与 `s*` 不匹配会导致无效频域截断。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/fourier/geo_spectral.py`
