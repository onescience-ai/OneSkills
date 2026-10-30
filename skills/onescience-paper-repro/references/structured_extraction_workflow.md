# 复现规格提取与核验

## 目标

直接从当前用户任务要求、论文全文、附录、补充材料和合法的官方仓库补证生成唯一交付物
`reproduction_spec.md`。规格把科学事实、模型结构、来源明确的工程信息、冲突和不确定性放在
同一文档中；原子证据只是提取方法，工程映射只是 coder 的后续工作，不形成第二份规格。

## 1. 用户要求覆盖表

按主技能“输入与启动”接收任务；原文可见时逐句核对，恢复执行时逐项核对已保留的明确约束。
不要先用论文默认设置解释或改写请求。登记所有明确要求：

- 目标论文、实验、复现范围和预期结果。
- 数据来源、用户指定的数据文件/目录/glob/URI、允许的文件、字段、split、样本和预处理。
- 科学方程、输入/输出、target、算法、模型、损失和指标。
- 训练、推理、rollout、checkpoint、日志和结果保存。
- 文件、类、函数、签名、shape、配置、路径和输出格式。
- 官方仓库使用许可、禁止事项和其它边界。

用户要求的优先级覆盖以上全部类别，不只覆盖名称。表中每项至少包含：要求内容及实际输入
来源、类别、最终采用值、覆盖状态、证据标签和相关冲突 ID。“原始要求”列保留用户原意；
来自 handoff 或保留上下文的要求注明来源，不伪称逐字原文。用户未要求的内容不要反推为
隐含要求。

所有用户数据路径必须在阅读论文前逐项建立数据绑定。绑定至少包含 `binding_id`、用户给出的
原始字面值、角色（data_root/train/validation/test/单文件/glob/URI）、要求来源、相对路径解析
基准、验证状态、预期数据身份/schema 和 coder 使用落点。遵守以下规则：

- 原始字面值逐字符保留，包括大小写、空格、扩展名、glob 和 URI；可另列解析后的路径，但不能
  用它覆盖原值。`~`、环境变量和相对路径不静默展开；解析基准未知时明确标为未决。
- 数据路径是本次执行的数据绑定，论文数据集名称、官方下载地址和仓库默认目录是数据语义证据；
  两者必须关联但不能互相替代。只有检查内容后才能声称用户路径符合论文所需数据 schema。
- 本地存放位置与论文下载位置不同本身不构成冲突；路径内数据的身份、版本、字段、split、单位或
  样本语义不一致才构成实质冲突。此时保留用户路径和论文数据契约，按冲突规则记录最终执行选择
  及对论文可比性/忠实度的影响，不能通过改写路径掩盖差异。
- 当前环境无法访问或路径不存在时，使用 `provided_unverified`、`unavailable_in_current_env` 或
  `not_found` 等明确状态；仍保留路径并交给 coder 做显式校验，不得改用合成数据或自动下载。
- 多个 split 路径、文件列表或 glob 必须逐项登记。数据输入路径与 checkpoint、输出目录、源码
  路径分开分类，不能因都叫 `path` 而混写。

### 1.1 从要求生成取证问题

登记要求后，为每个 requirement 生成实际需要从论文或仓库回答的 `information_need`，而不是先
按通用模板摘要全文。例如用户要求“复现某模型在某数据集上的实验”，至少展开：

- 目标实验和模型变体如何唯一识别？
- 原始数据文件、字段、split、分辨率、layout、dtype 和预处理是什么？
- 模型输入、输出、训练 target、loss target 和评估 target 是否为同一对象？
- 模块如何连接、重复、共享或分支，各边 tensor 的 shape/轴和变量语义是什么？
- loss、optimizer、scheduler、训练阶段、checkpoint 选择和 resume 语义是什么？
- 推理/rollout 如何构造输入、更新状态、反归一化并映射到指标与产物？
- 用户指定的文件、接口、路径和禁止事项分别由什么来源约束？
- 每个用户数据路径绑定到哪个数据角色、split 和 consumer？相对路径从哪里解析，是否已验证存在
  且满足论文所需字段、shape、dtype 与样本语义？

每项 information need 记录 `need_id / requirement_ids / expected_source / resolved_value /
source_ids / status`。阅读过程中发现闭环缺口时新增 need；不能因为用户未逐项询问就忽略实现目标
必需的信息，也不能把与目标实验无关的全文内容大量写入规格。

## 2. 证据、描述与冲突

关键声明使用：

- `USER_REQUIREMENT`：用户明确规定，由可见原文、任务 handoff 或保留上下文承载，注明实际来源。
- `PAPER_FACT`：论文明确陈述，正文只附简短 `source_id`。
- `OFFICIAL_REPO_DETAIL`：经许可的官方仓库补证，附 URL、版本、文件/符号。
- `INFERRED`：从已列证据机械推出，写清推导过程。
- `UNRESOLVED`：来源缺失、表述模糊或无法裁决，且会影响科学语义或复现结果。
- `IMPLEMENTATION_FREEDOM`：未被可靠来源约束、不会改变科学语义的工程选择。
- `PROPOSED_CHOICE`：定向查证后仍缺失，但代码交付可以采用可逆候选时使用；注明候选依据、
  配置或替换边界和论文忠实度影响。

详细页码、章节、图表、公式以及仓库文件/符号定位统一登记在来源索引。数据、模型、训练和评测
描述只引用 `[S-...]`，不得写“如 Table X、Chapter Y、Section Z 或 page N 所示”一类导航句。

冲突处理同时使用两套优先级：

- 执行决策：用户明确要求 > 论文设置 > 版本匹配的官方仓库补充 > 可逆工程选择。
- 事实可信度：目标版本论文明确事实 > 版本和实验匹配的官方实现 > 其它官方版本 > 机械推导。

因此必须：

1. 最终实现采用用户明确要求。
2. 保留论文原始定义和精确证据。
3. 说明偏离影响哪些结果、可比性或“论文忠实复现”声明。
4. 官方仓库先核对 commit、目标实验和阶段；可补论文空白，但不能被标成论文事实。
5. 论文与仓库或论文内部不一致时，不静默选一个值；按
   [source_conflict_resolution.md](source_conflict_resolution.md) 查明适用范围并登记裁决。

用户要求不同的 `seq_len`、测试集合、目标变量、方程、注意力公式、损失或评测协议时，都是
科学/实验协议变体，必须进入冲突表并采用用户值。

## 3. 提取论文复现基线

每个数值、公式、变量、shape、split、超参、指标和模型组件必须紧邻简短 `source_id`；详细定位
只写在来源索引。论文没有的信息按影响分类为 `UNRESOLVED`、`IMPLEMENTATION_FREEDOM` 或
显式 `PROPOSED_CHOICE`，不要把候选值写成论文默认值。

### 论文身份与范围

- 标题、作者、venue/年份、版本、DOI/arXiv/URL、本地来源路径。
- 使用的正文、附录、补充材料和官方仓库范围。
- 目标实验对应的表、图、配置和报告结果；主结果、消融结果与泛化结果分开。

### 科学问题与任务语义

- 问题定义、方程、变量、单位、坐标系、初始/边界条件和约束。
- 输入、输出、训练 target、loss target、rollout 更新量和评估 target；角色不得混用。
- 单步、多步、自回归、反演、生成、重建或其它推理形式。

### 数据与样本

- 用户提供的数据路径逐项绑定到 data root、具体文件、glob 或 split；保留原始字面值、解析基准、
  验证状态、预期内容和 consumer。路径本身标为 `USER_REQUIREMENT`，路径内容观察不能冒充论文事实。
- 数据集版本和来源、原始文件/字段、样本数、分辨率和许可。
- train/validation/test split、索引/时间/对象隔离、采样和泄漏风险。
- 从原始数据到模型输入的转换、重采样、归一化统计量来源、mask 和 augmentation。
- 变量、通道或 shape 算术仅在需要时以内嵌表格记录，不生成独立 ledger 文件。

### 模型与算法

- 论文明确给出的模块、顺序、数学公式、参数共享、tensor shape/轴和初始化。
- 架构图只支持图中可见关系；`1 x 16` 之类标记必须先确认代表通道、kernel、矩阵或其它含义。
- 引用其它方法的组件不等于给出了完整实现；需要时回查引用或合法官方补证，否则保持未决。
- 不从概念图臆造 constructor、公开属性、代码容器、具体库、hidden size 或 tensor program。

### 损失与训练

- 每项损失的公式、prediction、target、权重、reduction、mask 和计算空间。
- optimizer、学习率、scheduler、batch、epoch/step、seed、precision、硬件、预算和 checkpoint。
- 每个训练参数绑定目标实验、训练阶段、更新对象及证据原文的适用范围。多阶段任务分别提取，
  不把输出场阶段的 optimizer/lr/epochs 自动传播到几何、SDF、latent 或内循环阶段；只有来源
  明确声明共享设置时才共用。split、validation 和 best/last checkpoint 规则同样不能互推。
- 论文只写损失名称或引用时，不自行发明公式。例如 “gradient regularization following X”
  不能改写为预测场平滑惩罚，除非可靠来源给出该公式。

### 推理与评估

- checkpoint 选择、输入构造、rollout、后处理、反归一化和保存语义。
- 指标完整公式、统计粒度、评估对象/split、baseline、表图映射和随机性报告。
- 结果表的缩放因子、单位、百分数、主结果与 ablation 值不能混用。

## 4. 统一规格中的可编码信息

以下内容直接属于科学复现规格，不构成独立 Implementation Contract 或 coder 视图。只提取用户、
论文或合法官方实现实际约束的信息，并为每个确定字段保留 `source_id`：

### 文件与配置

- 用户要求的文件清单和职责。
- 每个配置的路径、格式、flat/nested 布局、loader 和配置间依赖。
- 每个 key 的精确名称、类型、必填/default、含义、范围/单位、依赖和来源。
- 来源没有规定的配置组织属于 `IMPLEMENTATION_FREEDOM`，不要生成一套通用 schema。

### 模型与 Tensor Program

模型任务必须按 [model_structure_reconstruction.md](model_structure_reconstruction.md) 形成六个互补
视图：模块树、Tensor 数据流、数学算子、shape/语义、参数关系和行为不变量。类名、constructor、
forward 签名、公开属性等只在用户或来源确有约束时写成确定要求；否则由 coder 自主组织。来源只
给概念结构时，保留概念边界和未决内部，不从图示臆造隐藏算子。

### 数据链与脚本接口

- 每个用户数据绑定如何进入配置/CLI/loader，路径相对什么基准解析，缺失、类型错误或 schema 不符
  时如何显式失败；配置键名称未被来源约束时可以由 coder 选择，但不能忽略或替换绑定值。
- 原始字段到 batch/target 的步骤、split、索引、采样、resolution、layout、dtype 和归一化统计。
- 用户要求或来源规定的可导入类/函数、签名、参数、返回值、异常、import 副作用、main/CLI、
  配置加载、模块 import 和调用关系。
- 未被要求的 callable 命名和项目组织属于 `IMPLEMENTATION_FREEDOM`。

### 训练、评测与产物

- optimizer、loss、scheduler、batch/epoch/step、梯度更新、checkpoint 和 resume。
- 指标公式/reduction、split、checkpoint/预测输入、调用入口、统计范围和论文表图映射。
- 每个必需产物的路径、producer、serializer、字段、shape、dtype、单位和 consumer。
- 用户明确给出的验收项及其来源和实现落点。不得主动寻找隐藏 evaluator 或把评测器细节反向
  写成论文事实。
- 正式论文配置与用户明确要求的 smoke/quick override 分开。

## 5. 缺失信息处理

禁止：

- 用“常用值”“合理默认”“保守实现”补 batch size、学习率、inner-loop lr、seed 或 scheduler。
- 猜测网络层数、hidden size、归一化公式、气动系数公式、PDE loss 权重或 Radon 实现库。
- 把数据文件观察、benchmark 检查或官方仓库细节升级为论文事实。
- 因一项缺失就复制完整通用配置、脚本模板或目录树。

发现缺口后先按来源工作流查对应官方仓库的目标实验配置/符号；已检查仍缺失再分类处理。
对每个 `UNRESOLVED` 记录：字段、实验/阶段/模块、实现需要、影响、已检查来源和解决所需最小
信息，并区分 `blocks_build`、`blocks_run`、`affects_numerical_reproduction`。若用户已给出
值，它就是最终采用的 `USER_REQUIREMENT`，不是未决项；论文不同值或未说明状态仍进入冲突表。

对 `IMPLEMENTATION_FREEDOM` 只说明自由度边界和不能改变的语义，不替 coder 选择具体方案。

若缺口影响实现但存在一个或多个可逆候选，记录 `PROPOSED_CHOICE`：列出候选依据、默认选择、
配置键或替换接口、其它可行变体和忠实度影响。候选使 coder 可以继续交付，但不得提高为论文
事实。优先顺序为：版本匹配的官方实现候选 > 由已确认 shape/公式机械约束的候选 > 不改变科学
语义的常规工程选择。不得用候选填充论文结果、指标公式或数据 split 后声称精确复现。

未决项不自动阻止生成其它已确定模块。对未知拓扑、核宽或训练决策，优先采用显式必填配置、
可替换策略、多变体分支或标注清楚的候选实现，而不是中断整个交付或用空结构伪装成功。缺
validation split 不能默认用全部样本训练，缺 checkpoint 选择规则不能静默默认 final/best；若为
继续交付采用候选，必须显式可配置并降低 `paper_fidelity`。

## 6. 全文核验

完成初稿后逐条审计，并直接修订同一份 `reproduction_spec.md`：

1. 用户覆盖：当前任务输入每条明确要求均在覆盖表中，并已转化为完成或分类处理的信息需求。
   对用户原文和 handoff `inputs` 中的数据路径逐项做双向核对：输入中的每个路径都能定位到一个
   数据绑定，规格中的每个用户数据绑定都能追溯到实际输入来源。
2. 来源归属：没有把用户、仓库、数据观察或推断写成论文事实。
3. 证据回查：来源索引中的详细定位与原始内容一致；正文只引用 source ID，不夹带定位性描述。
4. 数值核对：单位、数量级、上下标、表格列、结果类型、split 和配置没有串行。
5. 语义核对：输入/输出/target/loss/metric 角色一致，模型数据流和 shape 可闭合。
6. 完整性：正文、表格、图注、算法框、附录、补充材料、消融和限制均按相关性检查。
7. 结构覆盖：模块六视图、配置、数据链、接口和产物已提取或正确分类；六视图互相一致。
8. 推断控制：没有因“任务书需要完整”而把缺失内容硬化成要求。
9. 去重：同一事实只在最合适位置完整描述，其它位置用 ID 引用。
10. 状态一致性：按字段 ID + 实验/阶段核对最终采用值、配置 default、训练协议与未决表；同一
    字段不得既未决又被下游采用。检查无跨实验/阶段参数传播、无仓库版本串用；必要时回原文
    或固定 commit 补查，不能靠添加免责声明保留冲突值。
11. 行为闭合：每个关键模型分支、共享关系、条件输入、训练目标和推理路径至少有一个可由 coder
    验证的行为不变量，不能只验证文件或 shape 存在。
12. 就绪度：分别判断 source_status、paper_fidelity 和 implementation_readiness；来源不完整不
    自动等于实现不可继续，候选也不能被宣称为 exact。
13. 路径闭合：每个用户数据绑定都同时出现在用户要求覆盖、数据与样本契约和运行数据链中，并有
    coder consumer、验证状态和失败行为；不存在用论文数据集名称或仓库默认路径替换用户路径的情况。

固定标题数量、最小字符数、稳定 ID 数量和文件存在性不能证明内容正确。核验结论基于证据覆盖和
冲突处理，不基于模板填充。

## 7. 统一复现规格结构

`reproduction_spec.md` 必须使用下面全部章节。不得删除、合并或用一句概述替代章节。某章经
全文核验后确实不适用，仍保留标题并写 `NOT_APPLICABLE`、不适用理由和判定依据。信息缺失但
会影响复现时写 `UNRESOLVED`，不能写成不适用。示例只说明信息粒度和证据格式，必须替换为
当前用户请求与论文的真实内容，严禁把示例值复制成事实。

同一事实只在一个章节完整定义，其它章节通过字段 ID、冲突 ID 或 source ID 引用，避免重复。
详细页码、章节、图表、公式、仓库文件和符号定位只出现在第 2 节来源索引；其它章节以 `[S-...]`
引用，不在描述句中重复论文导航信息。以下章节共同构成唯一科学复现规格，不产生独立 coder 视图。

### 7.1 标题

格式为 `# <论文简称>：<目标实验>复现规格`，必须同时识别论文和本次复现范围。

示例：

```markdown
# ExampleOperator：二维涡流单步预测实验复现规格
```

### 7.2 1. 文档控制、论文身份与来源范围

必须给出 canonical ID、唯一规格路径、标题、作者、venue/年份、版本、DOI/arXiv/官方 URL、
本地 PDF/全文路径，以及实际核验的正文、附录、补充材料和官方仓库范围。记录全文完整性和版本
匹配结论。

示例：

```markdown
## 1. 文档控制、论文身份与来源范围
| 字段 | 值 | 证据 |
|---|---|---|
| canonical_id | 2401.01234 | S-PAPER-ID |
| spec_path | .paper2code_work/2401.01234/reproduction_spec.md | 交付约束 |
| 目标版本 | arXiv v2，2024-03-01 | S-PAPER-ID |
| 来源范围 | 已核验正文与可用补充材料；详细覆盖见来源索引 | S-SCOPE-01 |
```

### 7.3 2. 决策优先级、证据标签与来源登记

必须分别写明执行决策优先级和事实可信度优先级，列出使用的证据标签，并登记每个外部来源的
URL、版本、详细定位、简短证据摘要、适用实验/阶段和用途。来源登记不能只写“见论文”。摘要要
准确表达原文支持的范围，不把解释扩写成证据。详细定位集中在本节；后续正文只引用 `source_id`。

示例：

```markdown
## 2. 决策优先级、证据标签与来源登记
执行决策：USER_REQUIREMENT > PAPER_FACT > OFFICIAL_REPO_DETAIL > 可逆工程选择。
事实可信度：目标版本 PAPER_FACT > 版本匹配 OFFICIAL_REPO_DETAIL > 其它官方版本 > INFERRED。
| source_id | 类型 | 版本与详细定位 | 证据摘要 | 适用范围 | 用途 |
|---|---|---|---|---|---|
| S-PAPER-01 | PAPER_FACT | v2，正文公式位置与页码 | 输出被定义为当前状态上的增量 | 目标实验/状态更新 | 定义状态更新 |
| S-REPO-01 | OFFICIAL_REPO_DETAIL | commit abc123，文件与符号 | 目标配置显式声明稳定项 | 目标实验/训练阶段 | 补充未写的实现值 |
```

### 7.4 3. 用户要求覆盖表

逐条保留用户原意，至少含 requirement ID、原始要求、类别、最终采用值、实现落点、状态、证据
标签和冲突 ID。名称、科学要求、目录、运行预算和禁止事项同等处理。不得把多条要求合并成无法
核对的一行。用户给出的每个数据路径必须有独立行并保留原始字面值；不能只写“使用用户数据”或
只在其它章节出现。

示例：

```markdown
## 3. 用户要求覆盖表
| ID | 原始要求 | 类别 | 最终采用值 | 实现落点 | 状态 | 冲突 |
|---|---|---|---|---|---|---|
| UR-04 | “输出未来 6 步” | 推理 | rollout_steps=6 | infer 配置与循环 | covered | C-02 |
| UR-05 | “数据位于 `<用户原始数据路径>`” | 数据路径 | 原值，不替换 | DB-01；loader 输入 | covered | 无 |
```

### 7.5 4. 目标实验、对照与验收边界

明确目标实验、训练和评估设置、baseline/ablation 身份、论文报告值及其单位或缩放、随机重复与
统计口径；目标实验在论文中的详细定位只写入来源索引，本节使用 source ID。区分论文目标、用户
验收目标和工程 smoke；不得把 smoke 成功等同于论文结果复现。

示例：

```markdown
## 4. 目标实验、对照与验收边界
| ID | 对象 | 设置 | 报告值 | 证据 | 本次判定 |
|---|---|---|---|---|---|
| EXP-01 | 论文主结果 | test split，3 seeds | RMSE=0.013±0.002 | S-PAPER-08 | 完整训练后比较 |
| ACC-01 | 工程 smoke | 1 batch，1 update | 不设精度阈值 | USER_REQUIREMENT | 只验证可执行性 |
```

### 7.6 5. 科学问题、方程与变量语义

写出问题定义、控制方程/目标函数、变量和单位、坐标系、初始条件、边界条件、约束，以及输入、
模型输出、训练 target、loss target、rollout state 和评估 target 的角色。公式必须定义符号，
引用精确证据；相同名称但物理语义不同的变量必须拆开。

示例：

```markdown
## 5. 科学问题、方程与变量语义
状态更新：u_{t+1}=u_t+Δu_θ(u_t,c) [S-PAPER-01]。
| 变量 | 角色 | shape | 单位 | 来源 |
|---|---|---|---|---|
| u_t | 模型输入/rollout state | [B,H,W,2] | m s^-1 | S-PAPER-01 |
| Δu | 训练 target/模型输出 | [B,H,W,2] | m s^-1 | S-PAPER-01 |
```

### 7.7 6. 数据与样本契约

给出数据集名称、版本、许可和来源；原始文件、字段、dtype、单位、shape/轴；样本构造、split
数量和精确规则；采样、重排、mask、augmentation、预处理、归一化/反归一化统计量的拟合范围；
train/validation/test 隔离及泄漏风险。开头必须先列“用户数据绑定”：每个用户路径一行，包含原始
字面值、角色、输入来源、解析基准、验证状态、预期 schema、consumer 和对应 requirement ID。
没有用户数据路径时才写 `NOT_PROVIDED`。数据实测只能标为数据观察，不能冒充论文事实。

示例：

```markdown
## 6. 数据与样本契约
### 用户数据绑定
| binding_id | 用户原始路径 | 角色 | 解析基准 | 验证状态 | 预期内容/schema | consumer | requirement |
|---|---|---|---|---|---|---|---|
| DB-01 | `<用户原始数据路径>` | data_root | `<用户指定基准或 UNRESOLVED>` | provided_unverified | 由下方数据契约定义 | dataset loader | UR-05 |

论文数据集身份与 DB-01 的本地执行绑定分别记录；DB-01 不因论文提供官方下载地址而被替换。

### 字段、样本与变换
| 阶段 | 输入字段 -> 输出 | shape/轴 | 统计量来源 | 证据 |
|---|---|---|---|---|
| load | velocity -> u | [T,Y,X,C] | 无 | S-PAPER-03 |
| normalize | (u-μ)/σ | 同上 | 仅 train 的 T,Y,X | S-PAPER-04 |
split：case 0-79 train、80-89 validation、90-99 test；按 case 隔离 [S-PAPER-05]。
```

### 7.8 7. 模型、算法与 Tensor Program

模型任务完整读取 [model_structure_reconstruction.md](model_structure_reconstruction.md)。本节不能只
写架构概述或一张组件表，必须按适用性给出六个互相校验的视图：

1. **总体职责与边界**：模型子任务、端到端输入输出、主干、条件分支、跳连、重复与变体。
2. **模块树**：父子层级、顺序、数量、普通/末 block 差异和来源约束的公开结构。
3. **Tensor 数据流**：tensor ID、producer、consumer、分支、合并、循环和先后顺序。
4. **数学算子**：公式、einsum/matmul、求解空间、归一化、残差、激活、gating 和稳定项。
5. **Shape 与变量语义**：shape、轴名、dtype、物理/统计语义、可选性和变体条件。
6. **参数关系与行为不变量**：共享/独立、初始化、冻结、梯度关系，以及输入敏感性、归一化、
   可重复性和关键组件实际参与 forward 等 coder 可验证行为。

六个视图必须引用短 `source_id` 并互相闭合。模块树中的关键模块应出现在数据流中或明确标为
辅助模块；数据流边应能在 shape 台账中解释；数学算子的轴与 shape 一致；共享关系应有行为
不变量。论文只给概念结构时只记录可见边界，不从术语或图形位置臆造 hidden size、kernel、代码
容器或完整 Tensor Program。

示例：

```markdown
## 7. 模型、算法与 Tensor Program

### 7.1 总体模型结构
模型由输入投影、4 个算子 block 和预测头串联组成；每个 block 接收上一层 token，并通过残差
连接回写主干。第 2 层另接条件分支，预测头只读取最终主干表示 [S-PAPER-06]。

### 7.2 模块树
Model
- input_projection：输入投影 [S-PAPER-06]
- blocks x 4：顺序执行；block 参数独立 [S-PAPER-07]
- prediction_head：只消费最后主干状态 [S-PAPER-06]

### 7.3 Tensor 数据流与数学算子
| step | 输入 tensor -> 运算 -> 输出 tensor | 分支/残差 | 来源 |
|---|---|---|---|
| M1 | x[B,H,W,C] -> input_projection -> h0[B,N,D] | 无 | S-PAPER-06 |
| M2-k | hk -> operator_k -> uk；hk+uk -> h{k+1} | 4 个独立 block | S-PAPER-07 |

### 7.4 Shape 与变量语义
| tensor | shape/轴 | 语义 | dtype/可选性 | 来源 |
|---|---|---|---|---|
| x | [B,H,W,C] | 输入物理场 | float；必需 | S-PAPER-02 |
| hk | [B,N,D] | 第 k 层 latent token | float；必需 | S-PAPER-06 |

### 7.5 参数关系与行为不变量
- input_projection 只定义和计算一次；4 个 block 不共享参数 [S-PAPER-07]。
- 改变 x 应改变输出；任一 block 输出干预应传播到 prediction_head。
- 初始化未被可靠来源约束，记为 IMPLEMENTATION_FREEDOM，不声称某初始化属于论文设置。
```

### 7.9 8. 损失、正则与优化算术

逐项给出 prediction、target、公式、权重、reduction 维度和顺序、mask、计算空间、单位、数值
稳定项及梯度流向。多阶段或内外循环需说明每一项更新哪些参数，是否 create_graph/detach。

示例：

```markdown
## 8. 损失、正则与优化算术
L = mean_b(sum_{t,x} mask·(ŷ-y)^2 / sum_{t,x} mask) + λ||θ||²。
| 项 | 权重 | reduction | 更新参数 | 证据 |
|---|---:|---|---|---|
| forecast_mse | 1.0 | 先空间时间均值，再 batch 均值 | θ | S-PAPER-09 |
| weight_decay | 1e-4 | optimizer 内部 | θ，不含 bias | S-PAPER-10 |
```

### 7.10 9. 训练阶段、调度与 Checkpoint 协议

按执行顺序列出阶段、依赖、冻结/解冻、数据 split、batch、epoch/step、optimizer、学习率、
scheduler、precision、seed、梯度累积/裁剪和停止条件。定义 checkpoint 的 producer、选择标准、
文件名、必需字段、resume 状态和 last/best 语义；正式训练与 smoke override 分开。

示例：

```markdown
## 9. 训练阶段、调度与 Checkpoint 协议
| stage | 输入依赖 | 更新对象 | optimizer | 结束条件 | 输出 | 来源 |
|---|---|---|---|---|---|---|
| T1 encoder | train split | encoder+latent | Adam, 1e-3 | 100 epochs | encoder_last.pt | S-PAPER-11 |
| T2 decoder | T1 best | decoder；encoder frozen | AdamW, 2e-4 | 50 epochs | decoder_best.pt | S-PAPER-12 |
best 按 validation RMSE 最小选择；checkpoint 必含 model/optimizer/scheduler/epoch/config/RNG。
```

### 7.11 10. 推理、Rollout 与后处理

说明 checkpoint 选择与加载、输入构造、单步/多步/自回归循环、状态更新、边界强制、反归一化、
物理后处理、分块/拼接和输出保存。每一步写 shape 与累计误差相关语义；没有 rollout 时明确
`NOT_APPLICABLE` 及依据。

示例：

```markdown
## 10. 推理、Rollout 与后处理
加载 CKPT-BEST -> 用 train 统计量归一化 u_0 -> 连续 6 次调用模型 ->
u_{t+1}=u_t+Δu_t -> 每步重新施加周期边界 -> 反归一化后保存 [case,step,Y,X,C]。
来源：UR-04、S-PAPER-13。
```

### 7.12 11. 评测、统计与论文结果映射

给出每个指标的完整公式、预测/真值、单位或缩放、统计粒度、样本/时间/空间 reduction 顺序、
评估 split、异常值/零分母处理、seed 汇总与置信区间。把输出字段映射到目标论文结果的
`source_id`，区分主结果、消融、baseline 和用户验收阈值；正文不重复图表或章节编号。

示例：

```markdown
## 11. 评测、统计与论文结果映射
relative_L2_i=||ŷ_i-y_i||_2/||y_i||_2；先逐样本计算，再对 test 样本取均值。
| metric_id | 保存字段 | 单位/缩放 | 目标结果来源 | 公式来源 |
|---|---|---|---|---|
| MET-01 | relative_l2 | 原始比例；报告时另列 ×100 | S-PAPER-15 | S-PAPER-14 |
```

### 7.13 12. 环境、依赖、硬件与计算预算

列出论文明确的软件版本、依赖、精度、硬件、设备数、显存/内存、训练时长和随机重复。用户给定
环境或预算优先；未知项标记来源状态。区分论文正式运行环境和本次工程验证环境。

示例：

```markdown
## 12. 环境、依赖、硬件与计算预算
| 项 | 正式协议 | 工程验证 | 来源 |
|---|---|---|---|
| device | 4×A100 40GB | 用户指定 CPU smoke | S-PAPER-16；USER_REQUIREMENT |
| precision | UNRESOLVED | float32 | 论文未说明；smoke 为 IMPLEMENTATION_FREEDOM |
```

### 7.14 13. 工程接口、运行闭环与交付产物

本章仍属于统一科学复现规格，用于记录用户、论文或官方实现明确约束的工程接口和交付信息，
不构成独立 coder 视图。没有来源约束的代码组织留给 coder；不得为填满本章发明科学设置、函数
名称或配置 schema。必须包含以下四个子节中适用的内容。

#### 13.1 文件与配置

列出每个必需文件职责；每个配置 key 的名称、类型、必填/default、含义、单位/范围、依赖、正式
值、smoke override 和来源。来源没有约束配置组织时明确标为 `IMPLEMENTATION_FREEDOM`，但
coder 最终采用的 schema 必须集中定义，不能散落为互相矛盾的硬编码。每个用户数据绑定必须映射
到配置、CLI 参数或固定 loader 参数之一；键名可以属于工程自由度，用户路径的值和用途不属于
工程自由度，不能被默认值覆盖。

示例：

```markdown
### 13.1 文件与配置
| 文件 | 职责 | consumer | 来源 |
|---|---|---|---|
| model.py | 模型定义，不触发训练 | train.py/infer.py | USER_REQUIREMENT |
| key | type | required | 值/语义 | 来源 |
| rollout_steps | int | yes | 正式值 6；smoke 值 2 | UR-04 |
| data_path | path/URI | yes | 绑定 DB-01；运行时按其解析基准解释，不设替代默认值 | UR-05 |
```

#### 13.2 公开类、函数、CLI 与调用关系

列出 class/function 名、签名、参数类型和 shape、返回值、异常、import 副作用、CLI 选项和模块
调用关系。没有来源约束的命名不得伪装成论文要求，但 coder 必须在实现中固定并记录选择。

示例：

```markdown
### 13.2 公开类、函数、CLI 与调用关系
`build_model(config: Mapping) -> nn.Module`；不得读数据或启动训练。
`forward(x: Tensor[B,N,C], mask: Tensor[B,N] | None) -> Tensor[B,N,O]`。
调用链：train.main -> load_config -> build_datasets -> build_model -> train。
```

#### 13.3 数据链、运行入口与失败行为

把原始字段到 batch/target、模型调用、loss、checkpoint、推理和指标串成闭合链；列出正式入口和
smoke 入口、每个数据绑定的 consumer、路径解析基准、校验失败时的显式异常，禁止静默 fallback
改变科学语义。数据链必须从 `DB-*` 开始，使 coder 能直接看到应读取哪个用户输入；不能只从论文
数据集名称或示例文件名开始。

示例：

```markdown
### 13.3 数据链、运行入口与失败行为
DB-01（用户原始数据路径）-> 校验存在性与 schema -> case split -> train-only normalize -> batch(x,y) -> model(x) -> loss(ŷ,y)
-> checkpoint -> rollout -> inverse transform -> metrics.json。
路径不可访问、数据字段缺失、checkpoint 架构不匹配或 split 重叠时必须失败；不得改用仓库默认
路径、自动下载数据或合成数据。
```

#### 13.4 产物 Schema 与验收项

每个必需产物列出相对路径、producer、serializer、字段、shape、dtype、单位和 consumer；明确
目录创建、覆盖策略、best/last 区别和最小 smoke 产物。逐条映射用户验收要求，隐藏 evaluator
规则不得作为事实来源。

示例：

```markdown
### 13.4 产物 Schema 与验收项
| path | producer | 内容/schema | consumer | 来源 |
|---|---|---|---|---|
| checkpoints/best.pt | train.py | model, optimizer, epoch, config, RNG | infer.py | S-PAPER-12 |
| results/metrics.json | infer.py | metric_id,value,unit,n_samples | 报告 | USER_REQUIREMENT |
验收 AC-01：从 best.pt 在 test split 生成 MET-01；不得读取 test 拟合统计量。
```

### 7.15 14. 用户要求下的最终采用规格与冲突决策

以冲突 ID 记录用户要求、论文事实、官方实现、各自 source ID、适用版本/实验、最终决定、优先级
理由及对可比性和论文忠实度的影响。没有冲突也必须写“未发现实质冲突”并说明核验范围。不要
重复论文导航信息，只引用 requirement、field 和 source ID。

示例：

```markdown
## 14. 用户要求下的最终采用规格与冲突决策
| ID | 用户要求 | 论文事实 | 官方实现 | 最终采用 | 忠实度影响 |
|---|---|---|---|---|---|
| C-02 | rollout=6 [UR-04] | rollout=12 [S-PAPER-13] | 12 [S-REPO-04] | 6 | 用户实验变体；不直接比较论文主结果 |
```

### 7.16 15. 未决项、候选选择、工程自由度与明确排除项

每个 `UNRESOLVED` 写出字段、实验/阶段/模块、为何实现需要、已检查来源、构建/运行/忠实度/
数值复现影响和解决所需最小信息。每个 `PROPOSED_CHOICE` 写出候选依据、默认选择、可配置键或
替换接口、其它变体和忠实度影响；每个 `IMPLEMENTATION_FREEDOM` 写清 coder 可选择范围及不得
改变的科学语义。列出用户禁止项和不在本次范围的实验，防止 coder 扩张任务。

示例：

```markdown
## 15. 未决项、候选选择、工程自由度与明确排除项
| ID | 分类 | 实验/阶段 | 内容 | 继续方式 | 忠实度/数值影响 |
|---|---|---|---|---|---|
| U-01 | UNRESOLVED | EXP-01/T1 | seed 未被可靠来源约束 | 作为必填配置 | 影响精确轨迹，不阻止构建 |
| P-01 | PROPOSED_CHOICE | EXP-01/T1 | 两种稳定项均可闭合公式 | 配置 `stabilizer`，默认采用版本匹配仓库候选 | paper_fidelity=evidence_aligned |
| F-01 | IMPLEMENTATION_FREEDOM | 全部 | 日志库 | coder 自选并记录 | 不得改变指标算术 |
明确排除：不运行未被用户要求的消融，不下载第三方复现代码。
```

### 7.17 16. 完整性核验结论与 Coder 交接

逐项声明用户覆盖、来源归属、模型六视图、公式/shape、数据泄漏、阶段依赖、接口与产物闭合是否
通过；列出未决和候选 ID，并分别给出 `source_status`、`paper_fidelity`、
`implementation_readiness`、`status` 和 `paper_repro_handoff`。记录唯一规格路径，并声明 coder
接收的是该文件的完整磁盘内容，不再生成第二份任务书或 JSON 契约。用户提供过数据路径时，必须
额外声明数据绑定数量、全部 binding ID 及其 consumer 均已核对；不能只用“用户要求全部覆盖”概括。

示例：

```markdown
## 16. 完整性核验结论与 Coder 交接
- 用户要求：12/12 covered；冲突 C-02 已按用户要求裁决。
- 用户数据绑定：1/1 covered；DB-01 已保留原始路径并映射到 dataset loader。
- 科学与实现链：data -> model -> loss -> train -> checkpoint -> inference -> metric 已闭合。
- 模型六视图：模块、数据流、算子、shape、参数关系和行为不变量一致。
- source_status=verified_fulltext；paper_fidelity=evidence_aligned。
- implementation_readiness=ready_with_configurable_choices；status=partial；handoff=true。
- 未决 U-01 与候选 P-01 均有继续方式，不阻止代码交付。
- 唯一规格：.paper2code_work/2401.01234/reproduction_spec.md。
- handoff：将上述文件读回的完整内容交给 onescience-coder。
```

## 8. 状态与交接

- `success`：论文身份和目标版本可靠，用户要求全部覆盖，目标实验的科学与实现链闭合，关键内容
  有直接证据或正确分类。
- `partial`：规格可靠且可交付，但来源覆盖、实现细节或数值复现存在明确不确定性。只要
  `implementation_readiness` 为 `ready` 或 `ready_with_configurable_choices`，就继续交给 coder。
- `failed`：无法唯一识别目标，且用户要求与允许的官方材料不足以形成不误导的可实现规格。

交接前必须创建 `.paper2code_work/<canonical-id>/`，将唯一规格写入该目录的
`reproduction_spec.md`，再从磁盘读回并验证：路径严格匹配、文件非空、统一规格结构已覆盖、
不适用项含理由、未知项含处理策略、读回内容与 `reproduction_spec_content` 完全一致。落盘不一致
时先修正同一文件，不得把实现产物根目录中的同名文件作为替代。

同时从当前用户输入与 handoff `inputs` 重新枚举数据路径，并与磁盘规格中的 `UR-*`、`DB-*` 和
13.3 数据链做双向核对。任一原始路径缺失、被改写、没有 consumer 或没有验证/失败状态时门禁
失败；先修正同一规格，不得把该缺口留给 coder 自行猜测。

门禁通过后计算磁盘规格的 SHA-256，将 `reproduction_spec_path`、完整
`reproduction_spec_content`、`reproduction_spec_sha256`、冲突和分类未决项一起交给
`onescience-coder`。散列放在交接回执中，不在规格文件内存自己的散列，以免形成自引用。
`paper_repro_handoff` 由 `implementation_readiness` 决定，不由全文完整度或 `status=partial`
单独决定。`PROPOSED_CHOICE` 必须按规格暴露配置或替换边界；`IMPLEMENTATION_FREEDOM` 可由 coder
在不改变规格语义的前提下决定。coder 不得静默把 `UNRESOLVED` 变成论文默认值。
