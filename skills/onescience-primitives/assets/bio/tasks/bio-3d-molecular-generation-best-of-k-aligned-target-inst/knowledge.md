# 实例任务：三维分子生成与采样 @ B53

- domain: bio
- 骨架: bio-3d-molecular-generation-sampling-task
- 场景: bio-best-of-k-aligned-target-specific-3d-molecule-generation-scenario (B53)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- B53
- 关联论文: BoKDiff: Best-of-K Diffusion Alignment for Target-Specific 3D Molecule Generation | doi:; TAGMol: Target-Aware Gradient-guided Molecule Generation | doi:
- 以官方提交 `b3c7da493a13ab3d84b28057748d7c03ab7b0303` 的 [sample_diffusion_decomp.py:421–462、465–618](https://github.com/khodabandeh-ali/BoKDiff/blob/b3c7da493a13ab3d84b28057748d7c03ab7b0303/scripts/sample_diffusion_decomp.py#L421) 与 [sampling_drift.yml](https://github.com/khodabandeh-ali/BoKDiff/blob/b3c7da493a13ab3d84b28057748d7c03ab7b0303/configs/sampling_drift.yml)核对生效参数和逐样本返回结构；参考配置不构成当前资源的吞吐证明。

## 本实例步骤描述
生成分子拓扑和构象并记录随机性参数。

1. 接收前序已核验的模型、数据 manifest 与特征契约，运行 `scripts/sample_diffusion_decomp.py` 的实际版本。将{SEED}映射到 `sample.seed` 并调用入口的 `seed_all`，将{NUM_MOLECULES}映射到 `sample.num_samples`；从任务清单固定步数和先验，记录所有生效值及其 CLI/config 来源。
2. 参考 YAML 写有 `sample.gen_mode=complete`、`sample.prior_mode=ref_prior`、`sample.num_steps=1000`、`center_pos_mode=protein`、`sample_num_atoms=prior` 及 `energy_drift`。逐项沿入口验证是否真的消费：先验可被 `--prior_mode` 覆盖；实际原子数模式来自 `--num_atoms_mode`（beta_prior 分支用 `--bp_num_atoms_mode`），不能把 YAML 的 `sample_num_atoms` 当作生效证据。该调用未显式传递 `sample.gen_mode`，须核对实际函数默认/实现是否满足 complete 要求。
3. 核对 `sample.num_steps`、`center_pos_mode`、arms/scaffold 原子数配置与 `energy_drift` 传入采样函数；记录受体中心化及返回坐标恢复关系，禁止生成物与受体分别平移后直接对接。`--batch_size` 与 `--device` 控制实际批量和设备，调整资源参数时保留科学条件、规模与预算。
4. 按返回列表的原始索引保存每个真实尝试，再重构候选 SDF；失败、重复和约束不满足都留痕。输出为空时区分未执行和执行后无有效分子，不用计划数量、空 SDF 或占位文件证明已采样。

## 本实例执行 prompt
运行Best-of-K对齐的靶标特异性三维分子生成，以种子{SEED}和本次生效配置尝试生成{NUM_MOLECULES}个分子及三维构象。只有选定入口实际支持温度时才映射{TEMPERATURE}；上述官方入口没有此参数，标记不适用，不强传或声称已生效。保存实际调用、原始逐样本预测与后处理关联。

## 本实例输入槽
- {NUM_MOLECULES} | required=True | type=int | var_name=生成分子数 | hint=设置生成候选数量 | default=1000
- {TEMPERATURE} | required=False | type=float | var_name=采样温度 | hint=仅实际入口支持时使用；本官方入口不适用 | default=1
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定随机采样结果 | default=42

## 本实例产出
- 候选分子SDF：按稳定 sample_id/candidate_id 交付；记录重复关联与失败，不将失败伪造为成功文件。
- 生成轨迹：保留官方返回的 `mol/smiles`、`pred_pos/pred_v`、`pred_pos_traj/pred_v_traj`、`decomp_mask`，以及启用键扩散/重构所需的 `pred_bond_index/pred_bond_type`；`mol=None` 时仍保留原始索引、预测及重构错误。不要假设该返回包含额外键轨迹或分数键。
- 模型分数：仅保存实际产生且定义明确的分数，没有该输出时注明不适用。
- 逐尝试表：记录 seed、sample_id、raw_path、raw_index、SDF 或 error/status/duplicate_of，并分别统计计划槽位、真实尝试、可解析、有效和唯一分子；保留有效配置、设备、批量、耗时与预算用量，交给评价消费者。

## 本实例质量门禁
- 按本次规模条件分别核对真实尝试数与有效唯一数，不把默认样本数或计划未执行槽位算作生成成功。
- 检查 `pred_pos` 为 `[n_atoms,3]` 且全部有限，`pred_v` 长度与原子数一致；按加载阶段的模式核对原子类别、键索引/键型、decomp_mask 和轨迹维度。
- 每个分子须可解析并进入后续完整化学检查；以 seed/sample_id/raw_path/raw_index 追溯 SDF、失败和重复，核对生成坐标与受体的同一坐标系。

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: 从任务清单固定数量、时间和完整性条件；1000 步只是该版本参考配置，不推断任意设备能在预算内达标。
- missing_policy: 按真实资源选择批量/设备并记录耗时；不足时保存健康部分原始产物及未完成槽位，不改小验收规模后宣称完成，不重用历史预测充数。
