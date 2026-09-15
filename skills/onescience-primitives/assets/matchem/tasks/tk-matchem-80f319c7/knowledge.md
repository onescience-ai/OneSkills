# 骨架任务：光电性能与老化响应评估

- domain: matchem
- 复用场景数: 9
- 实例任务数: 9

## 步骤描述（跨场景聚合去重）
- 获取效率、滞后、相稳定性和退化响应。

## 执行 prompt（跨场景聚合去重）
- 用 {CHARACTERIZATION_DATA} 或新测试比较性能和老化，关联界面/缺陷证据。

## 输入槽（var/hint/default）
- {CHARACTERIZATION_DATA} | required=False | type=doc | var_name=表征或器件数据 | hint=J-V、EQE、PL、XRD、XPS 或 | default=optional

## 产出
- 性能与老化数据
- 机制分析

## 质量门禁 quality_gate
- 不以单点效率替代稳定性
- 初始效率和稳定性同时报告

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-04b00219
- it-2b0d0f9a
- it-2b194b95
- it-5d8440d9
- it-7a054bad
- it-ed86c5f7
- it-ef6ff63b
- it-f5a138f0
- it-fc2e4741

## 复用场景
- TiO2CsPbBr3异质结CO2光还原设计
- 二维三维钙钛矿界面长期稳定设计
- 二维钙钛矿实验室机器学习合成
- 倒置钙钛矿晶粒界面配体锚定优化
- 全无机无铅钙钛矿原生氧化物钝化
- 准二维钙钛矿绿光LED相组分钝化优化
- 平面钙钛矿太阳能电池接触钝化优化
- 柔性钙钛矿组件SnO2界面钝化设计
- 钙钛矿太阳能电池氧诱导碘缺陷退化分析
