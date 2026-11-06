## description
为 eSEN 氧化物小样本数据制定按 oxide/polymorph 分组的读取、微调准备与评测交接方案。

## when_to_use
用户需要本地 oxides 微调包、氧化物能量/力/应力评估或多晶型组合泛化验证时使用。

## inputs
数据根目录、manifest、目标模型/checkpoint 字段要求、单位与参考能量协议、可用资源和评测需求。

## outputs
保留的 238/28/29 split、30 组映射、ASE 数据 adapter、标签单位/shape 契约及按组指标清单。

## procedure
1. 读取 manifest，核对三个库的行数和逐行 oxide/polymorph 分组。
2. 用 ASE 恢复结构，确认 energy/forces/stress 及其有效性。
3. 保留已输出的 eV/Angstrom^3 应力，核对符号/Voigt 顺序和其它标签单位。
4. 将训练 split 映射到模型输入，仅从 train 计算适配统计。
5. 小批检查邻居图、标签和损失权重；保留 val 作选择、test 作最终测试。
6. 交接按 oxide/polymorph 的误差和样本量报告要求。

## constraints
组不能跨 split，test 不参加训练统计；未知可选标签不启用监督。小样本结果必须保留样本量与本地覆盖边界。

## next_phase_recommendation
将 ASE reader、分组 manifest 和单位契约交给数据标准化/编码技能，再按具体任务交给微调或推理技能。

## fallback
模型不支持 stress 时保留结构/能量/力路径并明确目标减少；ASE 读取失败时先以只读 SQLite 检查 schema 与缺失项，不改源库修补或随机重划数据。
