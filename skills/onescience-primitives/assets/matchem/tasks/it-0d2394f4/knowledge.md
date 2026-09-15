# 实例任务：材料与工况建模 @ 商用锂离子电池电压松弛容量估计

- domain: matchem
- 骨架: tk-matchem-45bbfe0b
- 场景: sc-e4726f15 (商用锂离子电池电压松弛容量估计)
- step_id: s01
- depend: []

## 场景研究主体
- 商用锂离子电池电压松弛容量估计
- 关联论文: Data-driven capacity estimation of commercial lithium-ion batteries from voltage relaxation | doi:

## 本实例步骤描述
核对材料组成、初始状态和电池工况。

## 本实例执行 prompt
读取 {MATERIAL_STRUCTURE} 与 {CELL_CONDITION}；明确满锂/脱锂状态、对照样和失效判据。

## 本实例输入槽
- {MATERIAL_STRUCTURE} | required=True | type=doc | var_name=电极或电解质材料信息 | hint=结构文件、组成、粒径或配方及来源。 | default=CIF/POSCAR/配方表
- {CELL_CONDITION} | required=True | type=object | var_name=电池工况 | hint=电压窗口、倍率、温度、负载量和循环数。 | default={'voltage_window_V': [2.8, 4.5], 'temperature_C': 25}

## 本实例产出
- 材料与工况清单
- 初始状态记录

## 本实例质量门禁
- 材料化学计量和电压参考明确
- 缺失电解液或对电极信息时标记 BLOCKED

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
