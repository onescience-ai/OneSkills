# Contract: OneAttention

## 基本信息

- 组件名：`OneAttention`
- 所属模块族：`attention`
- 统一入口：`OneAttention`
- 注册名：`style="OneAttention"`

## 组件说明
OneAttention 位于 attention 模块，是统一注意力原语入口，面向 EarthAttention、Transolver 物理注意力、线性注意力、窗口注意力和 Protenix 注意力等多类实现提供一致的构造与 forward 分发能力。它本身不定义张量语义，只负责 style 校验、实例化和运行时透传。

## 用途
- 做什么：为不同注意力实现提供统一入口，减少上层模型对具体模块路径的直接依赖。
- 解决问题：让气象网格、CFD token、非结构化网格、pair 表征等注意力实现通过同一调用模式接入。
- 适用场景：Transformer block、Transolver block、GraphViT/Factformer/GNOT、Protenix pair 或 atom 注意力。
- 不适用场景：需要自动完成网格展平、窗口划分、mask 构造或邻接图构建的场景；这些应由上游 pipeline 或具体 style 完成。

## 输入规格
输入由 `style` 决定，常见分支如下：

规则网格注意力
  x: 2D/3D 网格或窗口 token
  mask/window metadata: 由 EarthAttention 或 WindowAttention 定义

CFD/物理注意力
  x/fx: (Batch, Points, Channels) 或结构化网格 token
  坐标/shape: `shapelist`、`slice_num` 等由具体 style 消费

Protenix 注意力
  token/pair/atom 表征: 维度和 mask 语义由 ProtenixAttention 系列定义

## 输出规格
输出直接来自底层 attention，一般保持 batch 与 token/空间组织不变，仅更新最后一维特征；若底层实现返回附加权重、bias 或 tuple，则 OneAttention 不做拆包或改名。

## 参数
- `style`：注册表名称，例如 `EarthAttention2D`、`Physics_Attention_Irregular_Mesh`、`LinearAttention`、`ProtenixAttentionPairBias`。
- `**kwargs`：完整透传给目标 attention。常见参数包括 `dim`、`heads`、`dim_head`、`dropout`、`slice_num`、`shapelist`、窗口尺寸和 pair bias 配置。
- 典型值：结构化 2D 网格优先 `EarthAttention2D` 或 `Physics_Attention_Structured_Mesh_2D`；非结构化点云优先 `Physics_Attention_Irregular_Mesh`；低复杂度长序列可评估 `LinearAttention`。

## 关键依赖
- _lazy.py
- earthattention2d.py
- earthattention3d.py
- physicsattention.py
- linearattention.py
- protenixattention.py

## 使用注意与风险
典型使用是由 Transformer 类组件在构造时创建并在 forward 中透传 token。风险点：

- wrapper 不检查 shape，错误的网格维度会在底层 attention 中暴露。
- EarthAttention2D 与 EarthAttention3D 不可仅通过参数替换互换。
- Protenix 的 `z`/pair bias 不是 CFD 窗口 mask。
- FactAttention 与物理注意力常依赖 `shapelist`，不能只根据 token 数推断。

## 启动方式
Python API 启动，调用方按目标 style 传入底层实现参数：

``` sh
python -c "from onescience.modules.attention.oneattention import OneAttention; m=OneAttention(style='LinearAttention'); print(type(m).__name__)"
```

在模型 pipeline 中通常由上层模型构造函数实例化，不单独提供 CLI。

## 输入规格
准备底层 style 需要的张量、mask、坐标或 shape 配置；若来自 datapipe，应在进入 attention 前完成 batch 拼接、窗口化或点云坐标归一化。

## 运行接口
- 构造接口：`OneAttention(style, **kwargs)` 选择并实例化目标注意力。
- 调用接口：`module(*args, **kwargs)` 将所有运行时输入透传给底层实现。
- 属性访问：未在 wrapper 上找到的属性会转发到底层 attention 实例。

## 主要函数
- `forward`

## 执行资源
依赖张量计算环境；全局注意力和显式物理注意力通常需要 GPU，显存随 token 数、窗口数、head 数或 DFT/attention 矩阵规模增长。

## 操作限制
不负责注册表外 style、mask 生成、网格 reshape、邻接构建或跨 style 参数兼容；常见失败模式是 style 未注册、kwargs 名称不匹配、输入维度与底层实现不一致。

## 规划决策

### 描述
在任务编排中将 OneAttention 视作注意力分发器：先判断数据拓扑和注意力语义，再选择具体 style，并把 shape/mask/坐标准备工作安排在它之前。

### 使用时机
当上层模块需要注意力机制但希望通过统一配置切换 Earth、Transolver、线性、窗口或 Protenix 注意力时使用。

### 输入
- 数据拓扑：规则网格、非结构化点云、token 序列或 pair/atom 表征。
- 空间维度：1D/2D/3D。
- 复杂度预算：token 数、head 数、显存上限。
- 所需偏置：窗口 mask、pair bias、物理切片或坐标信息。

### 输出
- 选定的 `style`。
- 对应构造参数字典。
- 上游需要准备的 mask、shapelist、坐标或 pair 表征清单。
- 与后续 transformer block 的 shape 约定。

### 执行步骤
1. 判断输入是规则网格、非结构点云还是结构化 token。
2. 根据维度和物理语义筛选 attention family。
3. 核对底层 style 的 forward 签名与上游张量。
4. 在模型构造时实例化 OneAttention。
5. 在首个 batch 上检查输出 shape 与 residual 分支是否一致。

### 约束
style 必须在注册表中；kwargs 必须属于目标实现；OneAttention 不改变输入输出结构，不应承担数据预处理职责。

### 下一阶段建议
若注意力用于新模型，下一阶段应补充最小 shape 测试，并记录 style 与 datapipe 输出字段之间的映射。

### 回退策略
style 不匹配时退回底层具体 attention 源码确认签名；显存不足时优先切换窗口/线性/物理切片注意力或减少 token、head、slice_num。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/modules/attention/oneattention.py`
- `{onescience_path}/onescience/src/onescience/modules/attention/earthattention2d.py`
- `{onescience_path}/onescience/src/onescience/modules/attention/earthattention3d.py`
- `{onescience_path}/onescience/src/onescience/modules/attention/physicsattention.py`
- `{onescience_path}/onescience/src/onescience/modules/attention/linearattention.py`
- `{onescience_path}/onescience/src/onescience/modules/attention/protenixattention.py`
