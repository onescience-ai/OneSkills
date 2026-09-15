# 骨架任务：三维分子生成与采样

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 生成分子拓扑和构象并记录随机性参数。

## 执行 prompt（跨场景聚合去重）
- 运行Best-of-K对齐的靶标特异性三维分子生成，以温度{TEMPERATURE}和种子{SEED}生成{NUM_MOLECULES}个分子及三维构象。
- 运行SMILES基础模型驱动的ADMET性质预测，以温度{TEMPERATURE}和种子{SEED}生成{NUM_MOLECULES}个分子及三维构象。
- 运行一维语言与三维扩散融合的分子生成，以温度{TEMPERATURE}和种子{SEED}生成{NUM_MOLECULES}个分子及三维构象。
- 运行亲和力梯度引导的口袋条件分子生成，以温度{TEMPERATURE}和种子{SEED}生成{NUM_MOLECULES}个分子及三维构象。
- 运行全原子流匹配的三维小分子从头生成，以温度{TEMPERATURE}和种子{SEED}生成{NUM_MOLECULES}个分子及三维构象。
- 运行分子潜空间扩散进化与多位点抑制剂设计，以温度{TEMPERATURE}和种子{SEED}生成{NUM_MOLECULES}个分子及三维构象。
- 运行合成路线约束的GFlowNet分子生成，以温度{TEMPERATURE}和种子{SEED}生成{NUM_MOLECULES}个分子及三维构象。
- 运行多任务靶点感知的三维分子生成，以温度{TEMPERATURE}和种子{SEED}生成{NUM_MOLECULES}个分子及三维构象。
- 运行形状静电药效团联合的生物电子等排体设计，以温度{TEMPERATURE}和种子{SEED}生成{NUM_MOLECULES}个分子及三维构象。
- 运行正负活性联合引导的靶向小分子生成，以温度{TEMPERATURE}和种子{SEED}生成{NUM_MOLECULES}个分子及三维构象。

## 输入槽（var/hint/default）
- {NUM_MOLECULES} | required=True | type=int | var_name=生成分子数 | hint=设置生成候选数量 | default=1000
- {TEMPERATURE} | required=False | type=float | var_name=采样温度 | hint=控制生成分布宽度 | default=1
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定随机采样结果 | default=42

## 产出
- 候选分子SDF
- 模型分数
- 生成轨迹

## 质量门禁 quality_gate
- 原子坐标为有限值
- 每个分子可被化学解析
- 生成数量达标

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-0e083170
- it-17bf03c7
- it-1bda47fe
- it-3c8405be
- it-477c7484
- it-8ac379a4
- it-9e10a9b6
- it-a13d8edb
- it-ab6bee19
- it-cde78fcf

## 复用场景
- B53
- B56
- B57
- B54
- B59
- B52
- B58
- B60
- B55
- B51
