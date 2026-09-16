# 实例任务：免疫预测或候选生成 @ B28

- domain: bio
- 骨架: bio-immune-prediction-candidate-generation-task
- 场景: bio-affinity-optimized-structure-aware-antibody-inverse-folding-scenario (B28)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- B28
- 关联论文: Structure-Aware Antibody Design with Affinity-Optimized Inverse Folding | doi:

## 本实例步骤描述
执行任务并产生可重复的得分或设计候选。

## 本实例执行 prompt
运行亲和力优化的结构感知抗体反向折叠，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。

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
