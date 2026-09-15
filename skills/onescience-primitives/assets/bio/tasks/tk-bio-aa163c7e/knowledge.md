# 骨架任务：候选生成与序列采样

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 生成结构或序列候选并记录随机性参数。

## 执行 prompt（跨场景聚合去重）
- 以温度{TEMPERATURE}和种子{SEED}运行ProToken潜空间蛋白结构序列协同设计，生成{NUM_DESIGNS}个候选。
- 以温度{TEMPERATURE}和种子{SEED}运行全原子蛋白结构与序列联合生成，生成{NUM_DESIGNS}个候选。
- 以温度{TEMPERATURE}和种子{SEED}运行功能位点约束的蛋白骨架生成，生成{NUM_DESIGNS}个候选。
- 以温度{TEMPERATURE}和种子{SEED}运行反应条件驱动的从头酶设计，生成{NUM_DESIGNS}个候选。
- 以温度{TEMPERATURE}和种子{SEED}运行多功能基序支架蛋白生成，生成{NUM_DESIGNS}个候选。
- 以温度{TEMPERATURE}和种子{SEED}运行多构象状态兼容的蛋白序列设计，生成{NUM_DESIGNS}个候选。
- 以温度{TEMPERATURE}和种子{SEED}运行底物口袋约束的酶骨架设计，生成{NUM_DESIGNS}个候选。
- 以温度{TEMPERATURE}和种子{SEED}运行给定蛋白骨架的稳健序列设计，生成{NUM_DESIGNS}个候选。
- 以温度{TEMPERATURE}和种子{SEED}运行跨膜蛋白序列离散扩散设计，生成{NUM_DESIGNS}个候选。
- 以温度{TEMPERATURE}和种子{SEED}运行靶标特异性全原子肽类设计，生成{NUM_DESIGNS}个候选。

## 输入槽（var/hint/default）
- {NUM_DESIGNS} | required=True | type=int | var_name=设计数量 | hint=设置生成候选数量 | default=64
- {TEMPERATURE} | required=False | type=float | var_name=采样温度 | hint=控制采样多样性 | default=0.2
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定随机采样结果 | default=17

## 产出
- 生成日志
- 设计候选
- 采样分数

## 质量门禁 quality_gate
- 候选数量达标
- 固定残基未改变
- 序列与结构长度一致

## 可调资源（edge:resource，仅真实存在）
- models/proteinmpnn
- models/protoken
- models/rfdiffusion

## 实例任务（本骨架在各场景的实例化）
- it-28261598
- it-37e60b3e
- it-5bfb1b2d
- it-c4be9a38
- it-d7fd95fe
- it-daf5466b
- it-dc29baee
- it-ea8d8d40
- it-eb9d1b45
- it-f2bfbcfe

## 复用场景
- B14
- B13
- B11
- B20
- B15
- B18
- B16
- B12
- B19
- B17
