# 实例任务：吸附与反应响应获取 @ 分子金属界面CO2到乙醇催化设计

- domain: matchem
- 骨架: matchem-adsorption-reaction-response-acquisition-task
- 场景: matchem-molecular-metal-interface-co2-to-ethanol-catalysis-design-scenario (分子金属界面CO2到乙醇催化设计)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- 分子金属界面CO2到乙醇催化设计
- 关联论文: Cooperative CO2-to-ethanol conversion via enriched intermediates at molecule–metal catalyst interfaces | doi:

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
- models/dft-calculation-of-defect-formation-energy

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
