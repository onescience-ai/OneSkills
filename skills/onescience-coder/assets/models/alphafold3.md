# Model Card: AlphaFold3

## 基本信息

- 模型名：`AlphaFold3`
- 任务类型：`蛋白质 / 核酸 / 配体复合物结构预测 / AF3-style JAX inference`
- 当前状态：`stable`
- 主实现文件：`./onescience/src/onescience/flax_models/alphafold3/model/model.py`

## 模型定位

AlphaFold3 是 OneScience 中的 JAX/Haiku AF3 风格结构预测实现，面向蛋白、RNA、DNA、配体、离子以及共价连接等复合物输入。

补充说明：

- 它与 `Protenix` 同属 AF3 风格结构预测，但实现栈不同：AlphaFold3 是 JAX/Haiku，Protenix 是 OneScience PyTorch 模块化实现
- 它有自己的 JSON 输入、data pipeline、featurisation、bucket、JAX 编译和 flash attention 选择
- example 主入口是 `examples/biosciences/alphafold3/run_alphafold.py`
- 如果需求是“修改 OneScience `One*` 组件注册”，优先看 `Protenix`；如果需求是“复用 AF3 JAX 推理脚本”，优先看本卡

## 输入定义

- 推理脚本入口：
  - `--json_path` 或 `--input_dir`
  - `--model_dir`
  - `--output_dir`
  - `--run_data_pipeline`
  - `--run_inference`
  - `--flash_attention_implementation`
  - `--num_recycles`
  - `--num_diffusion_samples`
- JSON 输入可包含：
  - `proteinChain`
  - `rnaSequence`
  - `dnaSequence`
  - `ligand`
  - templates / MSA / user CCD / bonds 等 AF3 folding input 信息
- 模型 forward 输入：
  - `batch: features.BatchDict`
  - 内部转为 `feat_batch.Batch`
- 关键 batch 语义：
  - `token_features`
  - `msa`
  - `templates`
  - `ref_structure`
  - `predicted_structure_info`
  - `atom_cross_att`
  - polymer-ligand / ligand-ligand bond layouts

## 输出定义

- `Model.__call__` 输出：
  - `diffusion_samples`: `atom_positions`, `mask`
  - `distogram`
  - `predicted_lddt`
  - `predicted_experimentally_resolved`
  - `full_pde`, `average_pde`
  - `full_pae`, `tmscore_adjusted_pae_global`, `tmscore_adjusted_pae_interface`
  - 可选 `single_embeddings`, `pair_embeddings`
- post-processing 输出：
  - 结构文件
  - ranking score / metadata
  - full PAE / PDE / contact probabilities
  - 可选 embeddings / distogram 文件

## 主干结构

- `ModelRunner`
  - 加载 Haiku 参数，JIT model forward，抽取 inference results
- `Model`
  - 构造 `feat_batch.Batch`
  - 执行 target feature embedding、recycling trunk、diffusion sampling 和 confidence heads
- `Evoformer`
  - 创建 target/single/pair embeddings
  - 处理 template、MSA、bond embedding
  - 使用 PairFormerIteration 更新 single/pair
- `DiffusionHead`
  - 基于 noisy atom positions、trunk embeddings 和 atom cross attention 生成坐标样本
- `ConfidenceHead`
  - 基于 diffusion samples 和 embeddings 输出 pLDDT、PAE、PDE、resolved 等置信度
- `atom_cross_att_encoder / atom_cross_att_decoder`
  - 在 token atom layout 与局部 atom query/key layout 之间桥接

## 主要依赖组件

- `Model`
- `ModelRunner`
- `Evoformer`
- `PairFormerIteration`
- `DiffusionHead`
- `ConfidenceHead`
- `DistogramHead`
- `atom_cross_att_encoder`
- `atom_cross_att_decoder`
- `DataPipeline / featurise_input`

## 主要 Shape 变化

- JSON fold input -> `features.BatchDict`
- `target_feat`: `[N_token, C_target]`
- trunk single: `[N_token, 384]`
- trunk pair: `[N_token, N_token, 128]`
- diffusion dense atom positions: `[N_sample, N_token, max_atoms_per_token, 3]`
- post-processing 后映射到 flat output atom layout

## 默认关键参数

- `num_recycles=10`
- `num_diffusion_samples=5`
- diffusion eval 默认 `steps=200`
- bucket 默认包含 `256` 到 `5120` 的 token 档位
- `flash_attention_implementation` 支持 `triton`, `cudnn`, `xla`, `cutlass`

## 常见修改点

- 已有 MSA 的 JSON 推理：设置 `--run_data_pipeline=false`
- 只做 JackHmmer / MMseqs 搜索：设置 `--run_inference=false`
- GPU / attention 兼容性问题：优先改 `--flash_attention_implementation=xla` 或脚本里的 GPU device
- 需要保存 trunk 表征：设置 `--save_embeddings=true`，但要注意 pair embeddings 很大
- 需要保存 distogram：设置 `--save_distogram=true`

## 风险点

- AlphaFold3 JAX batch 与 Protenix feature dict 概念相近但实现不兼容，不能直接共享 adapter
- 模型参数和输出使用条款应由用户自行确认，skill 中不要隐含替用户接受
- data pipeline 阶段可能启动大量 CPU 线程，尤其是 sharded JackHmmer / Nhmmer 数据库
- Triton / cuDNN flash attention 对 GPU 架构和环境要求更高，保守兼容可选 `xla`
- 配体与 CCD / RDKit conformer 路线对资源文件和化学组件数据敏感

## 推荐检索顺序

1. 先看本模型卡
2. 再看 `examples/biosciences/alphafold3/README.md`
3. 若改推理命令，读 `examples/biosciences/alphafold3/run_alphafold.py`
4. 若改模型主体，读 `flax_models/alphafold3/model/model.py`
5. 若改 trunk / diffusion / confidence，读对应组件契约

## 组件契约入口

- `../contracts/alphafold3jaxcomponents.md`
- 当前 AlphaFold3 不通过 OneScience `One*` wrapper 拼装；若要 PyTorch/One* 组件级改造，优先看 `protenix.md`

## 源码锚点

- `./onescience/src/onescience/flax_models/alphafold3/model/model.py`
- `./onescience/src/onescience/flax_models/alphafold3/model/network/evoformer.py`
- `./onescience/src/onescience/flax_models/alphafold3/model/network/modules.py`
- `./onescience/src/onescience/flax_models/alphafold3/model/network/diffusion_head.py`
- `./onescience/src/onescience/flax_models/alphafold3/model/network/atom_cross_attention.py`
- `./onescience/src/onescience/flax_models/alphafold3/model/network/confidence_head.py`
- `./onescience/examples/biosciences/alphafold3/run_alphafold.py`
- `./onescience/examples/biosciences/alphafold3/README.md`
