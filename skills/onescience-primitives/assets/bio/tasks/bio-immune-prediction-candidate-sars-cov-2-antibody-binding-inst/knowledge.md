# 实例任务：免疫预测或候选生成 @ B29

- domain: bio
- 骨架: bio-immune-prediction-candidate-generation-task
- 场景: bio-sars-cov-2-antibody-binding-affinity-prediction-scenario (B29)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- B29
- 关联论文: AbAffinity: A Large Language Model for Predicting Antibody Binding Affinity against SARS-CoV-2 | doi:

## 本实例步骤描述
执行任务并产生可重复的得分或设计候选。

## 本实例执行 prompt
运行新冠病毒抗体结合亲和力预测，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。

## 本实例输入槽
- {NUM_CANDIDATES} | required=True | type=int | var_name=候选数量 | hint=设置候选结果数量 | default=50
- {TEMPERATURE} | required=False | type=float | var_name=采样温度 | hint=控制候选序列多样性 | default=0.3
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定随机采样结果 | default=73

## 本实例产出
- 候选序列或配对
- 模型得分
- 推理日志

## 本实例质量门禁
- 候选数量达标
- 序列字符合法
- 得分与样本一一对应

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
