# 实例任务：吸附与反应响应获取 @ 金属氮掺杂碳CO2电还原选择性设计

- domain: matchem
- 骨架: tk-matchem-3b811623
- 场景: sc-f53d0708 (金属氮掺杂碳CO2电还原选择性设计)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- 金属氮掺杂碳CO2电还原选择性设计
- 关联论文: Understanding activity and selectivity of metal-nitrogen-doped carbon catalysts for electrochemical reduction of CO2 | doi:

## 本实例步骤描述
计算或测量关键中间体、速率和选择性。

## 本实例执行 prompt
按 {CALCULATION_CONFIG} 获取吸附、自由能、能垒或实验性能，保留参考态和校准信息。

## 本实例输入槽
- {CALCULATION_CONFIG} | required=False | type=object | var_name=计算或表征配置 | hint=如采用 DFT，记录软件、泛函、溶剂、电 | default={'method': 'experiment_or_user_confirmed_simulation'}

## 本实例产出
- 原始计算/实验数据
- 关键中间体响应

## 本实例质量门禁
- 吸附能、自由能和能垒不混用
- 基准与对照齐全

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
