# 实例任务：结构预测或序列采样 @ B87

- domain: bio
- 骨架: bio-structure-prediction-or-sequence-sampling-task
- 场景: bio-linear-time-rna-secondary-structure-folding-prediction-scenario (B87)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- B87
- 关联论文: LinearFold: linear-time approximate RNA folding by 5'-to-3' dynamic programming and beam search | doi:

## 本实例步骤描述
执行折叠、反向设计或复合物亲和力推理。

## 本实例执行 prompt
运行线性时间RNA二级结构折叠预测，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。

## 本实例输入槽
- {NUM_CANDIDATES} | required=True | type=int | var_name=候选数量 | hint=设置候选结构或序列数 | default=100
- {TEMPERATURE} | required=False | type=float | var_name=采样温度 | hint=控制RNA候选多样性 | default=0.8
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定随机采样结果 | default=31

## 本实例产出
- RNA候选
- 模型得分
- 推理日志

## 本实例质量门禁
- 候选数量达标
- 配对关系可解析
- 输出与输入链一致

## 可调资源（edge:resource，仅真实存在）
- models/alphafold

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
