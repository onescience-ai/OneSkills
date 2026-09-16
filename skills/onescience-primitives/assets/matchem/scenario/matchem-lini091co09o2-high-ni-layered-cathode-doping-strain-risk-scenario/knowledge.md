# 场景：LiNiCo_高镍层状正极掺杂结构优化与应变风险分析

- domain: matchem
- type: paper_scenario
- 算力: ['VASP'] (is_one_hpc=[True])
- 模型: ['NULL']
- 工具: []

## 研究意图（agent_task_prompt）
你是材料化学研究负责人。请围绕“Li[Ni0.91Co0.09]O2 高镍层状正极的掺杂结构优化与应变风险分析”完成一项可复现、可审计的研究任务。场景需求如下：针对 Li[Ni0.91Co0.09]O2 高镍层状正极，比较 Mg/Al/Ti/Ta/Mo 掺杂在深度脱锂和高电压下的 Li/Ni 混排、结构稳定性及应变/开裂风险；论文未涉及 OneModels 模型，模型按 NULL 处理。。请先核对用户提供的研究对象、边界条件、已有资料、可用资源和交付位置，明确哪些信息已经具备、哪些仍需确认；再自主提出合理的理论或实验计算路线、模型与软件选择、数据来源、验证方法、资源估算、质量门禁、风险和替代方案。不得将关联论文、历史案例、默认参数或未验证结果视为本次任务的结果；涉及科学范围、预算、关键约束或验收标准的选择须先请求确认。执行后应保留可追溯证据链，交付结果、数据来源、不确定度、适用性限制、复现材料及未完成项；每项交付均以 PASS、PARTIAL、REJECT 或 BLOCKED 标记。

## 客户端请求
- task_title: Li[Ni0.91Co0.09]O2 高镍层状正极的掺杂结构优化与应变风险分析
- request: 针对 Li[Ni0.91Co0.09]O2 高镍层状正极，比较 Mg/Al/Ti/Ta/Mo 掺杂在深度脱锂和高电压下的 Li/Ni 混排、结构稳定性及应变/开裂风险；论文未涉及 OneModels 模型，模型按 NULL 处理。
- scientific_context: 本场景从关联论文提炼为可直接执行的具体材料化学任务；关联论文用于理解背景和核验依据，不替代本次任务的数据与结论。
- desired_outcome: 获得可复现、可审计的研究结果，并明确结果证据、适用范围、不确定度和不能得出的结论。
- executor_role: 执行者应具备材料化学研究、数据分析和计算任务设计能力，能够将需求转化为经确认的可执行方案，并主动识别缺失信息和风险。

## 问题与适用性
本对象是提交给材料化学执行者的完整需求书，只规定研究目标、约束、预期结果和验收口径；执行者自主设计实施方案并在开工前说明风险。

## 工作流步骤（→workflow/→tasks）
- s01 母体结构检查与掺杂候选建模
- s02 不同脱锂状态下的 VASP 结构弛豫
- s03 Li/Ni 混排与结构稳定性计算
- s04 弹性与开裂风险代理指标分析
- s05 候选排序与实验/文献交叉验证

## 关联论文
- Transition metal-doped Ni-rich layered cathode materials for durable Li-ion batteries | doi:
- Additive engineering for robust interphases to stabilize high-Ni layered structures at ultra-high voltage of 4.8 V | doi:
- High-nickel layered oxide cathodes for lithium-based automotive batteries | doi:
- Origin of structural degradation in Li-rich layered oxide cathode | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
