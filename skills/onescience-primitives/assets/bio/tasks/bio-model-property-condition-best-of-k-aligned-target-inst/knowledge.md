# 实例任务：模型与性质条件准备 @ B53

- domain: bio
- 骨架: bio-model-property-condition-preparation-task
- 场景: bio-best-of-k-aligned-target-specific-3d-molecule-generation-scenario (B53)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- B53
- 关联论文: BoKDiff: Best-of-K Diffusion Alignment for Target-Specific 3D Molecule Generation | doi:; TAGMol: Target-Aware Gradient-guided Molecule Generation | doi:
- 依据官方提交 `b3c7da493a13ab3d84b28057748d7c03ab7b0303` 的 [README 权重与数据来源](https://github.com/khodabandeh-ali/BoKDiff/blob/b3c7da493a13ab3d84b28057748d7c03ab7b0303/README.md)、[sample_diffusion_decomp.py:504–585](https://github.com/khodabandeh-ali/BoKDiff/blob/b3c7da493a13ab3d84b28057748d7c03ab7b0303/scripts/sample_diffusion_decomp.py#L504)、[transforms.py:41–65、114–154、257–280](https://github.com/khodabandeh-ali/BoKDiff/blob/b3c7da493a13ab3d84b28057748d7c03ab7b0303/utils/transforms.py#L41) 与 [pl_pair_dataset.py:23–74](https://github.com/khodabandeh-ali/BoKDiff/blob/b3c7da493a13ab3d84b28057748d7c03ab7b0303/datasets/pl_pair_dataset.py#L23)核对以下加载契约。把实际数据 manifest、model_loading_plan 和 inference_contract 交给现有 infer/coder 消费；文档定位不代表二进制可用。

## 本实例步骤描述
加载权重并编码靶点、片段和优化性质。

1. 从本次权重清单核验对齐目标、发布来源、checkpoint 角色、实际路径和 hash；`bokdiff.ckpt` 只是占位。指定已对齐推理时，不能用基础权重、其他模型或从头训练代替后沿用对齐结论。
2. 按官方入口解析实际路径：`args.ckpt_path` 优先于 `config.model.checkpoint`；所选 `ckpt['config'].model` 用于构造 `DecompScorePosNet3D`，`ckpt['model']` 用于 `strict=True` 加载。若配置有 `model.train_config`，入口会替换 `ckpt['config']`，须核验覆盖后的结构与权重兼容。记录真实打开的路径和 hash；成功日志打印的 `config.model.checkpoint` 可能不同，不能单独作为证据。
3. 分开登记配套基础文件 `./pretrained_models/uni_o2_bond.pt`：入口从其 `ckpt_base['config'].data` 调 `get_decomp_dataset`，再取 `subsets['test']` 为 `val_set`。该角色提供数据配置，不等于选用基础权重替代对齐模型；不能直接拿采样 YAML 的 data 段覆盖它。
4. 在实例化 `DecompPLPairDataset` 前，按实际 `raw_path/mode/version` 核对处理文件：与 raw_path 同父目录的 `<raw_basename>_<mode>_<version>.lmdb` 和 `<raw_basename>_<mode>_<version>_name2id.pt`，以及 `config.split` 指向的 `split_by_name.pt`。缺文件时类会触发 `_process()` 或 `_precompute_name2id()` 写盘；原始输入只读时应先记录缺项，获准预处理后另写工作目录，不能隐式回写输入。
5. 按 split 算法把每个 `n[1][:-4]` 配体名映射到 `dataset.name2id` 的索引列表并展开；缺名会被跳过，必须核对其影响。验证 `args.data_id → val_set` 的实际记录与同编号 `test_index`、`src_protein_filename`、配体和分解字段一致，不假设两套索引天然同序。普通 TargetDiff 的 `PocketLigandPairDataset`/LMDB 不能替代分解数据。
6. 从生效 checkpoint 配置解析原子/键编码、indicator、先验与重构映射；只在模型实际支持时编码额外性质条件或固定骨架。完成现有 infer 的 strict 加载与公共 API 核对后，交接实际模型、数据身份及特征规格。

## 本实例执行 prompt
核验并严格加载{CHECKPOINT}，将{OBJECTIVES}解释为本次目标及权重对齐身份；只有真实模型支持额外性质条件输入时才编码条件向量。按{KEEP_SCAFFOLD}与实际生成接口决定是否固定骨架，不为已对齐 complete 推理强造接口。分开核对对齐 checkpoint、基础配置 checkpoint 与官方数据映射，并保存加载证据。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=核对发布来源、对齐目标和实际文件hash | default=bokdiff.ckpt（占位）
- {OBJECTIVES} | required=False | type=list[str] | var_name=优化目标 | hint=列出需要优化的性质 | default=['QED', 'SA', 'affinity']
- {KEEP_SCAFFOLD} | required=False | type=bool | var_name=保留核心骨架 | hint=是否固定输入分子骨架 | default=False

## 本实例产出
- 模型加载记录：对齐/基础权重各自路径、来源、hash、用途，CLI/YAML/训练配置的生效值、模型类、strict 加载结果与真实异常。
- 性质条件向量：仅在接口支持时交付；否则交付权重对齐目标与性质定义，不伪造输入张量。
- 骨架约束：仅对支持分支给原子映射；其余注明不适用。
- 数据 manifest：mode/version、LMDB/name2id/split 身份，展开后的 test 索引、选中记录、源文件和分解/参考先验信息；附特征维数及来源，供采样消费者核对。

## 本实例质量门禁
- 权重版本可追溯；保留 strict 加载原错，禁止 `strict=False` 吞掉不匹配。
- 性质定义完整；固定骨架分支的原子映射有效，不支持的条件不得假装生效。
- 从实际 featurizer 核对蛋白基础维数 `6+20+1=27`；配体 `basic` 的索引顺序为 H/C/N/O/F/P/S/Cl 共 8 类，`add_aromatic` 为 13 个元素/芳香性类别。分解 indicator 对蛋白/配体各加 2 维，启用 `add_ord_feat` 时再加 `max_num_arms+1`；总输入维数为基础维数加 indicator，类别数仍来自配体 featurizer。核对实际开关、键扩散、键编码与重构反向映射，不把参考 YAML 维数强塞给权重。
- 核对 `ref_prior` 经 `compute_golden_prior_from_data(data)` 使用的参考分解信息，并与输入对象一致；没有加载/张量验证时不得声称兼容性已通过。

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造。）先按本地 onestore 的元数据和精确路径核验，再提交包含官方提交、对齐目标、两类 checkpoint 角色、处理数据 mode/version、split 与特征要求的资源请求。
- 仅当本次网络策略允许时，沿上述官方 README 的基础/对齐权重及处理数据链接获取并验明身份；目录说明不证明文件存在，有界检索未命中也不证明全部共享归档缺失。

## 验收/缺失策略（继承场景）
- acceptance: 从任务清单绑定加载与输入验收要求，交出可核对的加载记录、性质定义和数据映射。
- missing_policy: 分开报告资产未定位、后端缺失和模型不兼容；沿已有 infer/runtime 交接处理，不用基础模型替代，也不从知识修改推断资源已经修复。
