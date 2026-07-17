# 解析论文与结构化信息提取工作流

## 目标

把 `.paper2code_work/<id>/paper_text.md`、`figures_tables.md`、附录和补充材料转换为结构化 `reproduction_spec.md`。提取结果必须全面、准确、可追溯，不能只覆盖摘要、主方法或容易提取的段落。本文件只定义跨领域通用提取框架；领域差异从 `../assets/domain_knowledge/` 按需读取。

## 证据原则

- 每个关键结论必须标注证据位置：section/table/figure/equation/page。
- 明确给出的内容写为事实。
- 推断得到的内容标为 `INFERRED:`。
- 论文未说明但实现必须选择的内容标为 `MISSING:` 或 `ASSUMPTION:`。
- 不得把领域经验、实现便利性或常见做法写成论文事实。
- 只有当论文正文、附录、补充材料、用户材料和公开页面对某个实现必需细节仍缺失或说明不足时，才允许使用官方开源仓库只读参考；引用时必须明确标注为 `OFFICIAL_REPO_REFERENCE:`，并写清对应 URL、文件/模块位置、补充的是哪个缺失细节，以及它是补充实现线索而不是论文事实来源。

## 全面性与准确性门槛

生成 `reproduction_spec.md` 前，必须逐项检查论文材料覆盖情况：

- 正文：Abstract、Introduction、Method/Model、Training/Experiment、Results、Discussion/Conclusion。
- 表格：变量表、超参表、数据集表、结果表、消融表。
- 图与图注：架构图、数据流图、训练/评估曲线、案例图。
- 算法框和公式：模型计算、loss、normalization、rollout、metric。
- 附录和补充材料：实现细节、额外指标、训练预算、失败模式、限制说明。

如果某一类材料存在但未被解析或未进入 `reproduction_spec.md`，必须在 spec 的缺口或审计结论中说明，不能静默遗漏。

准确性要求：

- 每个数值、变量名、shape、超参、指标、split、horizon、模型组件都必须能回指证据位置。
- 同一事实在正文、表格、图注、附录中出现不一致时，必须记录冲突并交给审计流程修正。
- 不确定内容不得写成确定要求；只能写 `MISSING:`、`INFERRED:` 或 `ASSUMPTION:`。
- `reproduction_spec.md` 生成后必须能回答“论文要实现什么、代码需要哪些数据/模型/训练/推理/评估细节、哪些仍缺失或是假设”。

## 论文内容摘要与领域知识召回

在读取领域知识前，必须先从 `paper_text.md`、`figures_tables.md`、附录和补充材料生成 `<paper_workdir>/paper_content_summary.md`。摘要用于召回领域知识，不作为论文事实的替代来源。

`paper_content_summary.md` 至少包含：

- 一句话任务目标。
- 真实科学领域候选与理由。
- 数据对象、输入/输出对象和关键术语。
- 模型/方法关键词。
- 训练、推理、评估关键词。
- 论文中出现的表格、图、算法框、附录主题。
- 仍不确定的领域归属或交叉领域信号。

然后按摘要召回领域知识：

1. 先读取 `../assets/domain_knowledge/` 下各领域文件顶部的摘要表头，根据摘要中的领域候选和关键词选择 0 个、1 个或多个领域文件。
2. 如果论文是交叉领域，例如物理场 + 材料、遥感 + 地球系统、生物结构 + 图神经网络，可以读取多个领域文件。
3. 领域资产用于提示“应该检查哪些字段”，不是事实来源。只有论文或用户材料中出现的内容才能写入 `reproduction_spec.md` 的确定要求。

## `reproduction_spec.md` 输出粒度硬性要求

`reproduction_spec.md` 不是论文摘要，而是下游编码代理可直接执行的复现规格。每个编号模块都必须写到“可以据此设计数据类、模型类、训练循环、推理脚本和评估脚本”的粒度。禁止只写“使用某模型”“采用某数据集”“进行评估”这类泛化描述。

每个编号模块必须包含：

- `**证据位置**`：列出 section/table/figure/equation/page/appendix。多个来源用逗号分隔。
- `确定事实`：论文或用户材料明确给出的实现相关内容，必须包括数值、变量名、shape、公式、split、horizon、组件名、超参或指标的原文语义。
- `结构化 ledger`：凡涉及变量、通道、shape、模块、阶段、指标、数据划分或实验矩阵，必须用表格或清单展开，不得只写自然语言。
- `关键缺失`：论文未说明但实现必须选择的内容，逐条写成 `MISSING:`；如果为了可执行需要给出保守默认值，写成 `ASSUMPTION:` 并说明理由和可配置项。
- `一致性检查提示`：记录本节需要审计工作流复核的高风险项，例如通道数求和、shape 是否闭合、训练目标是否等于评估目标。

写作要求：

- 中文为主，术语可保留英文原名。
- 不压缩细节。若论文给出 13 个变量、4 个阶段、6 个指标，必须逐项列出。
- 不把推断写成事实。推断项必须以 `INFERRED:` 开头，并说明推断依据。
- 不用“等”“相关”“若干”“适当”“常规”替代具体内容。论文确实没有具体内容时写 `MISSING:`。
- 同一字段在多处证据不一致时，保留冲突：`CONFLICT:` 后列出冲突来源，交给审计流程修正。
- 数值必须保留单位和语义，例如 `6h lead time`、`0.25 degree grid`、`batch size per GPU`，不能只写数字。
- 领域知识只能提示检查项，不能补成论文事实。

## 通用提取维度

### 1. 论文来源与元数据

必须写清楚论文来源边界，方便追溯和审计：

- 标题、作者、年份、会议/期刊或预印本版本。
- DOI、arXiv ID、URL、本地 PDF 路径、补充材料路径。
- 访问或解析时间。
- 使用的材料范围：正文、图表、附录、补充材料、用户提供材料。
- 明确写入：`implementation_code_used=official_repo_readonly_optional`。
- 若使用了官方开源仓库只读参考，必须记录官方仓库 URL、使用范围、涉及的模型/数据/训练/推理/评估文件或模块、补充的是哪个缺失或说明不足的实现细节，并明确这些内容属于 `OFFICIAL_REPO_REFERENCE:`，不得写成论文事实；若论文已明确某项，则官方仓库不能重新作为该项的主依据。
- 不得搜索、读取或引用第三方代码仓库作为事实来源；不得下载、clone 或复制任何仓库到本地。
- 若存在多个版本，记录版本号和选择理由。

### 2. 任务与问题定义

这一节必须像任务合同一样精确描述“模型学什么、输入什么、输出什么、怎样使用”：

- 任务类型：预测、分类、生成、反演、模拟加速、重建、优化、检索、控制等，保留论文中的具体领域名称。
- 输入对象：物理量、模态、序列、图、网格、结构、文本、图像或其它对象；列出变量名、数量、单位、层级、分辨率和时间步。
- 输出对象：预测量、生成物、类别、分数、场变量、轨迹或结构；说明 shape 是否与输入一致。
- 目标变量和训练 target：预测 state、delta、residual、tendency、noise、score、label 还是其它形式。
- 预测/生成/推理形式：单步、多步、自回归 rollout、条件生成、采样、搜索、ensemble、online/offline。
- 时间、空间、物理、几何、生物、化学或业务约束。
- 核心贡献：新模型、新数据处理、新训练方法、新损失、新评估、新系统工程或新实验结论。
- 复现范围边界：论文中哪些能力必须实现，哪些只是分析、可视化或非核心展示。

### 3. 数据集与样本定义

这一节必须能指导实现 dataset 和 dataloader：

- 数据集名称、版本、来源机构或发布者、许可、下载入口或获取方式。
- 原始数据格式：文件类型、字段名、单位、坐标系、采样频率、分辨率、对象 schema。
- 子集范围：时间、空间、对象类别、实验条件、过滤条件、质量控制规则。
- train/validation/test split：年份、case、随机划分、官方划分、交叉验证或留一设置；没有验证集时写 `MISSING:`。
- 单样本构造：输入窗口、历史步数、预测步长、stride、pair/triplet、轨迹长度、图/结构构造、负样本、mask。
- 标签来源：观测、模拟、再分析、人工标注、弱标签、teacher model 或计算派生量。
- 样本数：论文给出则列出；可由 split 和频率确定时写 `INFERRED:` 并给出公式；无法确定写 `MISSING:`。
- 数据泄漏风险：时间穿越、同源样本、相同对象跨 split、归一化统计量泄漏、case 重复。

### 4. 数据处理与张量协议

这一节必须给出从原始数据到模型张量的完整流水线和 shape ledger：

- 原始数据读取、字段选择、单位转换、坐标转换、重采样、插值、裁剪、padding、投影、tokenization、图构建、结构转换。
- 缺失值、异常值、边界、周期边界、mask、land/sea/valid region 等处理。
- 归一化/标准化策略：按变量、按层级、按通道、按数据集、按训练集统计；均值方差、min/max 或其它统计量的来源。
- 变量/特征角色：input、output、forcing、static、target-only、loss-only、metadata、mask。
- 变量通道 ledger：变量名、层级或子维度、通道数、角色、单位、证据位置。
- shape ledger：逐阶段记录 batch、time/history、space/node/token、level、channel、feature 的含义和变化。
- 如果涉及变量数、字段数、通道数、类别数、节点/边数，必须同时生成 `<paper_workdir>/variable_channel_ledger.json` 供机械校验。

推荐表格：

| 阶段 | 张量/对象 | Shape/Schema | 维度语义 | 处理动作 | 证据位置 |
| --- | --- | --- | --- | --- | --- |
| 输入 | `X_t` | `C x H x W` | `C` 为变量通道 | 读取并标准化 | Section ... |

### 5. 模型结构与组件映射

这一节必须能指导实现 `model.forward()` 和每个子模块：

- 总体架构：encoder、processor/backbone、decoder/head、postprocess 的顺序和职责。
- 数据流：每个模块的输入对象、输出对象、shape 变化、是否保留 skip/residual。
- 模块细节：层数、hidden dim、head 数、kernel size、patch size、basis、message passing steps、MLP ratio、dropout、activation、normalization。
- 编码信息：位置编码、时间编码、坐标编码、层级编码、变量编码、edge/node/global learnable features。
- 参数共享、权重冻结、LoRA/adapters、multi-stage modules、teacher/student、ensemble 成员。
- 初始化、预训练权重、加载策略、可训练参数范围。
- 论文没有给出内部顺序时，不得编写确定伪代码；写 `MISSING:` 或 `ASSUMPTION:`。

推荐表格：

| 组件 | 输入 | 输出 | 核心操作 | 关键超参 | 可训练参数 | 证据位置 |
| --- | --- | --- | --- | --- | --- | --- |

### 6. 损失函数与优化目标

这一节必须区分训练目标、模型输出和评估目标：

- 主损失名称、公式、target、prediction、reduction、权重、mask、区域/对象范围。
- 辅助损失、正则项、物理约束、守恒项、对抗/对比/蒸馏/重建项。
- 多变量、多层级、多时间步、多任务损失的加权方式。
- rollout loss、teacher forcing、scheduled sampling、多步训练或 curriculum。
- loss 使用归一化空间还是物理单位空间。
- 训练目标和推理输出不一致时，明确转换关系。
- 公式缺失但实现必须选择时写 `MISSING:`；建议假设必须标 `ASSUMPTION:`。

### 7. 训练配置

这一节必须能指导写训练脚本和配置文件：

- 训练阶段划分：预训练、微调、迁移学习、冻结/解冻、adapter/LoRA、蒸馏、ablation。
- 每个阶段的数据、初始化权重、可训练模块、loss、epoch/step、batch size、梯度累积、checkpoint。
- optimizer、learning rate、scheduler、warmup、decay、weight decay、gradient clipping、EMA。
- precision、mixed precision、distributed strategy、GPU/节点数、随机种子、多次运行统计。
- augmentation、sampling、curriculum、teacher forcing ratio、negative sampling。
- early stopping、validation frequency、checkpoint selection metric。

推荐表格：

| 阶段 | 数据 | 初始化 | 可训练模块 | 目标/loss | batch/step/epoch | optimizer/scheduler | 证据位置 |
| --- | --- | --- | --- | --- | --- | --- | --- |

### 8. 推理、rollout 与后处理

这一节必须能指导写 inference 脚本：

- 推理输入构造：单样本、batch、历史窗口、forcing/static feature、外部条件。
- 单步、多步、自回归 rollout、sampling、beam/search、ensemble 或 test-time augmentation。
- 自回归更新规则：哪些变量被模型输出替换，哪些变量保持外部 forcing 或重新读取。
- horizon、lead time、输出频率、保存频率、checkpoint 选择。
- 反归一化、单位恢复、坐标/网格/结构映射、插值回原空间、阈值化、约束修正。
- 推理资源、批处理限制、边界条件、流式或离线模式。
- 论文仅评估某些 horizon 时，不得把未评估 horizon 写成确定能力。

### 9. 评估协议

这一节必须能指导实现 metrics 和复现实验表格：

- 指标名称、公式、权重、mask、reduction、单位、越大越好或越小越好。
- 评估对象：变量、类别、层级、区域、结构元素、时间范围、lead time、case。
- baseline：名称、版本、训练数据、分辨率、checkpoint 或论文表格来源。
- 统计方式：mean/std、median、confidence interval、significance test、bootstrap、多 seed。
- 表格和图中每个结果对应的数据集、split、checkpoint、lead time、case 或场景。
- 消融实验、鲁棒性实验、泛化实验、限制章节中的失败模式和补充指标。
- 如果指标公式没有给出但指标名称出现，写 `MISSING:` 并说明是否可用领域标准公式作为 `ASSUMPTION:`。

推荐表格：

| 指标 | 公式/计算口径 | 评估对象 | 范围/horizon | baseline | 结果表/图 | 证据位置 |
| --- | --- | --- | --- | --- | --- | --- |

### 10. 可复现配置

这一节必须集中记录环境、预算和可执行约束：

- 硬件：GPU/CPU/加速器型号、数量、节点数、显存、互联。
- 软件：Python、深度学习框架、CUDA/ROCm、核心依赖、数据工具。
- 参数量、FLOPs、吞吐、显存、训练耗时、推理耗时、存储需求。
- 随机种子、确定性设置、版本固定、checkpoint 命名和保存策略。
- 训练预算、模型大小、ablation 设置、配置文件应暴露的关键参数。
- 未说明但实现必须选择的项，逐条写入 `MISSING:` 或 `ASSUMPTION:`。

### 11. 领域专属细节

这一节只写论文中实际出现或用户材料提供的领域字段。领域资产中没有被论文证据支持的项只能作为检查提示，不写成确定要求。

根据论文所属领域选择性展开：

- 地球系统：变量清单、垂直层、网格、投影、时间步、lead time、区域权重、周期经度、land/sea mask、物理单位。
- CFD/PDE：方程、边界条件、初始条件、网格类型、时间积分、Re/Mach 等无量纲数、守恒量、仿真 case。
- 材料/化学：原子类型、结构表示、晶胞、邻接/截断半径、能量/力/stress target、单位、周期边界。
- 生物：序列/结构/图表示、物种/样本、残基/原子/细胞层级、标签定义、数据库版本、评价口径。
- 其它领域：列出该领域中影响实现的对象 schema、约束、单位和评估特殊规则。

### 12. 复现实验矩阵与验收标准

这一节必须把论文结果转成可执行的复现实验清单：

- 必做实验：主结果、核心 ablation、关键泛化或鲁棒性实验。
- 可选实验：论文展示但非核心实现依赖的分析、可视化或扩展。
- 每个实验的数据 split、模型配置、checkpoint、指标、预期复现目标。
- 最小可运行验证：小样本/小网格/小 epoch smoke test 的合理构造，若论文未说明则写 `ASSUMPTION:`。
- 验收标准：shape 通过、loss 可下降、指标脚本可运行、主结果表可复算、关键图可复现。

### 13. 实现缺口与建议假设

这一节必须集中列出所有阻塞和非阻塞缺口，不得散落后遗漏：

- `MISSING:` 论文未说明且实现必须决定的内容。
- `ASSUMPTION:` 为了实现建议采用的保守默认值、理由、替代选项、应暴露的配置项。
- `INFERRED:` 可由论文信息计算或推断的内容，附推断公式和证据。
- `CONFLICT:` 多处证据冲突，列出来源、冲突字段、暂不确定的选择。
- 按优先级标注：阻塞编码、影响指标复现、仅影响工程便利性。

### 14. 审计结论

结构化提取阶段先写审计占位，审计工作流必须在迭代修复后补全：

- 待审计的高风险项：变量/通道数、shape ledger、loss target、rollout 语义、metric 公式、split。
- 已生成的机械校验输入，例如 `variable_channel_ledger.json`。
- 需要审计流程回查的冲突、缺口和假设。

## `reproduction_spec.md` 强制模板

生成 `reproduction_spec.md` 时必须使用下面结构。各节不得留空；没有证据时写 `MISSING:`，不删除标题。

```markdown
# 复现规格

## 论文来源与元数据

- 标题：
- 作者：
- 年份/venue：
- DOI/arXiv/URL：
- 本地材料路径：
- 解析时间：
- 使用材料范围：
- implementation_code_used=official_repo_readonly_optional
- official_repo_reference_used=true|false
- official_repo_reference_scope=

## 证据与可信度规则

- 确定事实：
- INFERRED：
- MISSING：
- ASSUMPTION：
- CONFLICT：

## 1. 任务与问题定义

**证据位置**:

### 确定事实
- 任务类型：
- 输入：
- 输出：
- 目标变量/target：
- 预测或推理形式：
- 约束条件：
- 核心贡献：
- 复现范围边界：

### 关键缺失
- MISSING:

### 一致性检查提示
-

## 2. 数据集与样本定义

**证据位置**:

### 数据集
- 名称/版本/来源：
- 原始格式与字段：
- 时间/空间/对象范围：
- 许可或访问方式：

### 样本构造
- 输入样本：
- 标签/目标：
- 窗口、stride、lead time 或结构关系：
- 样本数：

### 划分
- train：
- validation：
- test：
- 数据泄漏风险：

### 关键缺失
- MISSING:

## 3. 数据处理与张量协议

**证据位置**:

### 数据流程
1.

### 变量与通道 Ledger
| 变量/字段 | 层级/子维度 | 通道数/特征数 | 角色 | 单位 | 证据位置 |
| --- | --- | --- | --- | --- | --- |

### Shape Ledger
| 阶段 | 张量/对象 | Shape/Schema | 维度语义 | 处理动作 | 证据位置 |
| --- | --- | --- | --- | --- | --- |

### 归一化与 mask
-

### 关键缺失
- MISSING:

## 4. 模型结构与组件映射

**证据位置**:

### 总体架构
-

### 组件 Ledger
| 组件 | 输入 | 输出 | 核心操作 | 关键超参 | 可训练参数/共享策略 | 证据位置 |
| --- | --- | --- | --- | --- | --- | --- |

### 数据流与 shape 闭合
1.

### 初始化、预训练与冻结策略
-

### 关键缺失
- MISSING:

## 5. 损失函数与优化目标

**证据位置**:

### Loss Ledger
| 损失项 | prediction | target | 公式/权重/reduction | mask/范围 | 阶段 | 证据位置 |
| --- | --- | --- | --- | --- | --- | --- |

### 训练目标与推理输出关系
-

### 关键缺失
- MISSING:

## 6. 训练配置

**证据位置**:

### 训练阶段 Ledger
| 阶段 | 数据 | 初始化 | 可训练模块 | loss/目标 | batch/step/epoch | optimizer/scheduler | 证据位置 |
| --- | --- | --- | --- | --- | --- | --- | --- |

### 其它训练设置
- precision：
- distributed：
- seed：
- checkpoint：
- augmentation/sampling：

### 关键缺失
- MISSING:

## 7. 推理、rollout 与后处理

**证据位置**:

### 推理协议
- 输入构造：
- horizon/lead time：
- rollout 或 sampling：
- 自回归更新：
- checkpoint 选择：

### 后处理
- 反归一化/单位恢复：
- 映射回原空间：
- 保存频率和格式：

### 关键缺失
- MISSING:

## 8. 评估协议

**证据位置**:

### 指标 Ledger
| 指标 | 公式/计算口径 | 评估对象 | 范围/horizon | baseline | 结果表/图 | 证据位置 |
| --- | --- | --- | --- | --- | --- | --- |

### 实验结果映射
-

### 关键缺失
- MISSING:

## 9. 可复现配置

**证据位置**:

- 硬件：
- 软件/依赖：
- 参数量/FLOPs/显存：
- 训练/推理耗时：
- 配置文件必须暴露的参数：

### 关键缺失
- MISSING:

## 10. 领域专属细节

**证据位置**:

### 领域对象与单位
-

### 领域约束与特殊评估规则
-

### 关键缺失
- MISSING:

## 11. 复现实验矩阵与验收标准

**证据位置**:

| 实验 | 数据/split | 模型配置 | checkpoint | 指标 | 预期复现目标 | 必做/可选 | 证据位置 |
| --- | --- | --- | --- | --- | --- | --- | --- |

### 最小可运行验证
-

### 验收标准
-

## 12. 实现缺口与建议假设

### 阻塞编码的缺口
- MISSING:

### 影响指标复现的缺口
- MISSING:

### 建议假设
- ASSUMPTION:

### 推断项
- INFERRED:

### 冲突项
- CONFLICT:

## 13. 下游实现优先级与交接摘要

- 必须实现：
- 可以延后：
- 不在本次复现范围：
- coder_task_description.md 必须完整承载的高风险条目：

## 14. 审计结论

- 待审计高风险项：
- 已生成的机械校验输入：
- 审计工作流待补全：
```

## 合格输出示例风格

每个模块应达到如下信息密度，而不是只写一句摘要：

```markdown
## 1. 任务与问题定义

**证据位置**: Section 1 (p.2-3), Section 2 开头 (p.3)

- 任务类型：全球中期天气预测（global medium-range weather forecasting），6 小时单步预测 + 自回归 rollout。
- 输入：HR 初始大气状态 `X_t in R^{C x H_h x W_h}`，包含 5 个气压层变量（每变量 13 层）+ 4 个表面变量，共 `C=5 x 13 + 4 = 69` 通道。
- 输出：`X_{t+1}`（6 小时后预报），相同 shape `C x H_h x W_h`。
- 预测形式：单步 6h 预测，自回归 rollout 最多 10 天（40 步）。
- 约束条件：面积加权评估（latitude weighting）。
- 核心贡献：提出从 LR 预训练模型迁移到 HR 的多阶段策略。

### 关键缺失
- MISSING: 验证集划分方式。
```

真实输出必须根据具体论文证据生成，不得照抄示例内容。
