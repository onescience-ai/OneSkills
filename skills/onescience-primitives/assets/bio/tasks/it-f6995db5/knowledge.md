# 实例任务：口袋与模型特征准备 @ B43

- domain: bio
- 骨架: tk-bio-5f2ccf72
- 场景: sc-fe5c3f01 (B43)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- B43
- 关联论文: FlowDock: Geometric Flow Matching for Generative Protein-Ligand Docking and Affinity Prediction | doi:; DeltaDock: A Unified Framework for Accurate, Efficient, and Physically Reliable Molecular Docking | doi:

## 本实例步骤描述
加载权重并定义口袋中心、范围和图特征。

## 本实例执行 prompt
加载{CHECKPOINT}，围绕{POCKET_CENTER}和{POCKET_RADIUS}构建口袋及蛋白配体图特征。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=flowdock.ckpt
- {POCKET_CENTER} | required=False | type=list[float] | var_name=口袋中心 | hint=填写三维中心坐标 | default=[0, 0, 0]
- {POCKET_RADIUS} | required=False | type=float | var_name=口袋半径 | hint=设置口袋搜索半径 | default=12

## 本实例产出
- 口袋定义
- 蛋白配体特征
- 模型加载记录

## 本实例质量门禁
- 中心包含有效坐标
- 口袋残基非空
- 配体拓扑保持

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
