# 生信模型推理执行契约

## Preflight

每次推理前必须确认：

- `model_family` 与 `entrypoint` 一致。
- `checkpoint` 存在、版本与模型卡一致，或明确需要执行层下载。
- 输入协议正确：FASTA、AF3 JSON、Protenix JSON、PDB、contig、SMILES、DNA prompt 不能互换。
- 运行目录、输出目录、环境变量和数据目录已明确。
- 设备与精度可用：CPU/GPU/DCU、JAX/PyTorch/NeMo、bf16/fp16/fp32、flash attention fallback。
- 随机性可复现：seed、num samples/designs、sampling temperature 或 diffusion steps。

## Run

- 优先使用 `examples/biosciences` 中已有脚本。
- 不要在推理阶段修改模型主体参数，除非用户明确要求模型开发。
- 大数据库、远程硬件、模型下载、外部 docking 或 MSA 搜索需要交给执行层处理权限和资源。
- 运行命令必须记录到 manifest，包含 cwd、env、command、expected outputs。

## Postflight

- 结构预测：检查 PDB/CIF、ranking/confidence、PAE/PDE/pLDDT、空输出、链数/残基数。
- 设计生成：检查 FASTA/PDB/SMILES 有效性、候选数量、score/probability、约束是否被满足。
- 语言模型：检查 logits/sequence、token length、prompt 映射、seq_idx map。
- 小分子：检查 RDKit validity、duplicate、property/reward、外部 docking 是否真正运行。

## 失败恢复

- 依赖缺失：不要降级到错误模型；返回缺失依赖、推荐入口和可继续的本地检查。
- 显存/内存不足：优先降低 samples/designs、diffusion steps、batch size，或切换 attention fallback。
- 输入不合规：先修 manifest 或输入模板，不要强行运行。
- 输出不完整：保留日志和中间文件路径，给出重新运行的最小修改。
