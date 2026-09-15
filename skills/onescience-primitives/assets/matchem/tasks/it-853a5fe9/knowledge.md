# 实例任务：结构或电化学响应获取 @ 固态电池锂沉积原位CT机器学习检测

- domain: matchem
- 骨架: tk-matchem-ed26b503
- 场景: sc-a2ef07e1 (固态电池锂沉积原位CT机器学习检测)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- 固态电池锂沉积原位CT机器学习检测
- 关联论文: Detecting lithium plating dynamics in a solid-state battery with operando X-ray computed tomography using machine learning | doi:

## 本实例步骤描述
执行统一的计算、表征或循环测试。

## 本实例执行 prompt
按 {COMPUTE_OR_TEST_CONFIG} 获取结构演化、容量、阻抗或失效数据，记录版本、命令或仪器校准。

## 本实例输入槽
- {COMPUTE_OR_TEST_CONFIG} | required=False | type=object | var_name=计算或测试配置 | hint=说明软件、仪器、收敛或校准信息。 | default={'mode': 'experiment_or_user_confirmed_simulation'}

## 本实例产出
- 原始响应数据
- 实验/计算日志

## 本实例质量门禁
- 对照样采用同一工况
- 原始数据可追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
