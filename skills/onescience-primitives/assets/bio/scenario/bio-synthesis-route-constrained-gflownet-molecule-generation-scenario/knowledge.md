# 场景：B58

- domain: bio
- type: paper_scenario
- 算力: [] (is_one_hpc=[])
- 模型: ['RGFN']
- 工具: ['RDKit']

## 研究意图（agent_task_prompt）
你是本任务的生物信息学负责人。请先核验默认输入“reaction_templates.json”、模型/权重标识“rgfn.pt”及相关版本和许可，再根据1篇关联论文与可用计算环境，完成“合成路线约束的GFlowNet分子生成”：在反应模板和可购砌块约束下生成高奖励分子，适用于可执行的先导发现。研究对象是靶点口袋、参考配体、分子约束和候选小分子库，重点检查化学有效性、目标性质、结构新颖性、可合成性和多目标权衡，核心验收指标为可合成率。请在执行前提交对任务的理解、数据和标签血缘、拟采用的方法与模型选择、资源/时间估算、独立验证、质量门禁、风险、失败分支和需要确认的信息；不要把目录中的模型、权重、示例数据或历史结果直接视为已验证答案。正式结果必须保留全量输入、失败样本、随机性和版本记录，提供独立测试、分层性能、不确定度和适用域证据；保持元素/键级/立体化学合法，明确活性、脱靶、ADMET、相似性和合成约束；生成分子不能被表述为已验证药物。若证据、数据或资源不足，必须明确标记无法回答并提出最小补充方案，不得用推测、缺失标签或未经验证的高分结果补足结论。最终交付可复现的结果数据、报告、日志和校验信息，并对每项交付给出 PASS、PARTIAL、REJECT 或 BLOCKED。

这里的 `reaction_templates.json`、`rgfn.pt` 是源需求中的示例标识，不是已核验的官方接口或必备资源。采用下述固定 RGFN 实现时，先按实际化学库和训练/恢复分支绑定；从头训练不要求预存权重。原研究目标、质量门禁和科学结论边界继续适用。

## 客户端请求
- task_title: 合成路线约束的GFlowNet分子生成
- request: 请完成“合成路线约束的GFlowNet分子生成”的可复现研究任务：以“reaction_templates.json”作为默认输入示例，围绕在反应模板和可购砌块约束下生成高奖励分子，适用于可执行的先导发现获得可验证的可合成率结果和可用于后续研究的输出。请先评估数据、模型和资源是否足够，自主提出并论证执行方案；方案确认前不得把实现细节、历史案例或目录默认值当作不可变科学结论。
- scientific_context: 本场景研究靶点口袋、参考配体、分子约束和候选小分子库，希望解决在反应模板和可购砌块约束下生成高奖励分子，适用于可执行的先导发现。化学有效性、目标性质、结构新颖性、可合成性和多目标权衡是主要科学关注点；关联论文用于界定任务背景和证据起点，不代表当前输入上的结果。
- desired_outcome: 得到与输入和任务约束一致、可追溯、可复核的合成路线约束的GFlowNet分子生成结果，包括标准化口袋/参考配体和候选分子的化学合法性、立体化学与去重报告、独立评估、可合成率统计、不确定度、失败案例和适用边界；不能支持的结论必须明确说明原因。
- executor_role: 执行者应作为具有生物信息学、机器学习、数据质控和可复现研究经验的负责人，把需求转化为可执行方案，主动识别数据泄漏、适用域、偏差和安全风险，并在关键科学口径或资源取舍需要决定时请求确认。

方法适用条件：以下专业说明对应 [RGFN 论文 v2][rgfn-paper] 和代码 `6ce59169f855ed18f34ba4e8279de93bee306e4f`。RGFN 是在反应模板与砌块定义的离散空间中构建分子；靶点条件通过所选性质/对接奖励进入本实现，不据此假定模型原生生成口袋条件三维坐标。活性、选择性和 ADMET 仍是需要定义指标、标签与独立证据的目标。

## 问题与适用性
本对象是提交给生物信息学执行者的完整需求书：只规定要解决的科学或业务问题、输入、预期能力、必须满足的约束和验收口径；执行者负责自主选择可行的方法、模型组合、工具、参数、资源、执行顺序和异常处理，并在正式运行前说明方案与风险。

## 工作流步骤（→workflow/→tasks）
- s01 分子设计目标定义

  **输入与化学库绑定**：按 [ReactionDataFactory][rgfn-factory]，`reaction_path` 读取 XLSX；`docking=True` 选择 `Reactions_Docking` / `Fragments_Docking`，否则选择 `Reactions_NoDocking` / `Fragments_NoDocking`。反应字段为 `Reaction`、砌块字段为 `Fragment`；另给 `fragment_path` 时从 CSV 的 `SMILES` 列读砌块。需求中的 JSON 若要接入，须显式转换并核对字段、反应实体与砌块身份，不能只改扩展名。保存代码版本、库文件 hash、原串→规范实体→实际索引映射，反应及 anchored 反应的实际顺序也要保存。

  固定版本的 [chemistry.xlsx][rgfn-chemistry] 已有 ZIP/XML 静态检查：工作簿 SHA256 为 `f9cf021ea34c45f4371d51d98b3465727b42ec921c33772e2c5986715ecc2a4d`；对接页 `Reaction` 有 64 个非空原串，砌块有 357 个非空原串、351 个不同原串。这些是源文件层统计，不能当作 factory 规范化后的砌块数、反应对象数或 anchored 反应数。实际运行应分别保存这些统计及有序列表。源码使用 `set` 去重，跨进程顺序可能不同；相同字符串集合不代表检查点索引兼容。

  **化学身份与证据**：先解析、sanitize，再明确规范化、异构 SMILES、同位素和立体化学的去重策略；保留原实体及反应前后原子映射，逐步检查元素、键级、价态与立体化学。可复用 [RDKit 既有能力说明](../../../matchem/tools/rdkit/references/core_capabilities.md)，但图合法性不能证明实验反应可行。[论文的隐式 SMARTS 反应][rgfn-paper]允许产物含来自未显式写入试剂的原子，不能按显式反应物/产物原子数差机械否决；应标注额外原子的来源、已知或待补的试剂及条件。

  论文对接库因 QuickVina2 缺少硼参数，将硼酸及其衍生物转为羰基碳标记 `13C` 的羧酸代理。分别保留真实砌块、代理结构/模板、回映射及采购身份，核验回映射前后的同位素与立体化学；不能将代理直接当采购实体，也不能推广成任意同位素替换。逐反应记录试剂、催化剂、溶剂、温度及保护/脱保护策略的缺项。轨迹可重放、图合法、逆合成获解、专家复核和实验合成是不同证据等级；前两项不能补齐实验配方。

  **对接分支的目标准备**：只在选择对接奖励时准备受体及对应坐标。论文 ClpP 基准从 `7UVU` 保留两个单体，移除复合抑制剂及其他溶剂/溶质；另存原始复合物、参考配体及处理血缘。固定 [DockingMoleculeProxy][rgfn-docking] 中官方 `ClpP.pdbqt` 的中心为 `[-38.127, 45.671, -20.898]` Å，box 为 `[17, 17, 17]` Å，绑定该受体坐标系；未知靶点或变换后的结构须重新定义口袋，不能沿用此 box，也不能把原始 mmCIF 当准备好的受体。
- s02 模型与性质条件准备

  **离散状态与训练目标**：状态记录当前构建分子/起始状态及反应上下文，合法动作受反应模板、可用砌块和锚点约束；明确起始砌块选择、反应应用、允许终止及步数限制。每条轨迹记录状态、反应、锚点、砌块索引、合法动作/终止与最终分子，供检查重放和多路径血缘。正终端奖励的目标是 `P(x)=R(x)/Z`；同一分子有多条构建路径时，终点概率是所有合法到达路径概率之和。轨迹平衡为 `Z·∏P_F=R(x)·∏P_B`，常用平方对数残差 `(log Z + Σlog P_F − log R(x) − Σlog P_B)²` 训练。不能将此目标解释成每步贪心最大化或局部均匀采样；见[论文方法][rgfn-paper]。

  **科学量与失败状态**：按 [DockingMoleculeProxy][rgfn-docking] 区分 raw energy `E`（通常更负更好）、代理值 `s=max(-E/norm,0)`（`norm>0`）与[指数奖励][rgfn-paper] `R=exp(beta*s)`；固定变换、归一化及 beta 后再比较。beta 增大使奖励分布更集中，不是对接置信度，也不能默认等于共享槽 `TEMPERATURE`。本版本 ClpP 配置的 `beta=4` 只是实例。无效结构、构象/对接失败或空 PDBQT 必须有独立状态，即便实现返回有限 `failed_score` 也不能计为成功；检查失效值经过变换后的奖励，不能从数值有限推断任务完成。

  **从头训练与恢复**：从头训练将检查点作为产物；恢复或已有模型推理才要求真实且兼容的检查点。按 [Trainer][rgfn-trainer] 核对实际支持的 model、optimizer 等保存/恢复状态，并另存 RNG、采样与未自动恢复的运行状态，不能宣称加载单个 `rgfn.pt` 就完整续跑。冻结代码/依赖、化学库 hash、规范化砌块及索引、反应/anchored 映射、模型结构、奖励/优化和采样配置；任何索引/配置不兼容都应先停止恢复并解释差异。
- s03 三维分子生成与采样

  此共享步骤名称在本场景绑定为**离散反应生成与外部构象准备**，保留原 Task 映射。先由 RGFN 输出分子图/SMILES 与构建轨迹，记录实际采样预算、种子、模型版本和条件，保留有效、无效、重复及约束失败记录；需求示例中的数量和温度不自动成为官方命令参数。随后按[对接实现][rgfn-docking]在外部进行构象、质子化及 Meeko/PDBQT 准备，再交 QuickVina。原分子、代理/对接分子、构象、PDBQT、能量与失败原因需逐实体关联；三维坐标有限性属于外部构象产物检查，不证明 RGFN 原生生成坐标。
- s04 性质过滤与候选排序

  **独立评价设计**：训练/调参结束后固定生成模型，独立随机新采样并冻结全队列，再作[独立逆合成评价][rgfn-paper]，不能只复评训练中挑选的高分子集。将生成策略/反应模板与规划 policy/模板分别登记，记录重叠、stock 身份/覆盖偏差及可比性；对各方法预先固定相同的搜索终止、深度、时间和迭代预算。规划使用共享可比库存并报告库存敏感性；生成时的砌块库和规划库存不能混为一谈。

  固定 AiZynthFinder 版本为 `21ff546d5f22331b078390a2f12dc04defc3f39c`。[官方下载器][aizynth-data]定义 `uspto_model.onnx`，将源 `uspto_unique_templates.csv.gz` 保存为 `uspto_templates.csv.gz`，将 Figshare 文件 `23086469` 保存为 `zinc_stock.hdf5`。核对 ONNX 输入特征、输出类别与模板行顺序、stock 的化学身份/许可证及配置引用。HDF5 规划库存不等于 RGFN 生成砌块；文件名或模型可加载不足以证明三者兼容。

  按[该版本 API][aizynth-api]设置 `target_smiles`，依次 `prepare_tree()` → `tree_search()` → `build_routes()` → `extract_statistics()`；逐目标保存准备、搜索、路线及统计的对应关系。须核对实际路线叶子全部满足 stock 才判 `solved`，`number_of_routes>0` 或结果文件存在本身不充分。分别记录获解、预算内未解、超时、准备/搜索错误及排除原因；以预先声明的全队列为分母，另报各状态和有效结构子集，不能静默删除错误或把预算内未解等同不可合成。

  对接分数与 MW 的相关性可能奖励更大分子，须结合 MW/QED 分层及预先规定的硬约束、软目标、归一化和权重报告，防止单目标分数掩盖多目标退化。步数上限或 SA 分数不能替代药物相似性、选择性、ADMET 与实验验证。筛选后的 top-k 用于优先级排序，全队列可合成性统计及失败记录仍独立保留。

## 关联论文
- RGFN: Synthesizable Molecular Generation Using GFlowNets | doi:

- [论文 v2][rgfn-paper]：方法/轨迹平衡、隐式试剂与硼代理、靶点准备、MW 混杂及独立逆合成评价。
- RGFN 固定版本源码：[化学输入 factory][rgfn-factory]、[化学工作簿][rgfn-chemistry]、[对接 proxy][rgfn-docking]、[训练与检查点][rgfn-trainer]。ClpP 的 beta 实例见同版本 [rgfn_clpp_docking.gin](https://github.com/koziarskilab/RGFN/blob/6ce59169f855ed18f34ba4e8279de93bee306e4f/configs/rgfn_clpp_docking.gin)。
- AiZynthFinder 固定版本：[公共资源规格][aizynth-data]、[搜索/路线 API][aizynth-api]；RDKit 图检查以现有能力说明及 [RDKit Book](https://www.rdkit.org/docs/RDKit_Book.html)为依据。

[rgfn-paper]: https://arxiv.org/html/2406.08506v2
[rgfn-factory]: https://github.com/koziarskilab/RGFN/blob/6ce59169f855ed18f34ba4e8279de93bee306e4f/rgfn/gfns/reaction_gfn/api/reaction_data_factory.py
[rgfn-chemistry]: https://github.com/koziarskilab/RGFN/blob/6ce59169f855ed18f34ba4e8279de93bee306e4f/data/chemistry.xlsx
[rgfn-docking]: https://github.com/koziarskilab/RGFN/blob/6ce59169f855ed18f34ba4e8279de93bee306e4f/rgfn/gfns/reaction_gfn/proxies/docking_proxy/docking_proxy.py
[rgfn-trainer]: https://github.com/koziarskilab/RGFN/blob/6ce59169f855ed18f34ba4e8279de93bee306e4f/rgfn/trainer/trainer.py
[aizynth-data]: https://github.com/MolecularAI/aizynthfinder/blob/21ff546d5f22331b078390a2f12dc04defc3f39c/aizynthfinder/tools/download_public_data.py
[aizynth-api]: https://github.com/MolecularAI/aizynthfinder/blob/21ff546d5f22331b078390a2f12dc04defc3f39c/aizynthfinder/aizynthfinder.py

## 验收与缺失信息策略
- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）

方法层建议（不是客户新增阈值）：执行前定义可合成率的队列/分母、获解判据、预算、约束与证据等级；缺关键化学条件或资源时，只签收有证据的层级并列出影响与最小补充方案。真实采购/保护基条件未明时，不能将反应构建轨迹交付为实验配方。计算获解和对接高分均不支持“已合成”“有实验活性”或“已验证药物”。

资源定位先按实际授权的 onestore 根与明确候选目录有界核验。已有本地审查只覆盖 `onedatasets/{matchem,bioinformatics-demo,GenScore}` 和 `onemodels/BUAA` 等指定范围，扫描达到上限且无命中；这既不证明全库缺资源，也不提供可用绝对路径。复用该范围限制，不重复全库扫描；未确认本地资产时，将上述固定版本的官方来源、文件名、格式、模型/模板/stock 兼容要求交给资源获取流程。缓存源码/元数据不等于 QuickVina、硬件、ONNX、模板、stock 或检查点已在执行节点就绪；大文件未核验时不编造 hash。资源状态与知识内容缺口分开记录。
