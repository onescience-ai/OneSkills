# 实例任务：候选生成与序列采样 @ B18

- domain: bio
- 骨架: tk-bio-aa163c7e
- 场景: sc-f1675b8c (B18)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- B18
- 关联论文: Multi-state Protein Design with DynamicMPNN | doi:

## 本实例步骤描述
生成结构或序列候选并记录随机性参数。

## 本实例执行 prompt
以温度{TEMPERATURE}和种子{SEED}运行多构象状态兼容的蛋白序列设计，生成{NUM_DESIGNS}个候选。

## 本实例输入槽
- {NUM_DESIGNS} | required=True | type=int | var_name=设计数量 | hint=设置生成候选数量 | default=64
- {TEMPERATURE} | required=False | type=float | var_name=采样温度 | hint=控制采样多样性 | default=0.2
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定随机采样结果 | default=17

## 本实例产出
- 设计候选
- 采样分数
- 生成日志

## 本实例质量门禁
- 候选数量达标
- 固定残基未改变
- 序列与结构长度一致

## 可调资源（edge:resource，仅真实存在）
- models/proteinmpnn

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
