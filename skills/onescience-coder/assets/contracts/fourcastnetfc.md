# Contract: FourCastNetFC

## 基本信息

- **组件名称**: FourCastNetFC
- **模块族**: fc
- **统一入口**: OneFC
- **注册名称**: style="FourCastNetFC"

## 组件说明

在最后一个特征维度上执行两层前馈映射，完成逐位置通道混合。

补充说明：

- 该组件通常位于 `FourCastNetFuser` 中的 AFNO 之后
- 它不关心前面的 batch 或空间维度
- 本质上是一个作用在最后一维上的 MLP

该组件的核心实现包括 `FourCastNetFC`，定位为全连接/投影模块，由上层 OneScience 模型或流水线通过 Python API 调用。

## 用途

对通道或 token 表示做线性投影、展开或重排，适用于模型头尾连接。

## 输入规格

- 2D 输入：`(..., in_features)`
- 3D 输入：`(..., in_features)`

内部统一做法：

- 对最后一个特征维度执行 `Linear -> Act -> Dropout -> Linear -> Dropout`
- 保持前面的所有维度不变

## 输出规格

- 2D 输出：`(..., out_features)`
- 3D 输出：`(..., out_features)`

明确约束：

- 该组件不依赖固定空间 shape
- 主要约束来自最后一维的特征维度匹配

## 参数

- `in_features`
  - 输入特征维度
- `hidden_features`
  - 隐层特征维度
- `out_features`
  - 输出特征维度
- `act_layer`
  - 激活函数类型
- `drop`
  - dropout 比例

## 关键依赖

- `fc` 模块族内的相邻组件

## 使用注意与风险

- 该组件不是空间算子，不能直接把它当作 embedding 或 fuser 使用
- 主要检查点是最后一维是否与调用层一致

## 启动方式

主要通过 Python API 在模型配置或上层模块中实例化，不是独立 CLI 入口。下面的命令会从源码模块导入组件并打印完整构造签名，便于确认全部 API 参数：

```sh
python -c "from onescience.modules.fc.fourcastnetfc import FourCastNetFC; import inspect; print(inspect.signature(FourCastNetFC))"
```

在真实任务中应由对应模型配置传入尺寸、通道数和隐空间维度等参数。

## 输入规格

- 2D 输入：`(..., in_features)`
- 3D 输入：`(..., in_features)`

内部统一做法：

- 对最后一个特征维度执行 `Linear -> Act -> Dropout -> Linear -> Dropout`
- 保持前面的所有维度不变

默认参数信息：

- `FourCastNetFC` 构造默认参数：`in_features=768`，`hidden_features=3072`，`out_features=None`，`act_layer=nn.GELU`，`drop=0.0`

## 运行接口

- `FourCastNetFC`：实例化后通过 `forward` 等运行时接口参与流水线。

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

FourCastNetFC 是 OneScience 中面向气象/地球系统建模的全连接/投影模块，用于在模型流水线中完成特征变换、尺度组织或结果重建。

```text
气象场或 token 特征
  -> 参数化特征变换
  -> 尺度/通道/分支组织
  -> 上层预测模型继续融合或输出
```

### 使用时机

- 任务需要 `全连接/投影模块` 能力，且组件输入输出契约与当前模型阶段匹配。
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

- `{onescience_path}/onescience/src/onescience/modules/fc/fourcastnetfc.py`
- `{onescience_path}/onescience/src/onescience/modules/fc/onefc.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/fourcastnetfuser.py`
