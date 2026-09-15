# 工作流：wf-matchem-923c2045

- domain: matchem
- 步骤数: 4
- 共用场景数: 1

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 Cu-N4 基底与局域配位构型生成
- desc: 读取 Cu-N4 单原子催化剂结构，保持 Cu 原子孤立，按 Cu-NxBy 候选替换第一配位层中的 N/B 并生成统一表面模型。
- depend: []
- prompt: 读取 {CATALYST_STRUCTURE}，生成 {COORDINATION_SET}；核对 Cu 是否为孤立位点、周期边界是否引入非目标 Cu-Cu 相互作用以及每个候选的电荷/自旋设定。无法确认的构型写 BLOCKED。
- step_input:
  - {CATALYST_STRUCTURE} (required=True, type=doc, var_name=基底结构, hint=CIF/POSCAR 及活性位说明。, default={CATALYST_STRUCTURE})
  - {COORDINATION_SET} (required=True, type=list[str], var_name=配位候选, hint=Cu-NxBy 构型列表。, default={COORDINATION_SET})
- outputs: ['配位候选 POSCAR', '局域配位与电荷/自旋清单', '构型检查日志']
- quality_gate: ['每个候选只有定义内的第一配位层变化', 'Cu 单原子孤立性和表面真空层满足设定', '所有候选的超胞、表面取向和边界条件一致']

### s02 吸附构型搜索与 VASP 弛豫
- desc: 对 CO2、COOH*、CO*、CHO* 和 H* 在每个 Cu-NxBy 位点枚举合理吸附姿态，使用统一 VASP 设置弛豫并计算吸附能。
- depend: ['s01']
- prompt: 使用 VASP 按 {DFT_CONFIG} 对 {COORDINATION_STRUCTURES} 上的 {INTERMEDIATE_SET} 枚举并弛豫吸附构型；保留最低能和近简并构型，记录吸附能、键长、配位变化和收敛信息。
- step_input:
  - {COORDINATION_STRUCTURES} (required=True, type=doc, var_name=配位结构集合, hint=s01 输出。, default={COORDINATION_STRUCTURES})
  - {INTERMEDIATE_SET} (required=True, type=list[str], var_name=中间体集合, hint=反应路径和 HER 对照。, default={INTERMEDIATE_SET})
  - {DFT_CONFIG} (required=True, type=object, var_name=DFT 设置, hint=统一的 VASP 参数。, default={DFT_CONFIG})
- outputs: ['弛豫后吸附结构', '吸附能与关键键长表', '电子结构/电荷分析输入']
- quality_gate: ['每个候选和中间体至少有可解释的吸附构型搜索记录', '吸附能参考态、真空层、覆盖度和自旋设置一致', '近简并构型未被无记录地丢弃']

### s03 CO2→CH4 与 HER 竞争路径自由能分析
- desc: 以 *COOH、*CO、*CHO 等中间体建立 CO2→CH4 路径，计算电位相关自由能；同时分析 *H/HER 和 CO 脱附竞争，并对关键质子化步骤进行能垒计算或明确缺失。
- depend: ['s02']
- prompt: 根据 {ADSORPTION_RESULTS} 和 {ELECTROCHEMICAL_POTENTIAL} 构建 CO2→COOH→CO→CHO→CH4 与 HER 路径；用 {BARRIER_METHOD} 处理关键步骤。区分吸附能、自由能和能垒，缺失项写 MISSING。
- step_input:
  - {ADSORPTION_RESULTS} (required=True, type=doc, var_name=吸附结果, hint=s02 输出。, default={ADSORPTION_RESULTS})
  - {ELECTROCHEMICAL_POTENTIAL} (required=True, type=float, var_name=电位, hint=相对于 RHE 的统一参考。, default={ELECTROCHEMICAL_POTENTIAL})
  - {BARRIER_METHOD} (required=False, type=enum, var_name=能垒方法, hint=若没有过渡态计算能力，不得把热力学自由能, default=NEB)
- outputs: ['反应自由能图', '限制步骤与选择性竞争分析', '关键能垒或缺失项清单']
- quality_gate: ['每个自由能修正项、参考电位和温度均有记录', 'CH4 选择性结论同时考虑 CO 脱附和 HER 竞争', '没有能垒结果时不得宣称动力学选择性已被证明']

### s04 位点稳定性与选择性排序
- desc: 结合局域配位保持、结构重构/脱附风险、关键中间体结合强度和反应路径，形成 Cu-NxBy 候选的 CH4 选择性—稳定性排序。
- depend: ['s03']
- prompt: 依据 {REACTION_ANALYSIS} 对 Cu-NxBy 候选排序；将 CH4 路径、HER 竞争、位点稳定性及验证数据分列，输出推荐、淘汰和待验证候选，不把单一描述符当作充分证据。
- step_input:
  - {REACTION_ANALYSIS} (required=True, type=doc, var_name=反应分析结果, hint=s03 输出。, default={REACTION_ANALYSIS})
  - {VALIDATION_DATA} (required=False, type=doc, var_name=验证数据, hint=实验性能和局域配位表征。, default={VALIDATION_DATA})
- outputs: ['Cu-NxBy 候选排序', 'CH4 选择性设计规则', '需实验验证的优先候选']
- quality_gate: ['排序依据可回溯到原始吸附/自由能/能垒数据', '推荐位点的结构与配位环境明确', '计算预测和实验观察分开报告']

## 使用本工作流的场景（场景→工作流映射）
- Cu-NxBy_单原子位点CO2到CH4选择性优化
