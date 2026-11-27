# 实例任务：分子动力学或结构探索验证 @ 神经网络势长程静电自洽训练

- domain: matchem
- 骨架: matchem-molecular-dynamics-structure-exploration-validation-task
- 场景: matchem-neural-network-potential-long-range-electrostatic-training-scenario (神经网络势长程静电自洽训练)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- 神经网络势长程静电自洽训练
- 关联论文: Self-consistent determination of long-range electrostatics in neural network potentials | doi:10.1038/s41467-022-29243-2

## 本实例步骤描述
在目标条件下进行短程验证和失效分析。

## 本实例执行 prompt
先核对 s03 通过的独立配对、目标覆盖及其模型摘要。仅在同一完整冷重载状态、可读真实初态及符合目标范围的可调用自洽入口就绪时，按已锁定条件选择最窄的短程 MD 或结构扰动。沿用 s03 的核顺序、晶胞、外场和单位；记录有效参数、迭代残差及上限、有限性、实际有序帧或扰动序列及质量诊断。静态扰动须使用带收敛阈值和迭代上限的自洽单构型入口；作者 MD 与参考条件化诊断不能替代它。s03 未放行时不启动，不以场序列或演示轨迹代替。

## 本实例输入槽
- {MD_CONFIG} | required=False | type=object | var_name=分子动力学验证配置 | 真实初态 ID、范围、条件、体系尺寸、参考及依据；如采用 MD，给出有依据的温压系综、时间步和窗口。缺省展示值（300 K、10,000 步）不构成此实例的工况与预算，不套入默认时标。

## 本实例产出
- MD/探索轨迹：可重开、有序的真实帧或扰动及对应运行参数、单位和诊断窗口。
- 适用域结论：证据仅适用于已支持条件和观察窗口；验证门禁、非物理构型、数值失稳、域外与未知参考分开。
- PASS/REJECT/BLOCKED

## 本实例质量门禁
- 不把势函数置信度当作量子或实验验证
- 软件版本和命令完整
- 零步积分或仅有输出字段不算轨迹，非有限结果、未收敛或非物理构型不能作为稳定性证据。已证实失稳或域外按原因 REJECT；缺参考、s03 门禁未满足或入口不可调用时 BLOCKED，记录恢复所需的同次检查点、配对证据、真实初态或入口条件。

## 可调资源（edge:resource，仅真实存在）
- models/scfnn：模型身份、冷重载与支持范围沿用 s03。
- tools/scfnn-train-test：MD 构建和使用条件；不复用演示状态或二进制。

## 验收/缺失策略（继承场景）
- 仅凭实际轨迹或扰动证据、质量诊断和适用范围判定 PASS/REJECT/BLOCKED；如未运行，保留上游最后健康产物与受阻决策，不报告 MD 或域外结论。
