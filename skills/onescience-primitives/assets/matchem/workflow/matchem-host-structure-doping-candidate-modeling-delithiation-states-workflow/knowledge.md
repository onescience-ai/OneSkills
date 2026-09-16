# 工作流：matchem-host-structure-doping-candidate-modeling-delithiation-states-workflow

- domain: matchem
- 步骤数: 5
- 共用场景数: 1

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 母体结构检查与掺杂候选建模
- desc: 读取 Li[Ni0.91Co0.09]O2 结构，检查层状堆垛、元素占位和 Li/Ni 位点；按统一比例生成 Mg、Al、Ti、Ta、Mo 掺杂候选，并记录每个替位构型。
- depend: []
- prompt: 读取 {PARENT_STRUCTURE}，核对 Li、Ni、Co、O 的元素顺序和层状结构；按照 {DOPANT_SET} 与 {DOPANT_RATIO} 生成候选。无法由输入确定的氧化态、电荷补偿或替位位点写 BLOCKED，不得猜测。
- step_input:
  - {PARENT_STRUCTURE} (required=True, type=doc, var_name=母体结构文件, hint=CIF/POSCAR 及来源。, default={PARENT_STRUCTURE})
  - {DOPANT_SET} (required=True, type=list[str], var_name=掺杂集合, hint=元素、氧化态和替位位点。, default={DOPANT_SET})
  - {DOPANT_RATIO} (required=True, type=list[float], var_name=掺杂比例, hint=统一化学计量定义。, default={DOPANT_RATIO})
- outputs: ['候选结构 POSCAR/CIF', '构型与化学计量清单', '建模日志']
- quality_gate: ['所有候选结构元素守恒且无明显原子重叠', '层状母体和掺杂位点可追溯', '电荷补偿未定义时输出 BLOCKED 而非静默假设']

### s02 不同脱锂状态下的 VASP 结构弛豫
- desc: 对母体和每个掺杂候选，在满锂与目标深度脱锂状态下使用统一 VASP 设置弛豫晶胞和原子位置，保存总能、晶格参数、体积和应力。
- depend: ['s01']
- prompt: 使用 VASP 按 {DFT_CONFIG} 对 {CANDIDATE_STRUCTURES} 在 x=1 和 x={LI_CONTENT} 下分别弛豫；记录 OUTCAR、CONTCAR、总能、晶格和应力，不得比较不同收敛标准的结果。
- step_input:
  - {CANDIDATE_STRUCTURES} (required=True, type=doc, var_name=候选结构集合, hint=s01 输出。, default={CANDIDATE_STRUCTURES})
  - {LI_CONTENT} (required=True, type=float, var_name=脱锂状态, hint=Li_x 化学计量数。, default={LI_CONTENT})
  - {DFT_CONFIG} (required=True, type=object, var_name=DFT 设置, hint=统一的 VASP 参数。, default={DFT_CONFIG})
- outputs: ['弛豫后 CONTCAR/POSCAR', '总能与晶格参数表', '应力和收敛日志']
- quality_gate: ['电子步和离子步均达到设定收敛标准', '所有候选使用一致的泛函、U、赝势、ENCUT 和 K 点标准', '弛豫后无明显非物理短键或未处理的自旋/电荷状态']

### s03 Li/Ni 混排与结构稳定性计算
- desc: 在母体和掺杂结构中枚举对称不等价的 Li/Ni 交换构型，计算混排能；同时提取脱锂引起的晶格参数、体积和层间距变化。
- depend: ['s02']
- prompt: 基于 {RELAXED_STRUCTURES} 构造对称不等价 Li/Ni 混排构型，计算 Emixing=E(mixed)-E(layered)，并统计 Δa、Δc、ΔV、层间距变化；明确 Emixing 的符号约定。
- step_input:
  - {RELAXED_STRUCTURES} (required=True, type=doc, var_name=弛豫结构集合, hint=s02 输出。, default={RELAXED_STRUCTURES})
  - {LI_CONTENT} (required=True, type=float, var_name=脱锂状态, hint=用于比较相同 x。, default={LI_CONTENT})
- outputs: ['Li/Ni 混排能表', '晶格应变与体积变化表', '结构稳定性对比图']
- quality_gate: ['混排构型与母体参考结构具有相同化学计量', '能量差采用统一参考零点并保留结构文件', '不得把较低混排能误报为更稳定的层状结构']

### s04 弹性与开裂风险代理指标分析
- desc: 对通过结构稳定性门限的候选计算弹性响应或应力—应变指标，结合脱锂晶格各向异性和体积变化形成开裂风险代理评分；计算不稳定时只保留可解释的应变指标。
- depend: ['s03']
- prompt: 对 {STABLE_CANDIDATES} 计算 {MECHANICAL_METHOD}，提取弹性常数/应力响应、各向异性、脱锂体积变化和层间距变化；将结构不稳定、未收敛或超出适用域的结果标记 REJECT 或 BLOCKED。
- step_input:
  - {STABLE_CANDIDATES} (required=True, type=doc, var_name=稳定候选集合, hint=s03 输出，包含结构稳定性门限结果。, default={STABLE_CANDIDATES})
  - {MECHANICAL_METHOD} (required=False, type=enum, var_name=力学分析方法, hint=可选弹性张量或有限应变应力响应；需与结构, default=elastic_tensor)
- outputs: ['弹性或应力—应变指标', '脱锂应变各向异性表', '开裂风险代理评分及其组成']
- quality_gate: ['弹性常数满足所采用晶体稳定性判据或明确标记失败', '风险评分可追溯到混排能、ΔV 和各向异性等原始量', '开裂风险代理不得表述为已完成实验断裂强度测量']

### s05 候选排序与实验/文献交叉验证
- desc: 按层状结构稳定性、低应变和力学风险代理指标排序，优先输出前 3 个候选；若提供验证数据，则对晶格、相变、循环或裂纹趋势进行独立对照。
- depend: ['s04']
- prompt: 依据 {ANALYSIS_TABLES} 对候选排序；有 {VALIDATION_DATA} 时逐项对照，无验证数据时明确写出计算范围和未验证项，输出 PASS、REJECT 或 BLOCKED。
- step_input:
  - {ANALYSIS_TABLES} (required=True, type=doc, var_name=分析结果表, hint=s03-s04 输出。, default={ANALYSIS_TABLES})
  - {VALIDATION_DATA} (required=False, type=doc, var_name=验证数据, hint=实验或文献数据；缺失时不做实验结论。, default={VALIDATION_DATA})
- outputs: ['候选排序与推荐理由', '结构—掺杂—应变关系', '可复现实验配置与最终判定']
- quality_gate: ['推荐候选的原始结构、参数和日志齐全', '未提供实验数据时不得声称已验证开裂强度或循环寿命', '每个结论都能回溯到 PDF 证据、计算结果或明确假设']

## 使用本工作流的场景（场景→工作流映射）
- LiNiCo_高镍层状正极掺杂结构优化与应变风险分析
