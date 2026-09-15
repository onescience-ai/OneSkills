# 骨架任务：Cu-N4 基底与局域配位构型生成

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 读取 Cu-N4 单原子催化剂结构，保持 Cu 原子孤立，按 Cu-NxBy 候选替换第一配位层中的 N/B 并生成统一表面模型。

## 执行 prompt（跨场景聚合去重）
- 读取 {CATALYST_STRUCTURE}，生成 {COORDINATION_SET}；核对 Cu 是否为孤立位点、周期边界是否引入非目标 Cu-Cu 相互作用以及每个候选的电荷/自旋设定。无法确认的构型写 BLOCKED。

## 输入槽（var/hint/default）
- {CATALYST_STRUCTURE} | required=True | type=doc | var_name=基底结构 | hint=CIF/POSCAR 及活性位说明。 | default={CATALYST_STRUCTURE}
- {COORDINATION_SET} | required=True | type=list[str] | var_name=配位候选 | hint=Cu-NxBy 构型列表。 | default={COORDINATION_SET}

## 产出
- 局域配位与电荷/自旋清单
- 构型检查日志
- 配位候选 POSCAR

## 质量门禁 quality_gate
- Cu 单原子孤立性和表面真空层满足设定
- 所有候选的超胞、表面取向和边界条件一致
- 每个候选只有定义内的第一配位层变化

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-ca7bbe3a

## 复用场景
- Cu-NxBy_单原子位点CO2到CH4选择性优化
