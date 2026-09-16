# 实例任务：成分与结构搜索空间定义 @ 高居里温度二维铁磁材料高通量筛选

- domain: matchem
- 骨架: matchem-composition-structure-search-space-definition-task
- 场景: matchem-high-curie-temperature-2d-ferromagnetic-materials-high-scenario (高居里温度二维铁磁材料高通量筛选)
- step_id: s01
- depend: []

## 场景研究主体
- 高居里温度二维铁磁材料高通量筛选
- 关联论文: High-throughput discovery of high Curie point two-dimensional ferromagnetic materials | doi:

## 本实例步骤描述
建立成分、压力和对称性约束。

## 本实例执行 prompt
根据 {COMPOSITION} 和 {STRUCTURE_CONSTRAINTS} 生成合法搜索空间；不明确的价态或压力边界标记 BLOCKED。

## 本实例输入槽
- {COMPOSITION} | required=True | type=str | var_name=成分与化学计量 | hint=给出元素、比例、价态假设和电荷约束。 | default=目标化学式
- {STRUCTURE_CONSTRAINTS} | required=True | type=object | var_name=结构约束 | hint=空间群、压力、原子数、层状或配位约束。 | default={'pressure_GPa': 0, 'max_atoms': 64}

## 本实例产出
- 搜索空间清单
- 初始构型

## 本实例质量门禁
- 化学计量和电荷约束一致
- 结构约束可复现

## 可调资源（edge:resource，仅真实存在）
- models/strain-tuning-method-for-hbn-quantum-emitters
- tools/molecular-structure-preparation

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
