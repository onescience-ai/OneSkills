# Contract: OnePairformer

## 基本信息

- 组件名：`OnePairformer`
- 所属模块族：`pairformer`
- 统一入口：`direct_import`
- 注册名：`style="<PairformerStyle>"`

## 组件职责

为 Pairformer 类模块提供统一入口，当前主要用于 Protenix 的 pair / single 表征更新。

补充说明：

- `ProtenixPairformerStack` 是 Protenix trunk 的高层堆栈
- `ProtenixPairformerBlock` 也直接注册，可在 MSA block 内作为局部 pair update 使用
- wrapper 不定义 shape，具体约束来自 `protenixpairformer.md`

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- 生信 token-pair 输入：
  - `s`: `[..., N_token, c_s]` 或 `None`
  - `z`: `[..., N_token, N_token, c_z]`
  - `pair_mask`: `[..., N_token, N_token]` 或 `None`

内部统一做法：

- 根据 `style` 实例化 pairformer 实现
- forward 时透传 `s`, `z`, `pair_mask` 和低内存 attention 参数

## 构造参数

- `style`
  - `ProtenixPairformerBlock`
  - `ProtenixPairformerStack`
- `**kwargs`
  - 常见为 `n_blocks`, `n_heads`, `c_z`, `c_s`, `dropout`, `blocks_per_ckpt`

## 输出约定

- `ProtenixPairformerStack` 输出：
  - `s`: `[..., N_token, c_s]`
  - `z`: `[..., N_token, N_token, c_z]`
- 当 `c_s=0` 或 `s=None` 的 block 路线中，single 分支不更新，主要输出 updated `z`

## 典型调用位置

- Protenix recycling trunk
- Protenix MSA block 内部 pair stack
- Protenix template embedder 内部 pairformer stack

## 典型参数

- Protenix trunk
  - `style="ProtenixPairformerStack"`
  - `n_blocks=48`
  - `n_heads=16`
  - `c_z=128`
  - `c_s=384`
- Protenix MSA 内部 pair block
  - `style="ProtenixPairformerBlock"`
  - `c_z=128`
  - `c_s=0`

## 风险点

- Pairformer 的 `z` 是二阶 pair 表征，显存随 `N_token^2` 增长
- `pair_mask=None` 在当前 Protenix 路线可出现，但自定义任务若有 padding，应先确认 mask 语义
- `use_deepspeed_evo_attention` 在 `N_token <= 16` 时会被 Protenix 调用层关闭

## 源码锚点

- `./onescience/src/onescience/modules/pairformer/onepairformer.py`
- `./onescience/src/onescience/modules/pairformer/protenixpairformer.py`
