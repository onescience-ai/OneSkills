# Model Card: LSM

## 基本信息

- 模型名：`LSM`
- 任务类型：`CFD / latent spectral multiscale operator`
- 当前状态：`stable`
- 主实现文件：`./onescience/src/onescience/models/cfd_benchmark/LSM.py`

## 模型定位

LSM 把 U-Net 的多尺度路径和 latent spectral block 结合起来，适合在规则网格或 GeoFNO 投影后的潜在网格上做多尺度全局建模。

补充说明：

- 结构上最接近“U-Net + spectral transformer hybrid”。
- 支持 structured 与 unstructured，两条路径都先统一到多尺度潜在网格主干。
- 若想比较纯 U-Net、纯 FNO 和混合型多尺度谱模型，LSM 是关键候选。

## 输入定义

- 输入 shape：`x -> (Batch, NumPoints, space_dim)`，`fx -> (Batch, NumPoints, fun_dim)`
- 输入变量组织：
  - `x`
    - 坐标或统一位置编码
  - `fx`
    - 点级场输入

## 输出定义

- 输出 shape：`(Batch, NumPoints, out_dim)`
- 输出变量组织：
  - 点级目标变量

## 主干结构

- `OneMlp`
  - 预处理
- 可选 `GeoSpectralConv2d`
  - 非结构化投影
- 4 级 U-Net 编码器/解码器
- 每个尺度插入 `OneTransformer(style="NeuralSpectralBlock*d")`
- `fc1 + fc2`

## 主要依赖组件

- `OneMlp`
- `OneFourier`
- `OneTransformer(style="NeuralSpectralBlock*d")`
- `unet_layer` 家族

## 主要 Shape 变化

- 预处理后：`(Batch, NumPoints, n_hidden)`
- reshape 后：`(Batch, n_hidden, *grid_shape)`
- 编码下采样时空间尺寸减小、通道数增大
- 解码恢复后再展平成点级输出

## 默认关键参数

- `num_token=4`
- `num_basis=12`
- `s1=96, s2=96`
- `task="steady"` 时默认走 `bn` 风格归一化

## 常见修改点

- 调整 `shapelist` 与 padding
- 依据任务修改 `num_token / num_basis`
- 对比实验时可直接与 `U_Net`、`F_FNO`、`MWT` 共用训练流

## 导入与实例化约束

- 新数据集接入，特别是 benchmark / 多模型对比案例，默认使用 `onescience.models.cfd_benchmark.LSM`。
- 推荐写法：`from onescience.models.cfd_benchmark import LSM`，再调用 `LSM.Model(args, device)`。
- 默认不要走 `from onescience.models.cfd_benchmark.model_factory import get_model`，除非明确复刻原 `CFD_Benchmark` runner。
- 模型参数应放在 YAML 配置文件中，训练脚本读取 YAML 后转成 `args` 对象传给 `LSM.Model(args, device)`。
- `onescience.models.pdenneval.lsm` 不存在，`LSM1d / LSM2d / LSM3d` 也不是当前 OneScience 中的 LSM 类名。
- 如果 agent 想按 PDEBench 风格选择 `FNO2d / UNet2d`，必须先停下来重新确认：`LSM` 仍然只能来自 `cfd_benchmark/LSM.py`，不能迁移到 `pdenneval` 包下。

## 新数据集 benchmark 接入提示

- 多模型对比时，`LSM` 默认使用 operator view：`x / fx / y`
- 规则网格数据需要给出 `shapelist`，并确认每个尺度下采样后仍能被 U-Net 主干处理
- 非结构数据需要先通过 Geo 投影进入潜在规则网格，第一轮规格必须说明 `s1 / s2`、投影方式和坐标归一化
- 如果新数据集目标是翼型点云回归，`LSM` 通常是 `adapter-required`，不能和 `Transolver` 共用同一个 PyG batch
- 如果投影分辨率、目标变量维度或 padding 规则不明确，先把 `LSM` 标记为需要补充探测信息

## 风险点

- 主干比纯 U-Net 和纯 FNO 都更重，显存和训练时间通常更高。
- 非结构化几何仍然依赖 GeoFNO 投影质量。
- 多尺度和谱块同时存在，改通道数时要同时检查 U-Net 和 spectral block 两边。

## 推荐检索顺序

1. 先看本模型卡
2. 再看 `U_Net (CFD_Benchmark)`
3. 再看 `OneTransformer` 和 `OneFourier`

## 组件契约入口

- `../contracts/onemlp.md`
- `../contracts/onefourier.md`
- `../contracts/onetransformer.md`

## 源码锚点

- `./onescience/src/onescience/models/cfd_benchmark/LSM.py`
- `./onescience/examples/cfd/CFD_Benchmark/exp/exp_steady.py`
