# 骨架任务：CO2→CH4 与 HER 竞争路径自由能分析

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 以 *COOH、*CO、*CHO 等中间体建立 CO2→CH4 路径，计算电位相关自由能；同时分析 *H/HER 和 CO 脱附竞争，并对关键质子化步骤进行能垒计算或明确缺失。

## 执行 prompt（跨场景聚合去重）
- 根据 {ADSORPTION_RESULTS} 和 {ELECTROCHEMICAL_POTENTIAL} 构建 CO2→COOH→CO→CHO→CH4 与 HER 路径；用 {BARRIER_METHOD} 处理关键步骤。区分吸附能、自由能和能垒，缺失项写 MISSING。

## 输入槽（var/hint/default）
- {ADSORPTION_RESULTS} | required=True | type=doc | var_name=吸附结果 | hint=s02 输出。 | default={ADSORPTION_RESULTS}
- {ELECTROCHEMICAL_POTENTIAL} | required=True | type=float | var_name=电位 | hint=相对于 RHE 的统一参考。 | default={ELECTROCHEMICAL_POTENTIAL}
- {BARRIER_METHOD} | required=False | type=enum | var_name=能垒方法 | hint=若没有过渡态计算能力，不得把热力学自由能 | default=NEB

## 产出
- 关键能垒或缺失项清单
- 反应自由能图
- 限制步骤与选择性竞争分析

## 质量门禁 quality_gate
- CH4 选择性结论同时考虑 CO 脱附和 HER 竞争
- 每个自由能修正项、参考电位和温度均有记录
- 没有能垒结果时不得宣称动力学选择性已被证明

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-9751efc5

## 复用场景
- Cu-NxBy_单原子位点CO2到CH4选择性优化
