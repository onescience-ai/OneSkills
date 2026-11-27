# 实例任务：能量力应力与外推验证 @ 神经网络势长程静电自洽训练

- domain: matchem
- 骨架: matchem-energy-force-stress-and-extrapolation-validation-task
- 场景: matchem-neural-network-potential-long-range-electrostatic-training-scenario (神经网络势长程静电自洽训练)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- 神经网络势长程静电自洽训练
- 关联论文: Self-consistent determination of long-range electrostatics in neural network potentials | doi:10.1038/s41467-022-29243-2

## 本实例步骤描述
评估预测误差、外推和物理一致性。

## 本实例执行 prompt
在独立集上报告能量、力、应力误差和外推检测，不以训练误差或参考条件化诊断代替泛化。预测侧只能输入待测构型的核坐标、晶胞、外场和同一次训练配置；预测中心与 Ewald 场迭代，不能读持出 Wannier/DFT 标签作为输入。按模型契约核对核顺序、晶胞与场单位、尺度和状态摘要，记录残差、阈值、迭代上限及非有限或未收敛原因；实际输出逐构型保存并重开，然后才与参考配对。

## 本实例输入槽
- {REFERENCE_DATA} | required=True | type=doc | var_name=参考量子化学或第一性原理数据 | `datasets/scfnn-water-reference-v2` 的可读持出组及核实标签、血缘、数据版本和划分摘要。格式名不是文件或标签。
- {INDEPENDENT_VALIDATION_SPEC} 对应冻结的持出组、选择依据、指标及适用范围，和 s02 同一次冷重载的完整检查点清单、模型配置、尺度与摘要；分开预测输入和仅供事后比较的参考。

## 本实例产出
- 验证报告分列 E/F/应力、独立自洽、物理一致性、外推和独立重算证据；记录误差定义、聚合轴、单位、样本数、覆盖、分组、窗口与不确定度。不以无误差值的缺项冒充已验证。
- 失败构型清单：组及构型 ID、失败量或自洽/物理/域外原因、证据和适用限制。s04 仅在必要门禁通过时接收同一状态摘要、已验证范围及对应初态条件。

## 本实例质量门禁
- 独立集不参与调参
- 外推构型单独标记
- 按母组、构型、原子和分量核对预测与参考。E 明确每胞或每原子、能量零点与单位；F 核对同构型下总力、原子排序和坐标分量，不用扰动分量替代总力；应力核对张量顺序、拉压符号、单位、体积及 virial 定义，不以翻符号掩盖定义不匹配。


## 可调资源（edge:resource，仅真实存在）
- datasets/scfnn-water-reference-v2：以真实持出组和可匹配参考构型核对标签。
- models/scfnn：用 s02 同次状态；模型卡列出输入、冷加载及独立预测的适用边界。

## 验收/缺失策略（继承场景）
- 缺独立入口、同次状态、参考或单位/定义无法对齐时，受影响的量和必要门禁标为 BLOCKED。可继续记录已核实的数据或部件诊断，不能借作者示例状态、独立组调参或用近邻势填补。域外拒绝凭可核查证据单列，不泛化到已定义的目标域。
