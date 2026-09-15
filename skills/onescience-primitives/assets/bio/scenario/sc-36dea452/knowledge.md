# 场景：B02

- domain: bio
- type: paper_scenario
- 算力: ['HMMER', 'HH-suite', 'Kalign', 'MMseqs2'] (is_one_hpc=[False, False, False, False])
- 模型: ['OpenFold']
- 工具: []

## 研究意图（agent_task_prompt）
你是本任务的生物信息学负责人。请先核验默认输入“CAMEO_targets.fasta”、模型/权重标识“finetuning_ptm_2.pt”及相关版本和许可，再根据3篇关联论文与可用计算环境，完成“OpenFold组件消融与结构泛化评测”：复现并消融OpenFold特征、回收和损失组件，比较其在未见折叠上的结构泛化能力。研究对象是蛋白质序列、复合物实体或构象集合，重点检查链组成、折叠拓扑、界面几何和置信度，核心验收指标为TM-score。请在执行前提交对任务的理解、数据和标签血缘、拟采用的方法与模型选择、资源/时间估算、独立验证、质量门禁、风险、失败分支和需要确认的信息；不要把目录中的模型、权重、示例数据或历史结果直接视为已验证答案。正式结果必须保留全量输入、失败样本、随机性和版本记录，提供独立测试、分层性能、不确定度和适用域证据；保持输入序列、链组成、配体身份、残基编号和任务模式；不得静默删链、改残基或把低置信区域当作已证实结构。若证据、数据或资源不足，必须明确标记无法回答并提出最小补充方案，不得用推测、缺失标签或未经验证的高分结果补足结论。最终交付可复现的结果数据、报告、日志和校验信息，并对每项交付给出 PASS、PARTIAL、REJECT 或 BLOCKED。

## 客户端请求
- task_title: OpenFold组件消融与结构泛化评测
- request: 请完成“OpenFold组件消融与结构泛化评测”的可复现研究任务：以“CAMEO_targets.fasta”作为默认输入示例，围绕复现并消融OpenFold特征、回收和损失组件，比较其在未见折叠上的结构泛化能力获得可验证的TM-score结果和可用于后续研究的输出。请先评估数据、模型和资源是否足够，自主提出并论证执行方案；方案确认前不得把实现细节、历史案例或目录默认值当作不可变科学结论。
- scientific_context: 本场景研究蛋白质序列、复合物实体或构象集合，希望解决复现并消融OpenFold特征、回收和损失组件，比较其在未见折叠上的结构泛化能力。链组成、折叠拓扑、界面几何和置信度是主要科学关注点；关联论文用于界定任务背景和证据起点，不代表当前输入上的结果。
- desired_outcome: 得到与输入和任务约束一致、可追溯、可复核的OpenFold组件消融与结构泛化评测结果，包括标准化的序列/实体清单、预测结构或构象集合，以及链和几何完整性报告、独立评估、TM-score统计、不确定度、失败案例和适用边界；不能支持的结论必须明确说明原因。
- executor_role: 执行者应作为具有生物信息学、机器学习、数据质控和可复现研究经验的负责人，把需求转化为可执行方案，主动识别数据泄漏、适用域、偏差和安全风险，并在关键科学口径或资源取舍需要决定时请求确认。

## 问题与适用性
本对象是提交给生物信息学执行者的完整需求书：只规定要解决的科学或业务问题、输入、预期能力、必须满足的约束和验收口径；执行者负责自主选择可行的方法、模型组合、工具、参数、资源、执行顺序和异常处理，并在正式运行前说明方案与风险。

## 工作流步骤（→workflow/→tasks）
- s01 输入与任务定义
- s02 特征与模型准备
- s03 结构推理与采样
- s04 结构质控与汇总

## 关联论文
- Quantifying the Role of OpenFold Components in Protein Structure Prediction | doi:
- Highly accurate protein structure prediction with AlphaFold | doi:
- OpenFold: Retraining AlphaFold2 yields new insights into its learning mechanisms and capacity for generalization | doi:

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）
