# launch
Python API 启动示例：

``` sh
python -c "import torch; from onescience.modules.fourier.geo_spectral import GeoSpectralConv2d; m=GeoSpectralConv2d(32,64,12,12,s1=64,s2=64); u=torch.randn(2,32,1024); x=torch.rand(2,1024,2); print(m(u,x_in=x).shape)"
```

# input_schema
准备 channel-first 特征 `u` 和归一化坐标 `x_in/x_out`；规则网格可省略坐标走 FFT；非结构点到点预测需同时提供 `x_out`。

# runtime_interfaces
- `IPHI.forward(x, code=None)`：将物理坐标映射到计算坐标。
- `GeoSpectralConv2d.forward(u, x_in=None, x_out=None, iphi=None, code=None)`：2D 几何谱卷积。
- `GeoSpectralConv3d.forward(u, x_in=None, x_out=None, iphi=None, code=None)`：3D 几何谱卷积。
- `fft2d/ifft2d/fft3d/ifft3d`：内部显式 Fourier 变换辅助接口。

# main_functions
- `forward`
- `fft2d`
- `ifft2d`
- `fft3d`
- `ifft3d`

# execution_resources
建议 GPU 运行；显存随 `Batch * Channels * Points * modes1 * modes2[*modes3]` 增长。规则网格 FFT 分支较省，非结构显式 DFT 分支更昂贵。

# operation_limits
仅覆盖源码实现的 2D/3D 谱卷积；IPHI 当前按 2D 坐标设计；不负责坐标归一化、点采样或边界条件处理。
