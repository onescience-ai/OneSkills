# 实例任务：性质过滤与候选排序 @ B53

- domain: bio
- 骨架: bio-property-filtering-candidate-ranking-task
- 场景: bio-best-of-k-aligned-target-specific-3d-molecule-generation-scenario (B53)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- B53
- 关联论文: BoKDiff: Best-of-K Diffusion Alignment for Target-Specific 3D Molecule Generation | doi:; TAGMol: Target-Aware Gradient-guided Molecule Generation | doi:
- 核对官方提交 `b3c7da493a13ab3d84b28057748d7c03ab7b0303` 的 [get_chem](https://github.com/khodabandeh-ali/BoKDiff/blob/b3c7da493a13ab3d84b28057748d7c03ab7b0303/utils/evaluation/scoring_func.py)、[compute_sa_score:185–189](https://github.com/khodabandeh-ali/BoKDiff/blob/b3c7da493a13ab3d84b28057748d7c03ab7b0303/utils/evaluation/sascorer.py#L185)、[Vina封装:118–149](https://github.com/khodabandeh-ali/BoKDiff/blob/b3c7da493a13ab3d84b28057748d7c03ab7b0303/utils/evaluation/docking_vina.py#L118)及[评价脚本:241 附近的裁剪](https://github.com/khodabandeh-ali/BoKDiff/blob/b3c7da493a13ab3d84b28057748d7c03ab7b0303/scripts/evaluate_mol_from_meta_full.py#L241)。对照 [Vina Python API](https://autodock-vina.readthedocs.io/en/latest/docking_python.html) 的 receptor/maps、score、optimize、dock 与 pose 接口；运行时固定实际软件版本。
- RDKit 原始 SA 依据 [Contrib/SA_Score/sascorer.py](https://github.com/rdkit/rdkit/blob/master/Contrib/SA_Score/sascorer.py) 的 calculateScore；本次来源缓存 SHA256 为 `8c191920cb9d011994e5f77a0b54924d20d92967052bf6f6903f6f40c0a6e3a2`，不要把浮动 master 当固定运行版本。

## 本实例步骤描述
按对接分数、药物相似性和合成可行性汇总候选。先完成全量尝试的化学审计和去重，对全部唯一有效候选独立评价；将性质筛选保留为单独标记集合，再对符合筛选且对接成功的子集聚类/排序。完整队列与筛选子集分别统计，避免仅评价优选样本造成偏差。

## 本实例执行 prompt
按{PROPERTY_LIMITS}的明确尺度标记性质是否合格，保存全队列结果；在统一受体、准备规则、固定 box、非零随机种子、exhaustiveness 和并行度下独立对接全部唯一有效候选及任务指定的参考/重复对象。仅在符合性质筛选且对接成功的子集中排序，最多保留{TOP_K}个分子；不足或空集时如实交付。不要为凑数量放松阈值或删除失败。

## 本实例输入槽
- {PROPERTY_LIMITS} | required=False | type=object | var_name=性质阈值 | hint=显式给出性质尺度及比较方向；示例sa_max采用原始SA，实际以任务配置为准 | default={'qed_min': 0.6, 'sa_max': 6}
- {TOP_K} | required=False | type=int | var_name=保留分子数 | hint=设置最终保留数量上限 | default=100
- 随评价清单交接受体/配体准备副本及 hash、由参考定义且对全部候选统一的 box center/size（Å）、软件版本、固定非零 seed、exhaustiveness、并行度、重复对象选择规则及预算；这些是运行清单内容，不增加 metadata 槽。

## 本实例产出
- 排序分子集：保留稳定 candidate_id、性质筛选标签、去重/聚类关系和 TOP_K 规则；完整队列及空筛选集仍须报告。
- 对接分数明细：按 candidate_id 与 role（主队列/参考/重复）分开保存 mode、seed、status、error、energy（kcal/mol）和对应 pose 身份/hash。score_only 对原始准备姿势评分，没有新 pose；minimize 保存优化后 pose；dock 保存搜索所得 pose，不能把同一原始 SDF 冒充三种姿势。
- 性质与多样性报告：保存 QED、SA_raw、SA_norm、实现/版本、化学检查、唯一性/多样性、参考比较及不确定度。记录原始指标与全部失败，不把可旋转键数当 SA。
- 计数账本：计划槽位与真实尝试分开；每个真实尝试以失败或有效结果闭合，有效结果再分唯一与重复。分别记录完整有效唯一队列的主对接成功/失败/未完成、性质筛选子集分母与成功/失败/未完成，以及最终可排序数。参考/重复不计入主候选数或主对接成功数；在评价前按任务规则选定重复对象，重复仅支持数值稳定性，不作独立靶点样本。

## 本实例质量门禁
- 对每个结果核对 RDKit sanitize、元素、价态、键级、立体化学、单连通、有限三维坐标及与原始重构的对应；解析成功不代替这些检查。重复结构合并时保留原始尝试映射和任务固定的去重定义。
- 按实际 `get_chem(mol)` 实现记录 QED 与 `sa` 的语义：该版本 `sa` 返回 `SA_norm=round((10-SA_raw)/9,2)`，越大越好；RDKit 原始 SA 通常为 1–10、越小越好。`sa_max` 必须绑定原始尺度或重新明确命名/方向，不能拿归一化值与 raw 阈值比较；保留原始值以便复核舍入边界。
- 核验准备副本、统一受体及固定 box，记录 Å/kcal/mol 单位，不能逐候选改变 box。按任务要求区分 `score()[0]`（score_only）、`optimize()[0]`（minimize）、`dock(...)` 后 `energies(n_poses=1)[0][0]`（dock）；能量越低越好，不以模式名或文件存在代替真实调用。
- 识别官方评价脚本中 `vina_min[i] < -6` 先裁剪再汇总的选择偏差：若沿用该步骤，仅能描述裁剪子集；要报告全队列就保留所有弱样本、失败及未完成，逐个给分母，不能直接把裁剪后的统计当全队列性能。
- 筛选规则和重复设计可复现；同时报告完整队列与筛选子集的性质、对接和多样性，不将参考/重复混入主成功率。计算 QED/SA/Vina 只能提供代理证据，不能证明实验活性、ADMET、可合成性或对齐因果收益。

## 可调资源（edge:resource，仅真实存在）
- models/diffdock：可用于另行需要的学习式姿势预测；其置信度或预测姿势不能替代本任务要求的 Vina score/minimize/dock 能量。当前没有绑定合法 Vina 资源卡时如实记缺项，不编造 resource 边；实际后端准备交现有执行/环境职责。

## 验收/缺失策略（继承场景）
- acceptance: 从本次任务绑定阈值、规模、重复设计及预算，按完整分母报告化学有效性、唯一性、排序、多样性、参考比较和不确定度；不借用其他论文的固定命中阈值。
- missing_policy: 后端不可用、准备失败、超时和缺失能量分别记录；失败不当作零能量，不隐去弱样本，不拿预测亲和或历史结果补本次 Vina 计算。保存健康部分并保持未完成结论。
