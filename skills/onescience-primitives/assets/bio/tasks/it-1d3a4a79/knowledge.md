# 实例任务：表征与参考数据准备 @ B31

- domain: bio
- 骨架: tk-bio-a4a8bb08
- 场景: sc-3e7ac522 (B31)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- B31
- 关联论文: Fine-tuning Protein Language Models with Deep Mutational Scanning improves Variant Effect Prediction | doi:; AnnoDPO: Protein Functional Annotation Learning with Direct Preference Optimization | doi:; Evolutionary-scale prediction of atomic-level protein structure with a language model | doi:

## 本实例步骤描述
加载权重并构建序列、结构或底物联合表征。

## 本实例执行 prompt
加载{CHECKPOINT}和{REFERENCE_DATA}，将序列裁剪或分块至{MAX_SEQUENCE_LENGTH}并生成联合表征。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=esm1v_t33_650M.pt
- {REFERENCE_DATA} | required=False | type=doc | var_name=参考数据 | hint=参考数据集名称 | default=UniProtKB_2025_01
- {MAX_SEQUENCE_LENGTH} | required=False | type=int | var_name=序列长度上限 | hint=限制模型输入长度 | default=1024

## 本实例产出
- 蛋白表征
- 参考标签映射
- 预处理日志

## 本实例质量门禁
- 权重加载成功
- 序列分块可回溯
- 参考标签无重复冲突

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
