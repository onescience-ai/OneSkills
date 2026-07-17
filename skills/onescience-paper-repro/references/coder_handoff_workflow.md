# Coder 任务描述及交接工作流

## 目标

把审计后的 `reproduction_spec.md` 展开为 `onescience-coder` 唯一消费的 `coder_task_description.md`。该文件不是摘要，必须完整承载 spec 中所有已确定内容、审计结论、缺口和实现假设。

## 生成规则

1. 先确认 `reproduction_spec.md` 已通过 `audit_workflow.md`。
2. 逐节展开 spec，不得只概述背景。
3. 保留 `MISSING:`、`INFERRED:`、`ASSUMPTION:` 标签。
4. 不得引入 spec 中没有证据的新任务、新模型、新参数、新数据或新公式；若某项来自官方开源仓库只读参考，必须在任务描述中保留 `OFFICIAL_REPO_REFERENCE:` 标签，并说明对应文件/模块、用途、补的是哪个论文缺口；若该项涉及论文与官方仓库的冲突，必须沿用 spec 中“论文优先”的冲突处理结论。 
5. 不得写“详见 reproduction_spec.md”“以 reproduction_spec.md 为准”“请再读取 spec”。
6. 如果 spec 中存在冲突处理结论，必须原样写入任务描述。
7. 必须使用下方强制模板生成 `coder_task_description.md`；模板中的 `<...>` 占位符必须由审计后的 `reproduction_spec.md` 逐项展开填充，不能原样保留。
8. 必须在 `coder_task_description.md` 内根据当前任务需求规划预期代码文件结构，并给出覆盖数据、模型、训练、推理、评估和配置流转的整体实现架构流程图；这两项是任务书内容，不新增独立交接文件。

## `coder_task_description.md` 强制模板

```markdown
## 任务概述

请实现<领域>领域的<任务类型>任务，输入为<变量、模态、时间步、空间维度、单位和 shape>，输出为<目标变量、预测步长、类别/连续值、shape>。预测形式为<单步/多步/自回归/条件生成/闭环 rollout/迭代求解>，使用<数据集/来源>进行训练/验证/微调，并满足<边界条件/守恒约束/物理先验/等变性/不变性>。

## 输入输出与数据

数据来源为<数据集/来源、版本、下载入口、许可、子集、年份/区域/分辨率>，样本构造方式为<历史窗口、预测窗口、stride、split、过滤条件、变量集合、样本规模>。变量-通道 ledger 为<变量名、变量组、层数、时间步数、输入/输出/forcing/static 角色、通道数计算公式>。输入张量为<shape 与维度含义>，输出张量为<shape 与维度含义>。单位、坐标、标签来源、缺失值和数据泄漏风险为<规则>。

## 数据处理与张量协议

从原始数据到模型输入的完整 pipeline 为<重采样、插值、裁剪、padding、对齐、投影、网格转换、tokenization、特征工程、数据增强>。归一化策略为<per-variable/per-level/global/per-sample/min-max/z-score、统计量来源、训练/验证/测试一致性>。forcing、静态特征、input-only 变量、output-only target、辅助变量和目标变量处理方式为<处理规则>。shape ledger 为<每一步张量形状、通道数、维度含义、batch/time/node/level/channel/feature 组织方式>。时间维处理为<拼接到 channel / 保留 sequence / 合并 batch / 时间编码 / 融合模块>；如果发生 reshape 或时间维消失，必须说明具体操作。

## 模型与实现范围

模型结构为<总体架构>：首先<encoder/embedding/data flow>，然后<processor/backbone/message passing/attention/Fourier/diffusion/solver>，最后<decoder/head/postprocess>。必须实现的模块、每个模块输入输出 shape、数据流箭头、skip connection、multi-branch fusion、图/网格/token 组织、参数共享和初始化方式为<逐项展开>。learnable feature / embedding 颗粒度为<per-node/per-edge/per-variable/per-level/per-grid/global broadcast、参数 shape、广播规则>。关键超参包括<层数、hidden dim、head 数、FFN dim、kernel、basis、message passing steps、dropout、activation、normalization、stochastic depth、gating、位置/时间/坐标/频域编码等>。

## 预期代码文件结构

请按当前任务需求规划实现文件落点，必须覆盖<配置、数据读取、数据处理、变量/通道 ledger、模型模块、损失函数、训练入口、推理入口、评估入口、可视化/结果保存、测试或静态校验、文档>。文件结构必须以目录树形式给出，每个文件后说明职责、主要类/函数、输入输出对象、与其它文件的调用关系，以及该文件承载的 `reproduction_spec.md` 要求。若论文未规定项目布局，可写 `ASSUMPTION:` 并给出保守、可替换的工程布局；不得要求 coder 自行重新设计整体目录。

## 整体实现架构流程图

请给出一个 Mermaid `flowchart`，覆盖从<原始数据/配置加载>到<样本构造/预处理>、<模型 forward>、<loss 计算>、<训练循环>、<checkpoint/日志>、<推理/rollout>、<后处理>、<评估指标>和<结果输出>的完整实现流程。流程图节点必须与“预期代码文件结构”中的文件或模块名称对应，并标注关键张量 shape、变量/通道 ledger、归一化/反归一化、外部 forcing、mask、rollout 更新和评估 target 的流向；如果某个环节来自 `MISSING:`、`INFERRED:` 或 `ASSUMPTION:`，必须在节点文本中保留对应标记。

## 损失、训练、推理与评估

损失函数为<主损失公式、权重项、物理约束、多任务组合、reduction、mask、teacher forcing/scheduled sampling/rollout loss>。loss target 类型为<full state / normalised state / tendency / delta / residual / noise / score / 其它>，并说明它与预测目标、rollout 更新量和评估 target 是否一致。训练配置为<optimizer、lr、scheduler、warmup、decay、batch 语义、epoch/step、precision、gradient clipping、weight decay、EMA、checkpoint、best model、resume、seed、分布式方式、预训练/微调/冻结策略>。推理阶段为<输入构造、单步/多步/rollout、窗口更新、外部 forcing、反归一化、单位恢复、插值回原网格、后处理、保存频率、不确定性估计>。评估采用<指标公式、区域、层级、变量、时间范围、lead time、baseline、统计方式、置信区间/显著性、结果表对应 checkpoint、领域诊断指标>。

## 可复现配置与领域专属细节

必须保留的可复现配置为<硬件、软件版本、框架、依赖、训练耗时、显存、参数量、FLOPs、模型大小、训练预算、ablation 设置>。领域专属细节为<气象/海洋/地球系统、CFD、材料/化学、生信/生命科学等对应变量、单位、网格、PDE、边界条件、原子/晶胞/邻接、序列/token/split/泄漏风险等>。

## 缺口、假设与保守实现策略

以下内容来自 `MISSING:`、`INFERRED:` 和 `ASSUMPTION:` 标记，必须在代码实现中按保守策略处理：<逐项列出缺口、推断、假设、理由、可替换选项、是否阻塞实现、占位接口或显式报错策略>。

## 代码生成后静态 review 要求

生成代码后必须执行静态需求一致性 review，逐条核对参数数量、模型结构、输入输出 shape、数据处理、训练/推理/评估逻辑、文件落点、预期代码文件结构和整体实现架构流程图是否满足本任务描述；发现不一致时先修改代码再输出最终结果。该 review 是静态审查，不要求运行训练、测试或 debug。
```

结构不允许删减；如果某项在论文中没有证据，必须在对应段落保留 `MISSING:`、`INFERRED:` 或 `ASSUMPTION:`，并在“缺口、假设与保守实现策略”中集中列出。

## 交接字段

交接给 `onescience-coder` 时只提供任务描述路径和全文：

```text
paper_repro_handoff=true
task_method=paper2code
domain_task_family=paper-reproduction
paper_workdir=.paper2code_work/<paper_key>
task_description_path=<coder_task_description.md 路径>
task_description_content=<coder_task_description.md 全文>
coder_reference_mode=paper_plus_official_repo_readonly
coder_static_review_required=true
next_action=onescience-coder
```

## 回复要求

交接前必须在回复中完整复述 `coder_task_description.md`，不能只给路径或只复述主要内容。内容很长时也要保留完整任务书，因为它就是下游唯一编码输入。
