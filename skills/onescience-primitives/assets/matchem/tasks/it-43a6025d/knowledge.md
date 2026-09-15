# 实例任务：候选结构生成与去重 @ 高居里温度二维铁磁材料高通量筛选

- domain: matchem
- 骨架: tk-matchem-244aa1a4
- 场景: sc-578b061d (高居里温度二维铁磁材料高通量筛选)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- 高居里温度二维铁磁材料高通量筛选
- 关联论文: High-throughput discovery of high Curie point two-dimensional ferromagnetic materials | doi:

## 本实例步骤描述
生成多样候选构型并去除等价结构。

## 本实例执行 prompt
在 {STRUCTURE_CONSTRAINTS} 内生成并去重候选，保留生成器、种子和对称性信息。

## 本实例输入槽
- {STRUCTURE_CONSTRAINTS} | required=True | type=object | var_name=结构约束 | hint=空间群、压力、原子数、层状或配位约束。 | default={'pressure_GPa': 0, 'max_atoms': 64}

## 本实例产出
- 候选结构库
- 去重日志

## 本实例质量门禁
- 无原子重叠
- 等价结构不重复计数

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
