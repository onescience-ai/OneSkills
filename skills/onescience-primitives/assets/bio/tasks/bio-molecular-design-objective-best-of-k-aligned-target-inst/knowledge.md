# 实例任务：分子设计目标定义 @ B53

- domain: bio
- 骨架: bio-molecular-design-objective-definition-task
- 场景: bio-best-of-k-aligned-target-specific-3d-molecule-generation-scenario (B53)
- step_id: s01
- depend: []

## 场景研究主体
- B53
- 关联论文: BoKDiff: Best-of-K Diffusion Alignment for Target-Specific 3D Molecule Generation | doi:; TAGMol: Target-Aware Gradient-guided Molecule Generation | doi:
- 按 [BoKDiff arXiv:2501.15631v1 §3、§4.3](https://arxiv.org/html/2501.15631v1) 区分奖励排序微调与免训练选优；按[官方 README 的数据、权重及 Sampling 说明](https://github.com/khodabandeh-ali/BoKDiff/blob/b3c7da493a13ab3d84b28057748d7c03ab7b0303/README.md)核对已发布权重推理所需对象。以下实现说明绑定官方提交 `b3c7da493a13ab3d84b28057748d7c03ab7b0303`，不将 TAGMol 的梯度引导接口移植给 BoKDiff。

## 本实例步骤描述
解析Best-of-K对齐的靶标特异性三维分子生成的靶点、种子分子和生成任务。

1. 先绑定本次输入清单与路线：Best-of-K 是对生成物按奖励排序选优后微调；Best-of-N 是生成后选优而不微调；已发布对齐 checkpoint 仅推理则直接加载指定权重，记录其训练对齐目标，不重新训练。奖励排序不要求 QED/SA/Vina 可微，不能据此称为梯度引导。
2. 对官方 DecompDiff cross-docked 输入，从 `test_index.pkl` 的所选记录解析 `data.protein_file` 和配体身份，再核对源受体/配体、fragment、分解及 meta 伴随记录；保持原子映射、坐标系与对象对应关系，交出实际路径、版本及 hash。索引值和文件名随本次清单变化，不固定为某个靶点。
3. 标注 cross-docked 配体为参照输入：其位姿不自动等于该受体的实验 native pose，也不是实测亲和标签。若使用参考分解/原子数信息或 `ref_prior`，声明参考知情条件，并把该约束交给后续模型准备与评价。

## 本实例执行 prompt
读取{MOLECULE_INPUT}并检查化学结构，使用{MODEL_NAME}建立{GENERATION_MODE}模式的Best-of-K对齐的靶标特异性三维分子生成任务。先确认调用方要求的是训练对齐、免训练选优还是已对齐权重仅推理；按输入清单核对官方记录、源结构和分解伴随文件，将对象身份与证据边界交给后续步骤。

## 本实例输入槽
- {MOLECULE_INPUT} | required=True | type=doc | var_name=分子设计输入 | hint=输入靶点或分子文件 | default=target_pocket.pdb（仅示例，实际从输入清单解析）
- {MODEL_NAME} | required=True | type=enum | var_name=分子模型 | hint=选择场景使用的模型 | default=BoKDiff
- {GENERATION_MODE} | required=False | type=enum | var_name=生成模式 | hint=选择分子生成任务 | default=de_novo

## 本实例产出
- 标准化分子输入：附官方索引记录、源受体/配体文件名、fragment/分解/meta 的对应表、实际来源及 hash。
- 靶点条件：附参考坐标系、口袋定义、参考知情先验及其适用限制。
- 生成任务配置：附路线、对齐目标、权重身份要求、规模、种子、预算和验收条件，供模型准备/采样/评价消费。

## 本实例质量门禁
- 分子化学价合法。
- 靶点条件可解析；索引、源对象与分解记录必须一致，不能把任意同名口袋视为已匹配。
- 生成模式与输入兼容；仅推理要求不转成重新对齐训练，缺少配体/分解条件时不冒用参考先验。
- 将单口袋单队列结论限定为该参考知情条件下的计算候选评价；需要匹配的基础/对齐对照实验才能归因对齐收益，不能推断实验活性或跨靶点泛化。

## 可调资源（edge:resource，仅真实存在）
- tools/simplefold-protein-structure-prediction-model-and-pipeline：仅当另行要求蛋白结构预测时使用；该资源存在不证明 BoKDiff 的口袋、分解数据或权重已经准备完成。

## 验收/缺失策略（继承场景）
- acceptance: 源场景未给出数值判据时，从本次输入绑定；保留对象核验结果与全部尝试、失败和科学结论边界。
- missing_policy: 缺少来源/分解对应关系时保存具体缺项并交资源责任方；不要将 cross-docked 参照改称 native pose 或实验标签，也不要用其他对象代替后沿用原结论。
