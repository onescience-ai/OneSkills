# component_info
OneFourier 位于 fourier 模块，是神经算子中频域卷积、几何感知谱卷积和多小波变换的统一构造入口。它适合放在 FNO/U-NO/GFNO/Geo-FNO 类主干中作为全局混合层。

# purpose
- 做什么：在频域或小波域执行全局特征混合。
- 解决问题：用统一入口管理 1D/2D/3D 谱卷积和几何谱卷积。
- 适用场景：规则网格 PDE 代理、非结构点到规则潜网格投影、群等变谱卷积。
- 不适用场景：局部 CNN 替代、自动网格插值或任意点云大规模显式 DFT。

# input_schema
常规 FNO 输入为 channel-first 网格张量；GeoSpectral 输入可为 `(Batch, Channels, N)` 加 `x_in/x_out/iphi/code`；MultiWavelet 输入由具体 wavelet kernel 定义。

# output_schema
输出由底层 style 决定，通常保持 batch 和空间/点数量语义，改变通道数；GeoSpectral 可输出规则网格或指定 `x_out` 的非结构点。

# parameters
- `style`：注册表名称，常见取值包括 `FNOSpectralConv2d`, `GeoSpectralConv2d`, `GSpectralConv2d`, `MultiWaveletTransform2D`。
- `**kwargs`：透传给目标 Fourier/谱算子 实现。
- 常见参数：`in_channels`、`out_channels`、`modes1/2/3`、`s1/s2/s3`、group 等变配置或 wavelet 配置。
- 典型值：2D FNO 可用 `modes1=modes2=12`；Geo-FNO 需同时配置输出潜网格尺寸。

# key_dependencies
- _lazy.py
- fno_layers.py
- geo_spectral.py
- ffno_layers.py
- group_spectral.py
- MultiWaveletTransform.py

# usage_and_risks
- `modes*` 必须小于对应空间频率容量。
- `GeoSpectralConv*d` 的 forward 与标准 FNO 不同，替换时需检查 `x_in/x_out/iphi`。
- 显式 DFT 的内存随点数和 modes 增长明显。
- Group spectral 需要等变通道布局，不能直接混入普通 FNO。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/fourier/onefourier.py`
- `{onescience_path}/onescience/src/onescience/modules/fourier/fno_layers.py`
- `{onescience_path}/onescience/src/onescience/modules/fourier/geo_spectral.py`
- `{onescience_path}/onescience/src/onescience/modules/fourier/ffno_layers.py`
- `{onescience_path}/onescience/src/onescience/modules/fourier/group_spectral.py`
