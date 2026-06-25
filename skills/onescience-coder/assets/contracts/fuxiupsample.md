# Contract: FuxiUpSample

## 基本信息

- **组件名称**: FuxiUpSample
- **模块族**: sample
- **统一入口**: OneSample
- **注册名称**: style="FuxiUpSample"

## 组件说明

对二维特征图做 2 倍上采样,并通过残差卷积块细化特征。

补充说明:

- 该组件处理的是二维特征图
- 不是 token 序列
- 通常位于 `FuxiTransformer` 的末尾

该组件的核心实现包括 `FuxiUpSample`,定位为采样模块,由上层 OneScience 模型或流水线通过 Python API 调用。

## 用途

执行上采样或下采样,改变特征图/特征体的空间尺度或通道维度,适用于多尺度主干网络。

## 输入规格

- 2D 输入: `(Batch, in_chans, Height, Width)`
- 3D 输入: `not_applicable`

内部统一做法:

- 先用转置卷积做 2 倍上采样
- 再通过若干残差卷积块细化特征
- 最终通过残差连接输出

## 输出规格

- 2D 输出: `(Batch, out_chans, OutHeight, OutWidth)`
- 3D 输出: `not_applicable`

其中:

- `OutHeight = Height * 2`
- `OutWidth = Width * 2`

## 参数

- `in_chans`
  - 输入特征通道数
- `out_chans`
  - 输出特征通道数
- `num_groups`
  - `GroupNorm` 分组数
- `num_residuals`
  - 残差卷积块数量

## 关键依赖

- `sample` 模块族内的相邻组件

## 使用注意与风险

- 该组件不处理 token 序列
- 输入通道数通常来自 skip 拼接后的 `2 * embed_dim`
- `num_groups` 需要与 `out_chans` 匹配

## 启动方式

主要通过 Python API 在模型配置或上层模块中实例化,不是独立 CLI 入口。下面的命令会从源码模块导入组件并打印完整构造签名,便于确认全部 API 参数:

```sh
python -c "from onescience.modules.sample.fuxiupsample import FuxiUpSample; import inspect; print(inspect.signature(FuxiUpSample))"
```

在真实任务中应由对应模型配置传入尺寸、通道数和隐空间维度等参数。

## 输入规格

- 2D 输入: `(Batch, in_chans, Height, Width)`
- 3D 输入: `not_applicable`

内部统一做法:

- 先用转置卷积做 2 倍上采样
- 再通过若干残差卷积块细化特征
- 最终通过残差连接输出

默认参数信息:

- `FuxiUpSample` 构造默认参数: `in_chans=1536 * 2`, `out_chans=1536`, `num_groups=32`, `num_residuals=2`

## 运行接口

- `FuxiUpSample`: 实例化后通过 `forward` 等运行时接口参与流水线。

## 主要函数

- `forward`

## 执行资源

- 运行设备由上层任务决定,训练和高分辨率推理通常建议使用 GPU。
- 图构建、邻居搜索或大分辨率气象场处理会占用较多内存,批量大小需随网格规模调整。
- 需要保证依赖库和 OneScience 模块路径可用,并与模型配置中的精度、设备和维度设置一致。

## 操作限制

- 不负责完整数据预处理、变量标准化、训练循环或损失函数编排。
- 仅在输入形状、变量顺序、图结构和上下游组件契约一致时可稳定工作。
- 源码中未声明的 CLI 参数、自动下载或外部数据读取能力不应假定存在。

## 规划决策

### 描述

FuxiUpSample 是 OneScience 中面向气象/地球系统建模的采样模块,用于在模型流水线中完成特征变换、尺度组织或结果重建。

```text
气象场或 token 特征
  -> 参数化特征变换
  -> 尺度/通道/分支组织
  -> 上层预测模型继续融合或输出
```

### 使用时机

- 任务需要 `采样模块` 能力,且组件输入输出契约与当前模型阶段匹配。
- 组件所属模型族或图/生成网络语义与任务目标一致。

### 输入

- 上游模型阶段提供的张量、图结构、条件特征或噪声特征。
- 与源码构造参数一致的通道数、分辨率、patch/window 尺寸、隐层维度和特征语义。

### 输出

- 可直接交给下一阶段的中间特征、图对象、节点/边表示或预测场。
- 输出结构应按 `spec.md` 的 `output_schema` 和 `code_references` 进行校验。

### 执行步骤

1. 确认组件所属模型族、模块族和上游/下游阶段。
2. 根据源码构造参数准备尺寸、通道、图特征维度和可选超参数。
3. 按 `usage.md` 的运行接口实例化组件,并传入契约化输入。
4. 检查输出形状、数据类型、设备和变量顺序是否满足下一阶段要求。
5. 在完整模型中通过单步前向或小批量样例验证集成效果。

### 约束

- 不跨越组件职责边界承担数据下载、全局训练调度或模型族外的语义转换。
- 不在未确认形状、图结构或变量顺序时直接替换已有模块。
- 规划中涉及代码位置时只以 `spec.md` 的 `code_references` 为准。

### 下一阶段建议

- 若组件用于新流水线,下一阶段应补齐上游输入准备和下游形状断言。
- 若组件替换已有模块,下一阶段应做等价输入样例对比和端到端 smoke test。

### 回退策略

- 当输入维度或依赖不匹配时,退回到同模型族的统一入口组件或相邻基础组件。
- 当源码缺少独立运行入口时,优先在上层模型配置中集成验证,而不是为该组件臆造 CLI。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/modules/sample/fuxiupsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/onesample.py`
- `{onescience_path}/onescience/src/onescience/modules/transformer/fuxitransformer.py`
