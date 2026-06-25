# Contract: FengWuDecoder

## 基本信息

- **组件名称**: `FengWuDecoder`
- **模块族**: `decoder`
- **统一入口**: `not_applicable`
- **注册名称**: `style="FengWuDecoder"`

## 组件说明

将单个变量分支的中分辨率 token 序列与高分辨率 skip 特征解码为原始分辨率输出场。

补充说明：

- 该组件处理的是单个变量分支，不负责跨变量融合
- 内部使用 `EarthTransformer2DBlock`、`PanguUpSample` 和 `PanguPatchRecovery`
- 输入通常来自 `FengWuFuser` 的单分支切分结果和对应 encoder 的 skip 特征

该组件的核心实现包括 `FengWuDecoder`，定位为解码器，由上层 OneScience 模型或流水线通过 Python API 调用。

## 用途

将潜在表示恢复到目标网格、变量通道或图节点空间，适用于模型后段的结果重建。

## 输入规格

- 2D 输入：
  - `inp[0]`: `(Batch, middle_resolution[0] * middle_resolution[1], 2 * dim)`
  - `inp[1]`: `(Batch, output_resolution[0], output_resolution[1], dim)`
- 3D 输入：`not_applicable`

内部统一做法：

- 先处理中分辨率 token 序列
- 上采样回高分辨率 token 网格
- 在高分辨率上继续做 2D Transformer
- 与 skip 特征拼接后恢复为原始分辨率场

## 输出规格

- 2D 输出：`(Batch, out_chans, img_size[0], img_size[1])`
- 3D 输出：`not_applicable`

## 参数

- `output_resolution`
  - 高分辨率 patch 网格尺寸 `(Height, Width)`
- `middle_resolution`
  - 中分辨率 patch 网格尺寸 `(Height, Width)`
- `out_chans`
  - 输出变量通道数
- `img_size`
  - 原始输出场尺寸 `(Height, Width)`
- `patch_size`
  - patch 恢复尺寸 `(PatchHeight, PatchWidth)`
- `dim`
  - 高分辨率特征维度
- `depth`
  - 高分辨率 Transformer block 层数
- `depth_middle`
  - 中分辨率 Transformer block 层数
- `num_heads`
  - 若为二元组，顺序为 `(HighResolutionHeads, MiddleResolutionHeads)`
- `window_size`
  - 二维窗口大小
- `drop_path`
  - 可为单值或按层提供的序列

## 关键依赖

- `onedecoder`
- `onesample`
- `panguupsample`
- `onerecovery`
- `pangupatchrecovery`
- `onetransformer`
- `earthtransformer2dblock`
- `oneattention`
- `earthattention2d`

## 使用注意与风险

- 该组件处理的是单个变量分支，不要把多个变量分支混在一起输入
- `num_heads` 二元组顺序是 `(高分辨率, 中分辨率)`
- `inp[1]` 是二维网格 skip 特征，不是展平 token 序列

## 启动方式

主要通过 Python API 在模型配置或上层模块中实例化，不是独立 CLI 入口。下面的命令会从源码模块导入组件并打印完整构造签名，便于确认全部 API 参数：

```sh
python -c "from onescience.modules.decoder.fengwudecoder import FengWuDecoder; import inspect; print(inspect.signature(FengWuDecoder))"
```

在真实任务中应由对应模型配置传入尺寸、通道数和隐空间维度等参数。

## 输入规格

- 2D 输入：
  - `inp[0]`: `(Batch, middle_resolution[0] * middle_resolution[1], 2 * dim)`
  - `inp[1]`: `(Batch, output_resolution[0], output_resolution[1], dim)`
- 3D 输入：`not_applicable`

内部统一做法：

- 先处理中分辨率 token 序列
- 上采样回高分辨率 token 网格
- 在高分辨率上继续做 2D Transformer
- 与 skip 特征拼接后恢复为原始分辨率场

默认参数信息：

- `FengWuDecoder` 构造默认参数：`output_resolution=(181, 360)`，`middle_resolution=(91, 180)`，`out_chans=37`，`img_size=(721, 1440)`，`patch_size=(4, 4)`，`dim=192`，`depth=2`，`depth_middle=6`，`num_heads=(6, 12)`，`window_size=(6, 12)`，`mlp_ratio=4.0`，`qkv_bias=True`，`qk_scale=None`，`drop=0.0`，`attn_drop=0.0`，`drop_path=0.0`，`norm_layer=nn.LayerNorm`

## 运行接口

- `FengWuDecoder`：实例化后通过 `forward` 等运行时接口参与流水线。

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

FengWuDecoder 是 OneScience 中面向气象/地球系统建模的解码器，用于在模型流水线中完成特征变换、尺度组织或结果重建。

```text
气象场或 token 特征
  -> 参数化特征变换
  -> 尺度/通道/分支组织
  -> 上层预测模型继续融合或输出
```

### 使用时机

- 任务需要 `解码器` 能力，且组件输入输出契约与当前模型阶段匹配。
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

- `{onescience_path}/onescience/src/onescience/modules/decoder/fengwudecoder.py`
- `{onescience_path}/onescience/src/onescience/modules/decoder/onedecoder.py`
- `{onescience_path}/onescience/src/onescience/models/fengwu/fengwu.py`
