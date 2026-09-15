# 实例任务：CO2→CH4 与 HER 竞争路径自由能分析 @ Cu-NxBy_单原子位点CO2到CH4选择性优化

- domain: matchem
- 骨架: tk-matchem-b00fbef2
- 场景: sc-9566751c (Cu-NxBy_单原子位点CO2到CH4选择性优化)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- Cu-NxBy_单原子位点CO2到CH4选择性优化
- 关联论文: Manipulating local coordination of copper single atom catalyst enables efficient CO2-to-CH4 conversion | doi:; The nature of active sites for carbon dioxide electroreduction over oxide-derived copper catalysts | doi:; Isolated copper–tin atomic interfaces tuning electrocatalytic CO2 conversion | doi:

## 本实例步骤描述
以 *COOH、*CO、*CHO 等中间体建立 CO2→CH4 路径，计算电位相关自由能；同时分析 *H/HER 和 CO 脱附竞争，并对关键质子化步骤进行能垒计算或明确缺失。

## 本实例执行 prompt
根据 {ADSORPTION_RESULTS} 和 {ELECTROCHEMICAL_POTENTIAL} 构建 CO2→COOH→CO→CHO→CH4 与 HER 路径；用 {BARRIER_METHOD} 处理关键步骤。区分吸附能、自由能和能垒，缺失项写 MISSING。

## 本实例输入槽
- {ADSORPTION_RESULTS} | required=True | type=doc | var_name=吸附结果 | hint=s02 输出。 | default={ADSORPTION_RESULTS}
- {ELECTROCHEMICAL_POTENTIAL} | required=True | type=float | var_name=电位 | hint=相对于 RHE 的统一参考。 | default={ELECTROCHEMICAL_POTENTIAL}
- {BARRIER_METHOD} | required=False | type=enum | var_name=能垒方法 | hint=若没有过渡态计算能力，不得把热力学自由能 | default=NEB

## 本实例产出
- 反应自由能图
- 限制步骤与选择性竞争分析
- 关键能垒或缺失项清单

## 本实例质量门禁
- 每个自由能修正项、参考电位和温度均有记录
- CH4 选择性结论同时考虑 CO 脱附和 HER 竞争
- 没有能垒结果时不得宣称动力学选择性已被证明

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
