# Contract: FuxiEmbedding

## 基本信息

- **组件名称**: FuxiEmbedding
- **模块族**: embedding
- **统一入口**: OneEmbedding
- **注册名称**: style="FuxiEmbedding"

## 组件说明

将多时间步二维气象场组成的三维时空块切分为三维 patch，并投影到统一的 embedding 特征空间。

这是 Fuxi 输入编码阶段的 patch embedding 组件。

补充说明：

- 该组件处理的是三维时空块 `(TimeSteps, Height, Width)`
- 输出是三维 patch 特征图，不是展平 token 序列
- 当前实现不做自动 padding

该组件的核心实现包括 `FuxiEmbedding`，定位为嵌入层，由上层 OneScience 模型或流水线通过 Python API 调用。

## 用途

把原始数值特征、patch 或图节点/边特征投影到统一隐空间，适用于主干网络进入前的特征标准化表达。

## 输入规格

- 2D 输入：`not_applicable`
- 3D 输入：`(Batch, in_chans, TimeSteps, Height, Width)`

内部统一做法：

- 使用 `Conv3d` 完成 patch 切分和线性投影
- 可选 `norm_layer` 作用在展平后的 patch token 上
- 最终再恢复回三维 patch 特征图

## 输出规格

- 2D 输出：`not_applicable`
- 3D 输出：`(Batch, embed_dim, OutTimeSteps, OutHeight, OutWidth)`

其中：

- `OutTimeSteps = TimeSteps // PatchTimeSteps`
- `OutHeight = Height // PatchHeight`
- `OutWidth = Width // PatchWidth`

## 参数

- `img_size`
  - 输入空间尺寸 `(TimeSteps, Height, Width)`
- `patch_size`
  - patch 切分尺寸 `(PatchTimeSteps, PatchHeight, PatchWidth)`
- `in_chans`
  - 输入变量通道数
- `embed_dim`
  - 输出特征维度
- `norm_layer`
  - 可选归一化层

## 关键依赖

- `embedding` 模块族内的相邻组件

## 使用注意与风险

- 该组件不支持二维输入
- 当前实现不做自动 padding，不能整除的尾部区域不会进入输出特征图
- Fuxi 当前调用层通常要求 `OutTimeSteps = 1`

## 启动方式

主要通过 Python API 在模型配置或上层模块中实例化，不是独立 CLI 入口。下面的命令会从源码模块导入组件并打印完整构造签名，便于确认全部 API 参数：

```sh
python -c "from onescience.modules.embedding.fuxiembedding import FuxiEmbedding; import inspect; print(inspect.signature(FuxiEmbedding))"
```

在真实任务中应由对应模型配置传入尺寸、通道数和隐空间维度等参数。

## 输入规格

- 2D 输入：`not_applicable`
- 3D 输入：`(Batch, in_chans, TimeSteps, Height, Width)`

内部统一做法：

- 使用 `Conv3d` 完成 patch 切分和线性投影
- 可选 `norm_layer` 作用在展平后的 patch token 上
- 最终再恢复回三维 patch 特征图

默认参数信息：

- `FuxiEmbedding` 构造默认参数：`img_size=(2, 721, 1440)`，`patch_size=(2, 4, 4)`，`in_chans=70`，`embed_dim=1536`，`norm_layer=nn.LayerNorm`

## 运行接口

- `FuxiEmbedding`：实例化后通过 `forward` 等运行时接口参与流水线。

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

FuxiEmbedding 是 OneScience 中面向气象/地球系统建模的嵌入层，用于在模型流水线中完成特征变换、尺度组织或结果重建。

```text
气象场或 token 特征
  -> 参数化特征变换
  -> 尺度/通道/分支组织
  -> 上层预测模型继续融合或输出
```

### 使用时机

- 任务需要 `嵌入层` 能力，且组件输入输出契约与当前模型阶段匹配。
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

- `{onescience_path}/onescience/src/onescience/modules/embedding/fuxiembedding.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/oneembedding.py`
- `{onescience_path}/onescience/src/onescience/models/fuxi/fuxi.py`
