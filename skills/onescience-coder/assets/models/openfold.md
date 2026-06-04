# Model Card: OpenFold

## 基本信息

- 模型名：`OpenFold / AlphaFold`
- 任务类型：`蛋白质结构预测 / AF2-style folding`
- 当前状态：`stable`
- 主实现文件：`./onescience/src/onescience/models/openfold/model.py`

## 模型定位

OpenFold 是 OneScience 中的 AlphaFold2 / OpenFold 风格结构预测实现，适合已有 AF2 特征流水线、MSA、template 和 recycling 协议的蛋白质结构预测任务。

补充说明：

- 模型类名是 `AlphaFold`
- 支持 monomer、multimer 与 seq embedding 相关配置分支
- 它与 Protenix 的主要差异是：OpenFold 使用 Evoformer + StructureModule 的 AF2 协议，Protenix 使用 Pairformer + diffusion 的 AF3 风格协议

## 输入定义

- 主输入：`batch: dict[str, Tensor]`
- 每个 feature 的最后一维是 recycling 维度，forward 中逐 cycle 取 `t[..., cycle_no]`
- 核心字段：
  - `aatype`: `[*, N_res]`
  - `target_feat`: `[*, N_res, C_tf]`
  - `residue_index`: `[*, N_res]`
  - `msa_feat`: `[*, N_seq, N_res, C_msa]`
  - `seq_mask`: `[*, N_res]`
  - `msa_mask`: `[*, N_seq, N_res]`
  - `pair_mask`: `[*, N_res, N_res]`
  - `extra_msa_mask`: `[*, N_extra, N_res]`
  - template 相关字段：`template_aatype`, `template_all_atom_positions`, `template_all_atom_mask`, `template_pseudo_beta`, `template_pseudo_beta_mask`

## 输出定义

- 主结构输出：
  - `final_atom_positions`
  - `final_atom_mask`
  - `final_affine_tensor`
- 中间表征：
  - `msa`
  - `pair`
  - `single`
- 辅助输出：
  - `num_recycles`
  - aux heads 输出，具体取决于配置

## 主干结构

- InputEmbedder / InputEmbedderMultimer
  - 生成 MSA representation 与 pair representation
- RecyclingEmbedder
  - 把上一轮结构、MSA、pair 信息注入下一轮
- Template stack
  - 处理 template pair / template angle 等特征
- ExtraMSAStack
  - 处理 extra MSA
- EvoformerStack
  - 交替更新 MSA、pair、single 表征
- StructureModule
  - IPA 和结构更新，恢复 atom 坐标
- Aux heads
  - 按配置输出 distogram、pLDDT、masked MSA 等辅助头

## 主要依赖组件

- `InputEmbedder`
- `InputEmbedderMultimer`
- `RecyclingEmbedder`
- `ExtraMSAStack`
- `EvoformerStack`
- `StructureModule`

## 主要 Shape 变化

- `msa_feat`: `[*, N_seq, N_res, C_msa]`
- MSA embedding: `[*, N_seq, N_res, C_m]`
- Pair embedding: `[*, N_res, N_res, C_z]`
- Single representation: `[*, N_res, C_s]`
- Structure output atom37: `[*, N_res, 37, 3]`
- recycling 维度在 outer forward 中逐轮消去

## 默认关键参数

- 具体参数来自 `onescience.configs.bio.openfold.config.model_config(...)`
- `config_preset` 决定 monomer / multimer / seq 模式
- `long_sequence_inference`、`use_deepspeed_evoformer_attention` 会影响推理内存与 attention 实现
- tracing 需要 `config.data.predict.fixed_size=True`

## 常见修改点

- 接入新数据时，优先复用 OpenFold feature pipeline，不要只生成 `aatype`
- 改 monomer/multimer 时，需要同时确认 input embedder、template searcher、feature processor 和配置 preset
- 若启用 seq embedding mode，alignment runner 只用于 template，序列表征来自 embedding generator
- 修改 recycling 次数或 fixed-size tracing 时，要同步检查 batch 最后一维和 padding

## 风险点

- OpenFold 的 batch 协议与 `onescience.datapipes.biology.ProteinDataset` 的通用特征不是一回事，需要专门 adapter 或 OpenFold feature pipeline
- `examples/biosciences/openfold/run_pretrained_openfold.py` 会使用 alignment、template、database 工具链，不能离线假设所有特征已存在
- monomer 和 multimer 使用不同 template searcher 与 input embedder，不能只改模型配置名

## 推荐检索顺序

1. 先看本模型卡
2. 再看 `openfold/model.py` 的 `forward` docstring 和 `iteration`
3. 再看 `embedders.py`、`evoformer.py`、`structure_module.py`
4. 若涉及推理脚本，再看 `examples/biosciences/openfold/run_pretrained_openfold.py`

## 组件契约入口

- `../contracts/openfoldevoformer.md`
- `../contracts/openfoldstructuremodule.md`
- 当前 OpenFold 主体未通过 OneScience `One*` wrapper 拼装，按 OpenFold 模型源码、组件契约和 feature pipeline 对齐

## 源码锚点

- `./onescience/src/onescience/models/openfold/model.py`
- `./onescience/src/onescience/models/openfold/embedders.py`
- `./onescience/src/onescience/models/openfold/evoformer.py`
- `./onescience/src/onescience/models/openfold/structure_module.py`
- `./onescience/examples/biosciences/openfold/run_pretrained_openfold.py`
