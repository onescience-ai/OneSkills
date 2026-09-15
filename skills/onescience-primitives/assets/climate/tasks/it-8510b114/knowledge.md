# 实例任务：执行时空插值或物理约束迁移重建 @ E13

- domain: climate
- 骨架: tk-climate-94c82a8e
- 场景: sc-697ebcbc (E13)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E13
- 关联论文: A comparative assessment of the uncertainties of global surface ocean CO 2 estimates using a machine-learning ensemble (CSIR-ML6 version 2019a) – have we hit the wall? | doi:; Global high-resolution monthly p CO 2 climatology for the coastal ocean derived from neural network interpolation | doi:; Spatiotemporal upscaling of sparse air-sea pCO2 data via physics-informed transfer learning | doi:

## 本实例步骤描述
按冻结配置执行“执行时空插值或物理约束迁移重建”，完成从稀疏海气pCO2观测、海温、盐度和生物地球化学辅助场到连续pCO2格点场及不确定性的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RECONSTRUCTION_CONFIG}、{OUTPUT_RESOLUTION}、{UNCERTAINTY_CONFIG}执行执行时空插值或物理约束迁移重建，将稀疏海气pCO2观测、海温、盐度和生物地球化学辅助场转换为连续pCO2格点场及不确定性。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RECONSTRUCTION_CONFIG} | required=True | type=str | var_name=重建配置 | hint=输入缺口重建配置。 | default=None
- {OUTPUT_RESOLUTION} | required=True | type=str | var_name=输出分辨率 | hint=输入输出分辨率。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 本实例产出
- 执行时空插值或物理约束迁移重建结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 观测位置保持原值且缺口结果无拼接突变

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
