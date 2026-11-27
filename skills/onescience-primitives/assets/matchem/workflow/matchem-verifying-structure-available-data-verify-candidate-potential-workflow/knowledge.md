# 工作流：matchem-verifying-structure-available-data-verify-candidate-potential-workflow

- domain: matchem
- 步骤数: 5
- 共用场景数: 1

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 核验结构与可用资料
- desc: 建立或复用 C12/C13 共用的优化原胞，核验初始几何、固定索引和 VASP 收敛。
- depend: []
- prompt: 核验 {OPTIMIZED_PRIMITIVE_CELL}、{C12_STRUCTURE}、{C13_STRUCTURE} 和 {HISTORICAL_DATA} 中的已有资料。没有合格复用原胞时，在已确认的计算范围内构建并用 VASP 优化，交付共用原胞和收敛证据。
- step_input:
  - {OPTIMIZED_PRIMITIVE_CELL} (required=False, type=doc, var_name=共用优化原胞, hint=提供同体系同约束原胞和同次收敛证据, default=)
  - {C12_STRUCTURE} (required=False, type=doc, var_name=C12 初始结构, hint=已有结构及来源，可供共用原胞核验, default=)
  - {C13_STRUCTURE} (required=False, type=doc, var_name=C13 初始结构, hint=已有结构及来源，可供共用原胞核验, default=)
  - {HISTORICAL_DATA} (required=False, type=doc, var_name=历史数据资料, hint=标明可用性和用途, default=)
- outputs: ['输入审计报告', '共用优化原胞及收敛证据', '几何检查与固定 Cu 清单']
- quality_gate: ['体系和原胞来源可追溯', '几何与固定 Cu 索引通过', '电子、离子收敛及可动原子残余力通过核验']

### s02 验证候选势能模型可用性
- desc: 核验或补充 DFT 参考标签，按来源分组划分数据，独立验证复用或新训练的 MACE 势。
- depend: ['s01']
- prompt: 核验 {TRAINING_DATA} 的来源、单位与完整性，必要时在已确认的范围及预算内补充 DFT/AIMD。按来源轨迹或构型族划分数据，基于独立能量误差、分元素力误差、最差构型和界面覆盖判定 {CANDIDATE_POTENTIAL} 或新训练 MACE 势的准入。
- step_input:
  - {TRAINING_DATA} (required=False, type=doc, var_name=训练验证数据, hint=已有 DFT 能量、原子力和来源，正式数据也可在授权范围内补充, default=)
  - {CANDIDATE_POTENTIAL} (required=False, type=doc, var_name=候选势能模型, hint=提供版本和训练信息, default=)
- outputs: ['模型验证报告', '独立测试指标', 'MD 准入结论']
- quality_gate: ['数据划分可追溯', '独立测试已完成', '适用范围已说明']

### s03 准备超胞与动力学测试
- desc: 由共用优化原胞构建两套 3×3×1 超胞，核对目标碳质量、逐原子固定映射和 LAMMPS 部署等价性。
- depend: ['s02']
- prompt: 按 {SUPERCELL} 和 {FIXED_CU_PER_CELL} 逐原子核验每套 288 个固定 Cu。两套输入仅改变目标碳质量，读回检查三斜晶胞和元素/模型映射，验证部署势能与逐原子力。
- step_input:
  - {SUPERCELL} (required=True, type=enum, var_name=面内扩胞倍数, hint=固定为 3×3×1, default=3x3x1)
  - {FIXED_CU_PER_CELL} (required=True, type=int, var_name=原胞固定铜数, hint=底部两层共 32 个, default=32)
- outputs: ['C12/C13 超胞', '固定 Cu 映射', '晶胞和类型读回检查及 LAMMPS 能量/力比对记录']
- quality_gate: ['扩胞原子数正确', '逐原子验证每套 288 个固定 Cu', '两套仅目标碳质量变化', '部署能量和力在约定容差内一致']

### s04 执行 2 ps 短时验证
- desc: 软件依赖、固定原子、控温及续算预检通过后，用 LAMMPS + MACE 分别执行 2 ps 短测。
- depend: ['s03']
- prompt: 在授权范围内事前确认共同系综、温度（如适用）、时间步、采样和预算。两套预检通过后分别运行 {TEST_DURATION_PS} ps，核查有效时间、原子数、结构、温度、能量、固定 Cu 位移、适用域及续算。关键条件缺失时停止受影响步骤。
- step_input:
  - {TEST_DURATION_PS} (required=True, type=float, var_name=短时测试时长, hint=每种同位素 2 ps, default=2.0)
  - {TARGET_TEMPERATURE} (required=False, type=float, var_name=目标温度, hint=优先用已给且核实的温度；获明确自主授权时按证据定案，缺依据则停门；其余按确认流程, default=None)
- outputs: ['C12 测试轨迹', 'C13 测试轨迹', '运行质量报告', '温度和能量输出、运行日志、重启文件和续算记录']
- quality_gate: ['模型正常加载', '约束持续有效', '轨迹与续算材料可用', '无未解释异常']

### s05 形成验证结论与后续建议
- desc: 汇总结构、模型和两套动力学证据，逐项签收并归档。
- depend: ['s04']
- prompt: 逐项标注 PASS、PARTIAL、REJECT 或 BLOCKED 并附归档证据。记录上游失败位置、影响及最后健康产物，按证据判定是否具备进入 {LONG_RUN_GOAL} 的条件。
- step_input:
  - {LONG_RUN_GOAL} (required=False, type=str, var_name=长时目标, hint=未确认时留空, default=)
- outputs: ['验收判定', '复现归档及文件校验清单', '风险与限制说明', '后续采样建议']
- quality_gate: ['结论与证据一致', '短时结果未被过度解释', '后续范围需用户确认']

## 使用本工作流的场景（场景→工作流映射）
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
