# 骨架任务：免疫预测或候选生成

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 执行任务并产生可重复的得分或设计候选。

## 执行 prompt（跨场景聚合去重）
- 运行CD4 T细胞表位加工与呈递预测，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行CDR环与抗体骨架联合生成，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行亲和力优化的结构感知抗体反向折叠，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行可解释TCR表位特异性预测，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行强化学习引导的抗体亲和力成熟，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行抗体抗原结合位点联合预测，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行抗原条件的全原子抗体从头设计，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行抗原特异性多模态抗体功能设计，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行新冠病毒抗体结合亲和力预测，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行结构检索增强的抗体序列设计，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。

## 输入槽（var/hint/default）
- {NUM_CANDIDATES} | required=True | type=int | var_name=候选数量 | hint=设置候选结果数量 | default=50
- {TEMPERATURE} | required=False | type=float | var_name=采样温度 | hint=控制候选序列多样性 | default=0.3
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定随机采样结果 | default=73

## 产出
- 候选序列或配对
- 推理日志
- 模型得分

## 质量门禁 quality_gate
- 候选数量达标
- 序列字符合法
- 得分与样本一一对应

## 可调资源（edge:resource，仅真实存在）
- models/proteinmpnn

## 实例任务（本骨架在各场景的实例化）
- it-0ed5cd8a
- it-48da641d
- it-6321bfd7
- it-7911c1a0
- it-95317b36
- it-bd4d54d7
- it-ce28ad82
- it-ee7c0378
- it-fb04c860
- it-ffcb89cf

## 复用场景
- B26
- B22
- B28
- B27
- B23
- B25
- B21
- B30
- B29
- B24
