# 实例任务：光电性能与老化响应评估 @ 全无机无铅钙钛矿原生氧化物钝化

- domain: matchem
- 骨架: tk-matchem-80f319c7
- 场景: sc-5e441f98 (全无机无铅钙钛矿原生氧化物钝化)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- 全无机无铅钙钛矿原生氧化物钝化
- 关联论文: Highly stable and efficient all-inorganic lead-free perovskite solar cells with native-oxide passivation | doi:

## 本实例步骤描述
获取效率、滞后、相稳定性和退化响应。

## 本实例执行 prompt
用 {CHARACTERIZATION_DATA} 或新测试比较性能和老化，关联界面/缺陷证据。

## 本实例输入槽
- {CHARACTERIZATION_DATA} | required=False | type=doc | var_name=表征或器件数据 | hint=J-V、EQE、PL、XRD、XPS 或 | default=optional

## 本实例产出
- 性能与老化数据
- 机制分析

## 本实例质量门禁
- 初始效率和稳定性同时报告
- 不以单点效率替代稳定性

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
