# 实例任务：成分与结构搜索空间定义 @ 钙钛矿氧化物与卤化物容忍因子稳定性筛选

- domain: matchem
- 骨架: tk-matchem-85bf1af1
- 场景: sc-89a7da1c (钙钛矿氧化物与卤化物容忍因子稳定性筛选)
- step_id: s01
- depend: []

## 场景研究主体
- 钙钛矿氧化物与卤化物容忍因子稳定性筛选
- 关联论文: New tolerance factor to predict the stability of perovskite oxides and halides | doi:

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
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
