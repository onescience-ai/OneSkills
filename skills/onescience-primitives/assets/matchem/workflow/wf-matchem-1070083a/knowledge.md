# 工作流：wf-matchem-1070083a

- domain: matchem
- 步骤数: 5
- 共用场景数: 1

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 核验结构与可用资料
- desc: 核对 C12/C13 结构、DFT 收敛状态、AIMD 数据、训练数据和历史资料，区分正式输入与参考资料。
- depend: []
- prompt: 审计 {C12_STRUCTURE}、{C13_STRUCTURE} 和 {HISTORICAL_DATA}，输出正式输入清单、异常排除项和待确认问题。
- step_input:
  - {C12_STRUCTURE} (required=True, type=doc, var_name=C12 初始结构, hint=提供结构及来源说明, default=)
  - {C13_STRUCTURE} (required=True, type=doc, var_name=C13 初始结构, hint=提供结构及来源说明, default=)
  - {HISTORICAL_DATA} (required=False, type=doc, var_name=历史数据资料, hint=标明可用性和用途, default=)
- outputs: ['输入审计报告', '结构质量检查', '待确认清单']
- quality_gate: ['结构来源可追溯', '异常 AIMD 数据已标识', '正式输入已确认']

### s02 验证候选势能模型可用性
- desc: 基于已确认的训练、验证和测试数据，提出候选势能模型训练或复用方案并完成独立验证。
- depend: ['s01']
- prompt: 基于 {TRAINING_DATA} 和 {CANDIDATE_POTENTIAL}，说明训练或复用判断、独立测试、最差构型和适用范围。
- step_input:
  - {TRAINING_DATA} (required=True, type=doc, var_name=训练验证数据, hint=含能量力和数据来源, default=)
  - {CANDIDATE_POTENTIAL} (required=False, type=doc, var_name=候选势能模型, hint=提供版本和训练信息, default=)
- outputs: ['模型验证报告', '独立测试指标', 'MD 准入结论']
- quality_gate: ['数据划分可追溯', '独立测试已完成', '适用范围已说明']

### s03 准备超胞与动力学测试
- desc: 构建 C12/C13 的 3×3 面内超胞，核对三斜晶胞、元素映射、模型映射及底部两层 Cu 固定约束。
- depend: ['s02']
- prompt: 准备 {SUPERCELL} 超胞，依据 {FIXED_CU_PER_CELL} 核对固定 Cu 映射、元素类型、晶胞表示和模型加载条件。
- step_input:
  - {SUPERCELL} (required=True, type=enum, var_name=面内扩胞倍数, hint=固定为 3×3×1, default=3x3x1)
  - {FIXED_CU_PER_CELL} (required=True, type=int, var_name=原胞固定铜数, hint=底部两层共 32 个, default=32)
- outputs: ['C12/C13 超胞', '固定 Cu 映射', '提交前预检报告']
- quality_gate: ['扩胞原子数正确', '固定 Cu 数为 288', '晶胞与类型映射正确']

### s04 执行 2 ps 短时验证
- desc: 在模型和输入预检通过后，分别执行 C12/C13 的短时动力学，检查运行质量和续算能力。
- depend: ['s03']
- prompt: 在 {TEST_DURATION_PS} 的短时测试中，按经确认的温度和采样方案执行 C12/C13 动力学并报告有效采样、温度、能量、约束、轨迹和续算能力。
- step_input:
  - {TEST_DURATION_PS} (required=True, type=float, var_name=短时测试时长, hint=每种同位素 2 ps, default=2.0)
  - {TARGET_TEMPERATURE} (required=False, type=float, var_name=目标温度, hint=由用户确认温度, default=None)
- outputs: ['C12 测试轨迹', 'C13 测试轨迹', '运行质量报告']
- quality_gate: ['模型正常加载', '约束持续有效', '轨迹与续算材料可用', '无未解释异常']

### s05 形成验证结论与后续建议
- desc: 汇总模型与短时动力学证据，判定是否具备进入长时采样的条件，并说明当前结论边界。
- depend: ['s04']
- prompt: 基于短时验证结果，判定是否可进入 {LONG_RUN_GOAL}；区分已证实、待确认和不可回答事项。
- step_input:
  - {LONG_RUN_GOAL} (required=False, type=str, var_name=长时目标, hint=未确认时留空, default=)
- outputs: ['验收判定', '风险与限制说明', '后续采样建议']
- quality_gate: ['结论与证据一致', '短时结果未被过度解释', '后续范围需用户确认']

## 使用本工作流的场景（场景→工作流映射）
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
