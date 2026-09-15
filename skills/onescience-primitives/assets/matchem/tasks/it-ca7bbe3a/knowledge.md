# 实例任务：Cu-N4 基底与局域配位构型生成 @ Cu-NxBy_单原子位点CO2到CH4选择性优化

- domain: matchem
- 骨架: tk-matchem-df4123d6
- 场景: sc-9566751c (Cu-NxBy_单原子位点CO2到CH4选择性优化)
- step_id: s01
- depend: []

## 场景研究主体
- Cu-NxBy_单原子位点CO2到CH4选择性优化
- 关联论文: Manipulating local coordination of copper single atom catalyst enables efficient CO2-to-CH4 conversion | doi:; The nature of active sites for carbon dioxide electroreduction over oxide-derived copper catalysts | doi:; Isolated copper–tin atomic interfaces tuning electrocatalytic CO2 conversion | doi:

## 本实例步骤描述
读取 Cu-N4 单原子催化剂结构，保持 Cu 原子孤立，按 Cu-NxBy 候选替换第一配位层中的 N/B 并生成统一表面模型。

## 本实例执行 prompt
读取 {CATALYST_STRUCTURE}，生成 {COORDINATION_SET}；核对 Cu 是否为孤立位点、周期边界是否引入非目标 Cu-Cu 相互作用以及每个候选的电荷/自旋设定。无法确认的构型写 BLOCKED。

## 本实例输入槽
- {CATALYST_STRUCTURE} | required=True | type=doc | var_name=基底结构 | hint=CIF/POSCAR 及活性位说明。 | default={CATALYST_STRUCTURE}
- {COORDINATION_SET} | required=True | type=list[str] | var_name=配位候选 | hint=Cu-NxBy 构型列表。 | default={COORDINATION_SET}

## 本实例产出
- 配位候选 POSCAR
- 局域配位与电荷/自旋清单
- 构型检查日志

## 本实例质量门禁
- 每个候选只有定义内的第一配位层变化
- Cu 单原子孤立性和表面真空层满足设定
- 所有候选的超胞、表面取向和边界条件一致

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
