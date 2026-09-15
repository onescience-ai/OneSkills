# 实例任务：微生物预测与聚合 @ B91

- domain: bio
- 骨架: tk-bio-aa67870c
- 场景: sc-30edf759 (B91)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- B91
- 关联论文: CHERRY: a Computational metHod for accuratE pRediction of virus-pRokarYotic interactions using a graph encoder-decoder model | doi:; CLMB: deep contrastive learning for robust metagenomic binning | doi:

## 本实例步骤描述
批量完成分类、分箱、宿主关联或耐药性预测。

## 本实例执行 prompt
以批次{BATCH_SIZE}和种子{SEED}运行噬菌体与原核宿主互作预测，用{DECISION_THRESHOLD}输出序列及样本级结果。

## 本实例输入槽
- {BATCH_SIZE} | required=True | type=int | var_name=批次大小 | hint=设置序列批次大小 | default=64
- {DECISION_THRESHOLD} | required=False | type=float | var_name=判定阈值 | hint=设置阳性判定阈值 | default=0.5
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定聚类或评测结果 | default=29

## 本实例产出
- 序列级预测
- 样本级汇总
- 运行日志

## 本实例质量门禁
- 每条序列有结果
- 聚合规则可复现
- 低置信结果未强制归类

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
