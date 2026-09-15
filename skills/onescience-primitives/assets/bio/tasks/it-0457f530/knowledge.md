# 实例任务：基因组输入与坐标规范化 @ B64

- domain: bio
- 骨架: tk-bio-7dcdc00a
- 场景: sc-9c3a83c8 (B64)
- step_id: s01
- depend: []

## 场景研究主体
- B64
- 关联论文: Caduceus: Bi-Directional Equivariant Long-Range DNA Sequence Modeling | doi:; DNABERT-2: Efficient Foundation Model and Benchmark For Multi-Species Genome | doi:

## 本实例步骤描述
读取双向等变长程DNA序列建模的DNA、区间、变异或表观信号。

## 本实例执行 prompt
读取{GENOMICS_INPUT}，相对{REFERENCE_GENOME}校验序列和坐标，使用{MODEL_NAME}建立双向等变长程DNA序列建模任务。

## 本实例输入槽
- {GENOMICS_INPUT} | required=True | type=doc | var_name=基因组输入 | hint=输入序列区间或变异 | default=long_dna_windows.fasta
- {MODEL_NAME} | required=True | type=enum | var_name=基因组模型 | hint=选择场景使用的模型 | default=Caduceus
- {REFERENCE_GENOME} | required=False | type=enum | var_name=参考基因组 | hint=选择坐标参考版本 | default=hg38

## 本实例产出
- 标准化基因组输入
- 坐标检查报告
- 任务配置

## 本实例质量门禁
- 坐标位于参考范围
- 等位基因方向一致
- 样本标识唯一

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
