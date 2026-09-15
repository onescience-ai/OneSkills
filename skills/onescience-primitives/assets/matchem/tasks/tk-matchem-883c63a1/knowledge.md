# 骨架任务：母体结构检查与掺杂候选建模

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 读取 Li[Ni0.91Co0.09]O2 结构，检查层状堆垛、元素占位和 Li/Ni 位点；按统一比例生成 Mg、Al、Ti、Ta、Mo 掺杂候选，并记录每个替位构型。

## 执行 prompt（跨场景聚合去重）
- 读取 {PARENT_STRUCTURE}，核对 Li、Ni、Co、O 的元素顺序和层状结构；按照 {DOPANT_SET} 与 {DOPANT_RATIO} 生成候选。无法由输入确定的氧化态、电荷补偿或替位位点写 BLOCKED，不得猜测。

## 输入槽（var/hint/default）
- {PARENT_STRUCTURE} | required=True | type=doc | var_name=母体结构文件 | hint=CIF/POSCAR 及来源。 | default={PARENT_STRUCTURE}
- {DOPANT_SET} | required=True | type=list[str] | var_name=掺杂集合 | hint=元素、氧化态和替位位点。 | default={DOPANT_SET}
- {DOPANT_RATIO} | required=True | type=list[float] | var_name=掺杂比例 | hint=统一化学计量定义。 | default={DOPANT_RATIO}

## 产出
- 候选结构 POSCAR/CIF
- 建模日志
- 构型与化学计量清单

## 质量门禁 quality_gate
- 层状母体和掺杂位点可追溯
- 所有候选结构元素守恒且无明显原子重叠
- 电荷补偿未定义时输出 BLOCKED 而非静默假设

## 可调资源（edge:resource，仅真实存在）
- tools/pymatgen

## 实例任务（本骨架在各场景的实例化）
- it-e1f1cb0b

## 复用场景
- LiNiCo_高镍层状正极掺杂结构优化与应变风险分析
