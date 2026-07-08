# Contract: OneHead

## 基本信息

- 组件名：`OneHead`
- 所属模块族：`head`
- 统一入口：`OneHead`
- 注册名：`style="OneHead"`

## 组件说明
OneHead 位于 head 模块，是最终输出层或任务头的轻量统一入口。对于 CFD 最常见的是 UNetHead1D/2D/3D，用于把已恢复的特征场映射到目标物理量通道。

## 用途
- 做什么：将主干/decoder 输出投影为任务目标通道或目标属性。
- 解决问题：统一管理不同任务头的构造。
- 适用场景：U-Net 输出场投影、材料能量/力/磁矩预测、生物 MSA mask 预测。
- 不适用场景：恢复空间尺度、构建图拓扑或替代 decoder。

## 输入规格
输入由 style 决定；UNetHead*d 通常接收 `(Batch, Channels, ...Spatial)` 特征图，材料 head 接收模型定义的结构表征。

## 输出规格
UNetHead*d 通常保持空间维度并改变通道数；其它 head 返回任务特定标量、向量或 logits。

## 参数
- `style`：注册表名称，常见取值包括 `UNetHead2D`, `UNetHead3D`, `MaskedMSAHead`, `EnergyHead`。
- `**kwargs`：透传给目标 预测头 实现。
- 常见参数：`in_channels`、`out_channels`、卷积核、激活或任务头隐藏维度。
- CFD 中 `out_channels` 应等于目标物理变量通道数。

## 关键依赖
- _lazy.py
- unet_head.py
- maskedmsahead.py
- matris_head.py

## 使用注意与风险
- head 不能修复 decoder 已经丢失的空间分辨率。
- `out_channels` 与 datapipe label 通道顺序必须一致。
- MaskedMSAHead 与 CFD 场预测语义不同，不应误用。
- style 未注册会实例化失败。

## 启动方式
Python API 启动，调用方按目标 style 传入底层实现参数：

``` sh
python -c "from onescience.modules.head.onehead import OneHead; m=OneHead(style='UNetHead2D'); print(type(m).__name__)"
```

在模型 pipeline 中通常由上层模型构造函数实例化，不单独提供 CLI。

## 输入规格
按所选 style 的 forward 签名准备张量和辅助字段；wrapper 不做数据读取、字段映射或 shape 修正。

## 运行接口
- 构造接口：`OneHead(style, **kwargs)`。
- 调用接口：`module(*args, **kwargs)` 透传到底层 预测头。
- 若源码实现了属性转发，可直接访问底层实例属性。

## 主要函数
- `forward`

## 执行资源
资源需求由底层实现决定；规则网格算子通常随空间分辨率增长，图/点云算子随节点边数量增长，训练建议使用 GPU。

## 操作限制
style 必须已注册；kwargs 与输入必须匹配底层实现；该 wrapper 不保证不同 style 的输入输出可互换。

## 规划决策

### 描述
在规划中把 OneHead 放在模型末端，仅负责从已对齐的隐特征映射到监督目标。

### 使用时机
当模型需要通过统一入口切换或复用不同 预测头 实现时使用。

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

- `{onescience_path}/onescience/src/onescience/modules/head/onehead.py`
- `{onescience_path}/onescience/src/onescience/modules/head/unet_head.py`
