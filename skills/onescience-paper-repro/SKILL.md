---
name: onescience-paper-repro
description: OneScience 论文复现信息提取技能。用于根据论文、PDF、arXiv、DOI 或论文标题复现实验、实现模型或提取复现规格的任务；按用户需求从全文和固定版本官方仓库定向取证，重建数据、模型、训练与评测闭环并生成唯一 reproduction_spec.md，交回调用方调度 onescience-coder。本技能不编码、不训练、不运行复现任务。
type: executor
capabilities:
  owns:
    - 用户论文复现要求解析与优先级决策
    - 论文身份识别、全文获取与来源校验
    - 用户需求驱动的论文复现信息提取与证据核验
    - 论文模型结构重建与跨来源冲突裁决
    - 官方仓库按需只读补证
    - 单一复现规格生成与 coder 交接
  not_owns:
    - 编码
    - 训练
    - 推理
    - 运行与评测
  inputs:
    - user_request
    - paper_source
    - paper_content
    - output_dir
    - domain_hint
  outputs:
    - reproduction_spec.md
  downstream:
    - onescience-coder
  intent_aspects:
    - paper_reproduction
    - paper_parsing
  operation_types:
    - create
  artifact_types:
    - spec
  domains:
    - general
---

# OneScience 论文复现信息提取

## 职责边界

本技能把用户对论文复现的要求、论文全文和合法的官方实现证据转换为一份准确、完整、可追溯且
可直接交给 coder 实现的 `reproduction_spec.md`。规格是唯一权威交付物，同时承载科学事实、
模型结构、来源明确的工程接口、冲突决定和不确定性；不再维护独立的证据层或 coder 视图。
本技能只提取和核验信息，不生成源码，不训练、推理、运行或评测，也不针对某个智能体或单个
case 定制实现过程。

核心交付物只有 `<paper_workdir>/reproduction_spec.md`。官方 HTML、TeX 源码、`paper.pdf`、
规范化全文和补充材料只是来源缓存，不属于交付规格。不得再生成 `coder_task_description.md`、
`implementation_contract.json`、`paper_content_summary.md`、`task_intent_profile.md`、
独立 audit 报告或 variable/channel ledger；需要保留的信息全部写入 `reproduction_spec.md`。

## 输入与启动

接受当前用户的自然语言需求、上下文 `step_handoff`，或已有的本步骤
`.onescience/handoff/step_{step_id}.yaml`。没有交接文件时直接使用当前任务上下文，不要求用户
先填 JSON、创建 handoff 或重新提交同一任务。只有使用文件模式时才读取
[文件交接格式](../onescience-orchestrator/references/file_handoff_contract.md)。

`user_request` 表示本次任务要求，不限定为某个字段：优先核对仍可见的用户原文，同时接收
handoff 中的 `task_context.user_goal`、`constraints`、`inputs`、`required_outputs` 和调用方
已传递的明确要求。保留精确文件名、类/函数、签名、shape、路径、目标实验、来源限制和禁止
事项；用户未指定的内容不作为启动缺项。

启动时单独枚举用户原文和 handoff `inputs` 中所有数据文件、数据目录、glob、URI 及 train/
validation/test 分路径。每个路径先按用户给出的字面值登记为 `USER_REQUIREMENT`，再记录其用途、
输入来源、相对路径解析基准和验证状态；不得先摘要为数据集名称，也不得用论文下载地址、仓库默认
目录、占位符或规范化后的另一条路径替换。路径不存在、当前环境不可访问或解析基准不明确时，仍
须把原始值写入规格并单独标记状态，不能因无法验证而省略。

上下文压缩后，保留的任务目标和明确约束仍是有效输入。能够确定任务范围、论文线索和交付
要求时直接继续，不因缺少逐字原文、`user_request` 字段或原文快照而停止。按实际来源登记
要求；上下文归纳不能伪称逐字引用，也不能从任务标题或失败摘要补造未保留的要求。确有影响
任务执行且无法从已有输入确定的缺项时，只指出具体字段及影响，不要求重发整段 prompt；
宿主禁止交互时按其结果协议报告该缺项。

加载本技能后，在同一任务中实际执行来源获取、提取、核验和落盘，再返回正式结果；不要仅
宣布已调用、返回计划或等待额外输入格式。任务输入可用不代表论文证据就绪，仍须执行下述
全文获取与核验流程。

## 来源事实与最终采用值

规格必须同时维护两套优先级，不能用一条简单排序混淆“按什么实现”和“什么是论文事实”：

- **执行决策优先级**：用户明确要求 > 目标论文设置 > 与目标版本匹配的官方仓库补充 > 可逆的
  工程选择。用户要求覆盖复现范围、数据、目标变量、算法变体、训练、评测、接口和禁止事项。
- **事实可信度优先级**：目标版本论文的明确陈述 > 与该论文版本和目标实验匹配的官方仓库证据
  > 其它官方版本证据 > 机械推导。用户要求决定交付，但不能把用户变体改写成论文事实。

用户要求与论文冲突时，最终采用用户要求，并同时保留论文原设定、用户设定、最终决定及对结果
可比性和论文忠实度的影响。论文与官方仓库不一致时，先核对版本、commit、目标实验、训练阶段
和变量语义；论文明确的科学定义不由较晚仓库实现覆盖，仓库只补论文空白或说明版本化实现。
完整规则见 [references/source_conflict_resolution.md](references/source_conflict_resolution.md)。

## 来源与工作目录

先识别唯一论文身份和版本。标题或别名不足以唯一识别时，根据作者、venue、DOI/arXiv、论文
URL 等消歧；仍无法确认则返回 `failed`，不得用模型记忆或同名项目替代。

论文材料和唯一规格统一放在 `.paper2code_work/<canonical-id>/`：优先使用去版本号的 arXiv ID，
其次 DOI slug，最后使用经确认的标题 slug。`output_dir`、实现产物目录或当前工作目录都不能替代
这个目录。识别论文后立即确定并规范化以下两个路径，后续不得改用同名的其它路径：

```text
paper_workdir = .paper2code_work/<canonical-id>/
reproduction_spec_path = .paper2code_work/<canonical-id>/reproduction_spec.md
```

获取前先查找该目录和 `.onescience` 中已有映射，并校验标题、作者与版本。已有完整、有效且保留
公式与表格结构的官方文本时直接复用；只有这类文本不可用或不完整时才复用、下载并解析 PDF。
目录不存在时创建；来源缓存和规格都写入这个目录。

处理来源时完整读取
[references/acquisition_text_workflow.md](references/acquisition_text_workflow.md)。获取顺序必须是：
已核验的本地结构化全文 -> 官方结构化全文（arXiv 优先 `/html/<versioned-id>`）-> 官方源码包
（arXiv `/e-print/<versioned-id>`）-> 官方 PDF。前一层不存在、转换失败或未覆盖公式、表格、附录
等必要内容时才进入下一层；摘要、搜索片段或不完整正文不能支撑 `PAPER_FACT`。
若全文因站点或宿主限制仍不完整，必须如实记录来源覆盖，继续利用用户要求和经核验的官方实现
生成证据受限规格；这会降低论文忠实度，但只要目标和实现链仍可确定，就不自动中断 coder 交接。

论文材料缺少当前实现必需项或表述不明确时，主动从经核验的对应官方 GitHub 等官方仓库只读
补证，无需为每个字段再次询问；用户禁止使用仓库时遵守其限制。只查看与用户要求或闭环缺口
直接相关的配置、文件或符号，不 clone、不下载仓库快照、不复制源码、不使用第三方复现，并
记录 URL、固定 commit/tag、文件、符号、目标实验/训练阶段及所补缺口。仓库可以提供版本化
实现证据，但不能冒充尚未取得的论文事实。

HTML 或源码全文必须完整保存到本地后再分段读取，不能把被工具截断的响应当作全文。仅进入 PDF
回退时，PDF 才必须下载落盘后本地解析；不用 `webfetch` 将 PDF 转成 markdown。宿主返回
`Response too large`/5MB 限制表示工具响应超限，应切换到流式下载并分段读取本地材料，不能判定
论文不可用后直接按 prompt 编码。具体回退、结构保真和下载要求见来源工作流。

## 提取、核验与交接

来源检查后完整读取
[references/structured_extraction_workflow.md](references/structured_extraction_workflow.md)，执行：
与任务领域或方法匹配时，只读取 `assets/domain_knowledge/` 中相关的领域文件和方法知识卡作为
提取与核验清单；知识卡不是当前论文事实，任何具体值仍须回到用户、论文或固定版本仓库取证。
方法卡按信号选择，不全量加载：

- FNO/RNO/DeepONet、PDE、Darcy、Navier-Stokes 或 operator learning：读取
  `assets/domain_knowledge/neural_operator_pde.md`。
- conditional diffusion、denoiser、noise schedule、随机下采样/天气生成：读取
  `assets/domain_knowledge/conditional_diffusion.md`。
- functional/operator attention、dual form、slice/group token、不规则网格注意力：读取
  `assets/domain_knowledge/functional_attention.md`。

1. `REQUIREMENTS`：逐条登记用户要求，并把每项要求展开成需要从来源回答的信息问题；用户提供的
   每个数据路径都是独立 requirement 和数据绑定，不能被其它数据要求合并覆盖。
2. `SOURCE`：确认论文身份、版本、全文、附录、补充材料和官方仓库证据范围。
3. `EXTRACT`：围绕信息问题定向读取，同时补齐 data -> model -> loss -> train -> checkpoint ->
   inference -> metric 闭环，不用摘要式通读替代目标实验取证。
4. `RECONSTRUCT`：模型任务必须读取
   [references/model_structure_reconstruction.md](references/model_structure_reconstruction.md)，以模块树、
   Tensor 数据流、数学算子、shape/语义、参数关系和行为不变量六个互补视图重建结构。
5. `RESOLVE`：按双优先级规则处理用户、论文、仓库内部及跨来源冲突，形成唯一最终采用值。
6. `VERIFY`：逐项回查用户覆盖、证据定位、跨章节一致性、shape 和运行链闭合，修正遗漏和误归属。
7. `PERSIST`：把唯一规格写到 `reproduction_spec_path`，从磁盘读回核验后交给 coder。

使用以下分类：

- `USER_REQUIREMENT`：用户明确选择，最终决策最高优先。
- `PAPER_FACT`：论文明确陈述；正文只引用集中来源索引中的 `source_id`，详细页码、章节、图表或
  公式定位只写在来源索引中，不夹入模型、数据、训练等描述内容。
- `OFFICIAL_REPO_DETAIL`：合法仓库补证，附 URL、版本、文件/符号。
- `INFERRED`：可由证据机械推出，写出推导。
- `UNRESOLVED`：可靠来源未说明或无法裁决，且会影响科学语义或结果复现。
- `IMPLEMENTATION_FREEDOM`：来源未约束、不会改变科学语义的纯工程选择，留给 coder。
- `PROPOSED_CHOICE`：可靠来源仍缺失但代码交付需要候选时使用；写明候选依据、可替换边界、
  可配置方式和论文忠实度影响，绝不标成论文事实。

不得静默生成假设，也不得用“常用值”“合理默认”冒充论文设置来补齐学习率、batch size、
网络层数、损失公式、归一化、数据划分、随机种子、调度器或评测公式。经定向查证仍缺失且不影响
科学语义的内容属于 `IMPLEMENTATION_FREEDOM`；影响实现但存在可逆候选的内容可明确记为
`PROPOSED_CHOICE`，使 coder 继续交付，同时降低 `paper_fidelity`。

## 单一规格的完整性

按任务适用性检查并写入同一份规格：

- 论文身份、版本、复现范围、主结果和对应实验设置。
- 科学问题、方程、边界/初始条件、输入、输出和训练 target。
- 数据来源、用户给出的原始数据路径及用途、路径解析基准与验证状态、字段、单位、split、样本
  构造、预处理、归一化和泄漏风险。
- 模型端到端职责，以及模块树、Tensor 数据流、数学算子、shape/轴与变量语义、参数共享/独立、
  初始化和可验证行为不变量；六个视图必须互相一致。
- 损失公式、权重、reduction、mask 及 prediction/target 关系。
- 训练阶段、优化器、学习率、scheduler、batch、epoch/step、随机性、checkpoint。
- 推理、rollout、后处理、指标公式、评测 split、baseline、表图映射和报告结果。
- 软件、硬件、计算预算、依赖、附录、补充材料、消融和限制。
- 用户指定的文件、接口、路径、产物、验收要求和禁止事项。

用户、论文或合法官方实现中能够约束编码的信息直接写入统一规格，包括适用的配置、文件清单、
模型 constructor、模块结构、forward Tensor Program、数据链、脚本 callable、训练/评测协议、
产物 schema、验收项、冲突和未决项。它们仍是统一科学复现规格的一部分，不形成独立
Implementation Contract 或 coder 视图。来源没有约束的内容分类为 `UNRESOLVED`、
`IMPLEMENTATION_FREEDOM` 或显式 `PROPOSED_CHOICE`，不能为填满模板而自行设计。

`reproduction_spec.md` 必须采用
[references/structured_extraction_workflow.md](references/structured_extraction_workflow.md) 第 7 节的
统一规格结构。结构用于保证科学链和实现链不遗漏，不以标题数量或表格非空判定正确；每个任务
只展开适用内容，不适用项写明 `NOT_APPLICABLE` 及证据，未知项写明来源检查范围和处理策略。
工作流中的示例只示范内容粒度和证据写法，不能原样复制为当前论文事实。

关键数值、公式、变量、shape、split、模型组件和指标必须紧邻简短 `source_id`，详细定位集中在
来源索引中。正文不得使用“Table/Chapter/Section/page 显示”一类论文导航语句污染科学描述。
论文示意图只支持图中明确表达的结构，不支持推断隐藏层数、kernel 参数、张量轴或实现库。
论文主结果、消融结果和用户验收目标必须分别标注，不能互换。

## 状态与 coder 交接

交接前执行落盘门禁：

1. `paper_workdir` 的规范化路径必须严格等于 `.paper2code_work/<canonical-id>/`。
2. `reproduction_spec_path` 必须严格等于 `<paper_workdir>/reproduction_spec.md`；不得指向实现产物根目录。
3. 文件必须存在、非空，并覆盖统一规格结构；不适用项必须有理由，未知项必须有来源范围和处理策略。
4. 从磁盘读回的完整内容必须与 `reproduction_spec_content` 逐字一致。
5. 落盘一致性失败时先修正同一份规格再交接；来源不完整不能用落盘门禁伪装成内容完整。
6. 核对同一实验/阶段的字段在正文、配置、契约与未决表中状态一致；不得同时写为
   `UNRESOLVED` 和已采用默认值。为磁盘全文计算 SHA-256，连同未决项作用范围一起传递。
7. 将用户输入中的全部数据路径与磁盘规格逐项对照：每个原始字面值、用途、解析基准、验证状态
   和 coder 使用落点都必须存在。缺失任一用户数据路径时不得交接，先修正同一份规格。

- `success`：论文身份和目标版本可靠，用户要求已覆盖，目标实验的科学与实现链闭合，关键内容有
  直接证据或正确分类。
- `partial`：唯一目标可确认且规格可交付，但全文覆盖、实现细节或数值复现仍有明确不确定性；
  只要 coder 能按已知事实、配置化候选或可替换边界继续实现，就保持 handoff 可用。
- `failed`：无法唯一识别目标，且现有用户要求、官方材料和允许来源不足以形成不误导的可实现规格。

返回给 orchestrator，并由其把同一份规格交给 `onescience-coder`：

```json
{
  "status": "success | partial | failed",
  "paper_workdir": ".paper2code_work/<canonical-id>/",
  "reproduction_spec_path": ".paper2code_work/<canonical-id>/reproduction_spec.md",
  "reproduction_spec_content": "reproduction_spec.md 完整内容",
  "reproduction_spec_sha256": "磁盘规格文件的 SHA-256",
  "source_status": "verified_fulltext | partial_official_sources | identity_only",
  "paper_fidelity": "exact | evidence_aligned | candidate",
  "implementation_readiness": "ready | ready_with_configurable_choices | insufficient",
  "key_conflicts": [],
  "key_unresolved": [],
  "paper_repro_handoff": true,
  "recommended_consumer": "onescience-coder",
  "next_action": "onescience-orchestrator"
}
```

`paper_repro_handoff` 由 `implementation_readiness` 决定，而不是由全文是否完整单独决定。
`ready` 或 `ready_with_configurable_choices` 时应交给 coder；`failed/insufficient` 时才设为 false，
并说明缺少的最小目标识别或实现信息。每个未决项须注明影响构建、运行、论文忠实度还是精确数值
复现，以及采用必填配置、可替换策略、多变体或候选实现中的哪一种继续方式；不能只加标签后
静默硬编码。
返回规格只完成信息提取步骤；用户要求生成代码时，调用方还必须调度 coder 并核查实际源码产物。
