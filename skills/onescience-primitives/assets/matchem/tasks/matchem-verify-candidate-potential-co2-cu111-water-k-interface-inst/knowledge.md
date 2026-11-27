# 实例任务：验证候选势能模型可用性 @ CO2_Cu111_12C13C_MACE_LAMMPS动力学验证

- domain: matchem
- 骨架: matchem-verify-candidate-potential-energy-model-availability-task
- 场景: matchem-co2-cu111-water-k-interface-12c-13c-kinetics-verification-scenario (CO2_Cu111_12C13C_MACE_LAMMPS动力学验证)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
- 关联论文: （源场景未提供）

## 本实例步骤描述
准备可追溯的 DFT 参考数据，对复用或新训练的 MACE 势完成独立验证并判定 MD 准入。

## 本实例执行 prompt
审计 {TRAINING_DATA} 和 {CANDIDATE_POTENTIAL} 中实际提供的资料。必要时在已确认的计算范围和预算内用 DFT 单点或 AIMD 补充目标界面标签，完成数据划分、独立测试和准入判定。

## 本实例输入槽
- {TRAINING_DATA} | required=False | type=doc | var_name=训练验证数据 | hint=已有 DFT 能量、原子力和来源，正式数据也可在授权范围内补充 | default=
- {CANDIDATE_POTENTIAL} | required=False | type=doc | var_name=候选势能模型 | hint=提供版本和训练信息 | default=

训练验证数据需真实目标构型与配对 energy/forces、完整 cell/PBC、原子顺序、frame_id 或 source_run/source_step 身份规则、数据成员/哈希、单位及 DFT 方法/收敛/异常排除来源。参考 split 的读取与身份、原始标签血缘、测试独立性和训练暴露分别核对；无重复 ID 不证明独立。未核实字段保持未验证，不能用通用参考首帧或模型预测替代目标标签。

沿 s01 实际交接的结构身份、轨迹、条件、原始步号和原子顺序核对每帧 eV 总能量、逐原子三分量 eV/Å 原始力、收敛证据和排除账本。补算时记录 DFT 设置与能量定义，核对与现有标签的可比性。此前审计的历史导出仅核对了能量和解析力列，原始力与逐帧收敛仍待核验。两条历史轨迹均跨三个分区，最邻近帧可只隔一步，不能作为轨迹级独测。

复用已登记的 `mace-mp-0-medium-finetune-portable.pt` 时，按 models/mace/usage.md 核对权重与配套 JSON，并用原生 ScaleShiftMACE、float64 和 strict=True 重构。保留原配置的元素表、cutoff、head、原子参考能和 scale/shift。权重文件名只用于定位资产，目标微调与训练暴露范围须有独立证据。

软件模块/发行版本、实际安装入口及 CPU 导入失败边界从 tools/onescience-mace 消费；其 planned 部署目录尚未安装，不得从那里加载软件。完整配置与模型位置由模型卡承载，软件位置由工具卡承载。

在实际执行域核查解释器、运行库路径与 `torch` 导入的退出状态。HIP 构建按实际依赖核对 SONAME/ABI 和 `ldd` 结果，再检查原生 `e3nn.o3.Irreps`、MACE 导入、严格重构，以及目标周期帧的能量与位置梯度力。依赖缺失时记录首错与最后健康权重和配置。

## 本实例产出
- 模型验证报告
- 独立测试指标
- MD 准入结论

模型报告交付同身份权重/config、序列化与原生导入/strict 的分别状态、真实目标 energy/forces 的执行记录、独立测试/最差构型与适用域，或对应未验证原因。向 s03 交接明确 MD 准入结论；缺正式结构、独立标签或原生加载失败时 MD 为 BLOCKED，可行来源/划分审计与失败交付继续。

按来源轨迹或构型族分组划分训练、验证和独立测试集。相邻帧、扩胞副本和仅质量不同的同位素副本须归入同一集合。选模及调参前冻结独测清单，记录候选及母模型各训练阶段的暴露范围与未核验项。事前确定能量归一化、力分量及聚合、单位、阈值和适用域。报告独立测试的能量误差、分元素力误差、最差构型和目标界面覆盖情况，附按帧及原子 ID 对齐的参考与预测值，依据这些证据签发 MD 准入结论。

## 本实例质量门禁
- 数据划分可追溯
- 独立测试已完成
- 适用范围已说明

文件可读、79 个有限张量的历史序列化检查与元素覆盖仅证明工程资产；不证明原生 strict、目标 forward 或独立科学精度。目标能量/力的单位、归一化与阈值须有依据；参考推理不记为独立测试通过。原生导入若在可选天气/分布式依赖的 GPU 属性查询失败，保留错误、最后健康权重/config 和工具所有者修复/部署依赖；不伪造 GPU、使用 shadow 模块、放宽 strict 或换其他模型。输入和科学模型均通过后方可进入超胞/MD，短时 2 ps 不证明同位素效应。

## 可调资源（edge:resource，仅真实存在）
- models/data-efficient-machine-learning-potentials-modeling-catalytic
- tools/reaxnet-polarizable-long-range-neural-network-potential

- models/mace：mace-mp-0-medium-finetune-portable 两文件身份、完整 model_config、原生重构参数及物理模型限制，见 ../../models/mace/usage.md。
- tools/onescience-mace：原生软件实际包入口、版本、加载 API 和可选 GPU 依赖失败边界，见 ../../tools/onescience-mace/usage.md。

既有方法资源继续提供通用方法，不能作为正式数据来源或所选模型的替代身份。

## 验收/缺失策略（继承场景）
- acceptance: 模型须有真实独立测试、最差构型及适用域说明，工程加载与科学精度分别判定；结构、模型和 MD 各项据证据标注 PASS、PARTIAL、REJECT 或 BLOCKED，不以文件检查替代科学准入。
- missing_policy: 缺真实目标标签、正式结构或原生导入失败时，保留最后健康权重/config、具体错误与影响范围、工具所有者责任及恢复条件；继续可行数据/血缘审计，科学精度保持未验证、MD 准入明确阻塞，不制造替代标签或冒称运行恢复。
