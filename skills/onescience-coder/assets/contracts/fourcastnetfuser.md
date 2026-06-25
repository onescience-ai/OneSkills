# Contract: FourCastNetFuser

## 基本信息

- **组件名称**: FourCastNetFuser
- **模块族**: fuser
- **统一入口**: OneFuser
- **注册名称**: style="FourCastNetFuser"

## 组件说明

在二维 patch 网格 `(Height, Width)` 上完成 FourCastNet 主干特征融合。

补充说明：

- 该组件处理的是二维 patch 网格特征，不是原始图像
- 内部先做 AFNO 频域混合，再做逐位置 MLP 通道混合
- 它是 FourCastNet 主模型中重复堆叠的核心 trunk block

该组件的核心实现包括 `FourCastNetFuser`，定位为融合模块，由上层 OneScience 模型或流水线通过 Python API 调用。

## 用途

融合来自不同变量、尺度、时间步或分支的特征，适用于多源气象场建模。

## 输入规格

- 2D 输入：`(Batch, Height, Width, dim)`
- 3D 输入：`not_applicable`

内部统一做法：

- 先做 `LayerNorm`
- 再调用 `OneAFNO(style="FourCastNetAFNO2D")`
- 再调用 `OneFC(style="FourCastNetFC")`
- 通过残差连接与 `DropPath` 完成 block 输出

## 输出规格

- 2D 输出：`(Batch, Height, Width, dim)`
- 3D 输出：`not_applicable`

明确约束：

- 输出 shape 与输入 shape 保持一致
- `dim` 必须与上下游 embedding / head 的特征维度对齐

## 参数

- `dim`
  - 输入与输出特征维度
- `mlp_ratio`
  - MLP 隐层放大倍数
- `drop`
  - MLP dropout 比例
- `drop_path`
  - Stochastic Depth 比例
- `double_skip`
  - 是否启用中间残差连接
- `num_blocks`
  - AFNO 的通道分块数
- `sparsity_threshold`
  - AFNO soft shrink 阈值
- `hard_thresholding_fraction`
  - AFNO 保留的频率模式比例
- `act_layer`, `norm_layer`
  - 激活函数与归一化层类型

## 关键依赖

- `onefuser`
- `oneafno`
- `fourcastnetafno`
- `onefc`
- `fourcastnetfc`
- `layers`

## 使用注意与风险

- 该组件输入是二维 patch 网格，不是展平 token 序列
- 若调用层忘记把 token 序列恢复成 `(Height, Width)` 网格，shape 会不匹配
- `num_blocks` 必须能与内部 AFNO 的 `dim` 配合整除

## 启动方式

主要通过 Python API 在模型配置或上层模块中实例化，不是独立 CLI 入口。下面的命令会从源码模块导入组件并打印完整构造签名，便于确认全部 API 参数：

```sh
python -c "from onescience.modules.fuser.fourcastnetfuser import FourCastNetFuser; import inspect; print(inspect.signature(FourCastNetFuser))"
```

在真实任务中应由对应模型配置传入尺寸、通道数和隐空间维度等参数。

## 输入规格

- 2D 输入：`(Batch, Height, Width, dim)`
- 3D 输入：`not_applicable`

内部统一做法：

- 先做 `LayerNorm`
- 再调用 `OneAFNO(style="FourCastNetAFNO2D")`
- 再调用 `OneFC(style="FourCastNetFC")`
- 通过残差连接与 `DropPath` 完成 block 输出

默认参数信息：

- `FourCastNetFuser` 构造默认参数：`dim=768`，`mlp_ratio=4.0`，`drop=0.0`，`drop_path=0.0`，`act_layer=nn.GELU`，`norm_layer=nn.LayerNorm`，`double_skip=True`，`num_blocks=8`，`sparsity_threshold=0.01`，`hard_thresholding_fraction=1.0`

## 运行接口

- `FourCastNetFuser`：实例化后通过 `forward` 等运行时接口参与流水线。

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

FourCastNetFuser 是 OneScience 中面向气象/地球系统建模的融合模块，用于在模型流水线中完成特征变换、尺度组织或结果重建。

```text
气象场或 token 特征
  -> 参数化特征变换
  -> 尺度/通道/分支组织
  -> 上层预测模型继续融合或输出
```

### 使用时机

- 任务需要 `融合模块` 能力，且组件输入输出契约与当前模型阶段匹配。
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

- `{onescience_path}/onescience/src/onescience/modules/fuser/fourcastnetfuser.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/onefuser.py`
- `{onescience_path}/onescience/src/onescience/models/fourcastnet/fourcastnet.py`
