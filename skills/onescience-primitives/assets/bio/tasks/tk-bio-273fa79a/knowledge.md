# 骨架任务：结构预测或序列采样

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 执行折叠、反向设计或复合物亲和力推理。

## 执行 prompt（跨场景聚合去重）
- 运行RNA三维靶结构的群智能反向折叠，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行低数据RNA三级结构条件序列设计，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行几何深度学习驱动的RNA三维反向设计，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行双向锚定的结构条件RNA序列生成，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行大卷积核RNA二级结构预测，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行深度序列模型的miRNA靶标预测，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行线性时间RNA二级结构折叠预测，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行结构序列编码多约束的RNA设计，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行蛋白质RNA复合物结合亲和力预测，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。
- 运行语言模型驱动的RNA三维结构预测，以温度{TEMPERATURE}和种子{SEED}生成或排序{NUM_CANDIDATES}个候选。

## 输入槽（var/hint/default）
- {NUM_CANDIDATES} | required=True | type=int | var_name=候选数量 | hint=设置候选结构或序列数 | default=100
- {TEMPERATURE} | required=False | type=float | var_name=采样温度 | hint=控制RNA候选多样性 | default=0.8
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定随机采样结果 | default=31

## 产出
- RNA候选
- 推理日志
- 模型得分

## 质量门禁 quality_gate
- 候选数量达标
- 输出与输入链一致
- 配对关系可解析

## 可调资源（edge:resource，仅真实存在）
- models/alphafold
- models/proteinmpnn

## 实例任务（本骨架在各场景的实例化）
- it-13dc356f
- it-21581d65
- it-24fdfa8c
- it-4a7dcf7d
- it-4edb02d5
- it-526903d7
- it-654b9331
- it-6bf5d3dd
- it-c640ad31
- it-f85d10f5

## 复用场景
- B83
- B90
- B85
- B82
- B86
- B88
- B87
- B84
- B89
- B81
