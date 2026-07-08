# Contract: OneFourier

## 基本信息

- 组件名：`OneFourier`
- 所属模块族：`fourier`
- 统一入口：`OneFourier`
- 注册名：`style="OneFourier"`

## 组件说明
OneFourier 位于 fourier 模块，是神经算子中频域卷积、几何感知谱卷积和多小波变换的统一构造入口。它适合放在 FNO/U-NO/GFNO/Geo-FNO 类主干中作为全局混合层。

## 用途
- 做什么：在频域或小波域执行全局特征混合。
- 解决问题：用统一入口管理 1D/2D/3D 谱卷积和几何谱卷积。
- 适用场景：规则网格 PDE 代理、非结构点到规则潜网格投影、群等变谱卷积。
- 不适用场景：局部 CNN 替代、自动网格插值或任意点云大规模显式 DFT。

## 输入规格
常规 FNO 输入为 channel-first 网格张量；GeoSpectral 输入可为 `(Batch, Channels, N)` 加 `x_in/x_out/iphi/code`；MultiWavelet 输入由具体 wavelet kernel 定义。

## 输出规格
输出由底层 style 决定，通常保持 batch 和空间/点数量语义，改变通道数；GeoSpectral 可输出规则网格或指定 `x_out` 的非结构点。

## 参数
- `style`：注册表名称，常见取值包括 `FNOSpectralConv2d`, `GeoSpectralConv2d`, `GSpectralConv2d`, `MultiWaveletTransform2D`。
- `**kwargs`：透传给目标 Fourier/谱算子 实现。
- 常见参数：`in_channels`、`out_channels`、`modes1/2/3`、`s1/s2/s3`、group 等变配置或 wavelet 配置。
- 典型值：2D FNO 可用 `modes1=modes2=12`；Geo-FNO 需同时配置输出潜网格尺寸。

## 关键依赖
- _lazy.py
- fno_layers.py
- geo_spectral.py
- ffno_layers.py
- group_spectral.py
- MultiWaveletTransform.py

## 使用注意与风险
- `modes*` 必须小于对应空间频率容量。
- `GeoSpectralConv*d` 的 forward 与标准 FNO 不同，替换时需检查 `x_in/x_out/iphi`。
- 显式 DFT 的内存随点数和 modes 增长明显。
- Group spectral 需要等变通道布局，不能直接混入普通 FNO。

## 启动方式
Python API 启动，调用方按目标 style 传入底层实现参数：

``` sh
python -c "from onescience.modules.fourier.onefourier import OneFourier; m=OneFourier(style='FNOSpectralConv2d'); print(type(m).__name__)"
```

在模型 pipeline 中通常由上层模型构造函数实例化，不单独提供 CLI。

## 输入规格
按所选 style 的 forward 签名准备张量和辅助字段；wrapper 不做数据读取、字段映射或 shape 修正。

## 运行接口
- 构造接口：`OneFourier(style, **kwargs)`。
- 调用接口：`module(*args, **kwargs)` 透传到底层 Fourier/谱算子。
- 若源码实现了属性转发，可直接访问底层实例属性。

## 主要函数
- `forward`

## 执行资源
资源需求由底层实现决定；规则网格算子通常随空间分辨率增长，图/点云算子随节点边数量增长，训练建议使用 GPU。

## 操作限制
style 必须已注册；kwargs 与输入必须匹配底层实现；该 wrapper 不保证不同 style 的输入输出可互换。

## 规划决策

### 描述
在规划中把 OneFourier 视为神经算子的全局谱混合阶段：先判断规则网格还是非结构几何，再选择普通 FNO、Geo-FNO、GFNO 或 wavelet 分支。

### 使用时机
当模型需要通过统一入口切换或复用不同 Fourier/谱算子 实现时使用。

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

- `{onescience_path}/onescience/src/onescience/modules/fourier/onefourier.py`
- `{onescience_path}/onescience/src/onescience/modules/fourier/fno_layers.py`
- `{onescience_path}/onescience/src/onescience/modules/fourier/geo_spectral.py`
- `{onescience_path}/onescience/src/onescience/modules/fourier/ffno_layers.py`
- `{onescience_path}/onescience/src/onescience/modules/fourier/group_spectral.py`
