# 实例任务：分子动力学或结构探索验证 @ 可极化长程相互作用基础机器学习势

- domain: matchem
- 骨架: tk-matchem-22341fb8
- 场景: sc-c776f8d6 (可极化长程相互作用基础机器学习势)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- 可极化长程相互作用基础机器学习势
- 关联论文: A foundation machine learning potential with polarizable long-range interactions for materials modelling | doi:

## 本实例步骤描述
在目标条件下进行短程验证和失效分析。

## 本实例执行 prompt
按 {MD_CONFIG} 进行验证；将势函数不稳定、非物理结构或适用域外结果标记 REJECT/BLOCKED。

## 本实例输入槽
- {MD_CONFIG} | required=False | type=object | var_name=分子动力学验证配置 | hint=温度、压力、时间步、体系尺寸和参考计算。 | default={'temperature_K': 300, 'steps': 10000}

## 本实例产出
- MD/探索轨迹
- 适用域结论
- PASS/REJECT/BLOCKED

## 本实例质量门禁
- 不把势函数置信度当作量子或实验验证
- 软件版本和命令完整

## 可调资源（edge:resource，仅真实存在）
- models/mace

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
