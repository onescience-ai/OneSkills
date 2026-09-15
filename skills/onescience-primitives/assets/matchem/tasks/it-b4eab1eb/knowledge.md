# 实例任务：吸附构型搜索与 VASP 弛豫 @ Cu-NxBy_单原子位点CO2到CH4选择性优化

- domain: matchem
- 骨架: tk-matchem-0c043f0d
- 场景: sc-9566751c (Cu-NxBy_单原子位点CO2到CH4选择性优化)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- Cu-NxBy_单原子位点CO2到CH4选择性优化
- 关联论文: Manipulating local coordination of copper single atom catalyst enables efficient CO2-to-CH4 conversion | doi:; The nature of active sites for carbon dioxide electroreduction over oxide-derived copper catalysts | doi:; Isolated copper–tin atomic interfaces tuning electrocatalytic CO2 conversion | doi:

## 本实例步骤描述
对 CO2、COOH*、CO*、CHO* 和 H* 在每个 Cu-NxBy 位点枚举合理吸附姿态，使用统一 VASP 设置弛豫并计算吸附能。

## 本实例执行 prompt
使用 VASP 按 {DFT_CONFIG} 对 {COORDINATION_STRUCTURES} 上的 {INTERMEDIATE_SET} 枚举并弛豫吸附构型；保留最低能和近简并构型，记录吸附能、键长、配位变化和收敛信息。

## 本实例输入槽
- {COORDINATION_STRUCTURES} | required=True | type=doc | var_name=配位结构集合 | hint=s01 输出。 | default={COORDINATION_STRUCTURES}
- {INTERMEDIATE_SET} | required=True | type=list[str] | var_name=中间体集合 | hint=反应路径和 HER 对照。 | default={INTERMEDIATE_SET}
- {DFT_CONFIG} | required=True | type=object | var_name=DFT 设置 | hint=统一的 VASP 参数。 | default={DFT_CONFIG}

## 本实例产出
- 弛豫后吸附结构
- 吸附能与关键键长表
- 电子结构/电荷分析输入

## 本实例质量门禁
- 每个候选和中间体至少有可解释的吸附构型搜索记录
- 吸附能参考态、真空层、覆盖度和自旋设置一致
- 近简并构型未被无记录地丢弃

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
