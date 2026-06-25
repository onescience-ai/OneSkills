# Contract: PanguUpSample

## 基本信息

- **组件名称**: PanguUpSample
- **模块族**: sample
- **统一入口**: OneSample
- **注册名称**: style="PanguUpSample"

## 组件说明

对二维或三维 token 网格做统一上采样，将低分辨率 token 恢复到更高分辨率的空间网格中。

这是 Pangu 系列多尺度解码阶段的统一 token 上采样组件。

该组件的核心实现包括 `PanguUpSample`，定位为采样模块，由上层 OneScience 模型或流水线通过 Python API 调用。

## 用途

执行上采样或下采样，改变特征图/特征体的空间尺度或通道维度，适用于多尺度主干网络。

## 输入规格

- 2D 输入：`(Batch, Height * Width, in_dim)`
- 3D 输入：`(Batch, PressureLevels * Height * Width, in_dim)`

内部统一做法：

- 对 2D 输入补一个长度为 1 的伪 `PressureLevels`
- 统一按三维网格恢复
- 通过线性层把每个 token 扩展到适合 2×2 子像素重排的形式
- 只在 `Height` 和 `Width` 方向做 2 倍上采样
- 最后按 `output_resolution` 做中心裁剪

## 输出规格

- 2D 输出：`(Batch, OutHeight * OutWidth, out_dim)`
- 3D 输出：`(Batch, OutPressureLevels * OutHeight * OutWidth, out_dim)`

默认约束：

- `OutHeight <= 2 * Height`
- `OutWidth <= 2 * Width`
- `OutPressureLevels <= PressureLevels`

## 参数

- `input_resolution`
  - 2D: `(Height, Width)`
  - 3D: `(PressureLevels, Height, Width)`
- `output_resolution`
  - 2D: `(OutHeight, OutWidth)`
  - 3D: `(OutPressureLevels, OutHeight, OutWidth)`
- `in_dim`
  - 输入 token 特征维
- `out_dim`
  - 输出 token 特征维

## 关键依赖

- `sample` 模块族内的相邻组件

## 使用注意与风险

- 这是 token 级组件，不接收图像张量
- 输入 token 数必须与 `input_resolution` 完全匹配
- `out_dim` 不是自动推断值，调用层需要明确传入
- 不建议继续回到旧的 `PanguUpSample2D` / `PanguUpSample3D` 依赖方式

## 启动方式

主要通过 Python API 在模型配置或上层模块中实例化，不是独立 CLI 入口。下面的命令会从源码模块导入组件并打印完整构造签名，便于确认全部 API 参数：

```sh
python -c "from onescience.modules.sample.panguupsample import PanguUpSample; import inspect; print(inspect.signature(PanguUpSample))"
```

在真实任务中应由对应模型配置传入尺寸、通道数和隐空间维度等参数。

## 输入规格

- 2D 输入：`(Batch, Height * Width, in_dim)`
- 3D 输入：`(Batch, PressureLevels * Height * Width, in_dim)`

内部统一做法：

- 对 2D 输入补一个长度为 1 的伪 `PressureLevels`
- 统一按三维网格恢复
- 通过线性层把每个 token 扩展到适合 2×2 子像素重排的形式
- 只在 `Height` 和 `Width` 方向做 2 倍上采样
- 最后按 `output_resolution` 做中心裁剪

默认参数信息：

- `PanguUpSample` 构造默认参数：`in_dim=384`，`out_dim=192`

## 运行接口

- `PanguUpSample`：实例化后通过 `forward` 等运行时接口参与流水线。

## 主要函数

- `forward`

## 执行资源

- 运行设备由上层任务决定，训练和高分辨率推理通常建议使用 GPU。
- 图构建、邻居搜索或大分辨率气象场处理会占用较多内存，批量大小需随网格规模调整。
- 需要保证依赖库和 OneScience 模块路径可用，并与模型配置中的精度、设备和维度设置一致。

## 操作限制

- 不负责完整数据预处理、变量标准化、训练循环或损失函数编排。
- 仅在输入形状、变量顺序、图结构和上下游组件契约一致时可稳定工作。
- 源码中未声明的 CLI 参数、自动下载或外部数据读取能力不应假定存在。

## 规划决策

### 描述

PanguUpSample 是 OneScience 中面向气象/地球系统建模的采样模块，用于在模型流水线中完成特征变换、尺度组织或结果重建。

```text
气象场或 token 特征
  -> 参数化特征变换
  -> 尺度/通道/分支组织
  -> 上层预测模型继续融合或输出
```

### 使用时机

- 任务需要 `采样模块` 能力，且组件输入输出契约与当前模型阶段匹配。
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
3. 按 `usage.md` 的运行接口实例化组件，并传入契约化输入。
4. 检查输出形状、数据类型、设备和变量顺序是否满足下一阶段要求。
5. 在完整模型中通过单步前向或小批量样例验证集成效果。

### 约束

- 不跨越组件职责边界承担数据下载、全局训练调度或模型族外的语义转换。
- 不在未确认形状、图结构或变量顺序时直接替换已有模块。
- 规划中涉及代码位置时只以 `spec.md` 的 `code_references` 为准。

### 下一阶段建议

- 若组件用于新流水线，下一阶段应补齐上游输入准备和下游形状断言。
- 若组件替换已有模块，下一阶段应做等价输入样例对比和端到端 smoke test。

### 回退策略

- 当输入维度或依赖不匹配时，退回到同模型族的统一入口组件或相邻基础组件。
- 当源码缺少独立运行入口时，优先在上层模型配置中集成验证，而不是为该组件臆造 CLI。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/modules/sample/panguupsample.py`
- `{onescience_path}/onescience/src/onescience/modules/sample/onesample.py`
