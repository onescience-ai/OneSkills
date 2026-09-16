# 实例任务：性质过滤与候选排序 @ B53

- domain: bio
- 骨架: bio-property-filtering-candidate-ranking-task
- 场景: bio-best-of-k-aligned-target-specific-3d-molecule-generation-scenario (B53)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- B53
- 关联论文: BoKDiff: Best-of-K Diffusion Alignment for Target-Specific 3D Molecule Generation | doi:; TAGMol: Target-Aware Gradient-guided Molecule Generation | doi:

## 本实例步骤描述
按对接分数、药物相似性和合成可行性汇总候选。

## 本实例执行 prompt
用{PROPERTY_LIMITS}过滤候选，计算对接分数并进行去重聚类，最终保留前{TOP_K}个分子。

## 本实例输入槽
- {PROPERTY_LIMITS} | required=False | type=object | var_name=性质阈值 | hint=设置分子性质过滤阈值 | default={'qed_min': 0.6, 'sa_max': 6}
- {TOP_K} | required=False | type=int | var_name=保留分子数 | hint=设置最终保留数量 | default=100

## 本实例产出
- 排序分子集
- 对接分数明细
- 性质与多样性报告

## 本实例质量门禁
- 入选分子通过化学检查
- 重复结构已合并
- 筛选规则可复现

## 可调资源（edge:resource，仅真实存在）
- models/diffdock

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
