# 实例任务：参考数据审计与覆盖定义 @ 神经网络势长程静电自洽训练

- domain: matchem
- 骨架: matchem-reference-data-audit-coverage-definition-task
- 场景: matchem-neural-network-potential-long-range-electrostatic-training-scenario (神经网络势长程静电自洽训练)
- step_id: s01
- depend: []

## 场景研究主体
- 神经网络势长程静电自洽训练
- 关联论文: Self-consistent determination of long-range electrostatics in neural network potentials | doi:10.1038/s41467-022-29243-2

## 本实例步骤描述
审计结构、能量、力和目标状态的覆盖范围。

## 本实例执行 prompt
读取 {REFERENCE_DATA}，核对原始成员、近重复、异常、标签血缘和目标覆盖。本实例的候选窄域为论文体相水：64 个分子（192 个核、256 个 Wannier 中心）的立方周期盒，同一母 Config 沿 z 轴的 0、0.1、0.2 V/Å 成组比较；不得覆盖明确给定的范围。盒长取 `init.xyz`，温压和采样标签据真实血缘；高温、缺陷和界面覆盖单列，不能代替目标覆盖。

## 本实例输入槽
- {REFERENCE_DATA} | required=True | type=doc | var_name=参考量子化学或第一性原理数据 | 实际可读的组级文件清单；extxyz/npz/数据库导出只是可能的格式，不是文件位置或缺省数据。`datasets/scfnn-water-reference-v2` 提供版本、目录、组匹配和读取约定。
- {REFERENCE_PROVENANCE} 对应同一数据清单：发布版本、许可、哈希、母轨迹和 Config、场方向与量纲、采样条件、参考计算设置和标签来源。历史标签按论文 Methods 可追溯到 CP2K v7、revPBE0（25% 精确交换）、D3、GTH、TZV2P 和 400 Ry；须核实到实际数据，读已有标签不要求本地安装 CP2K。
- `D0`、`D0p1V`、`D0p2V` 各取同名 Config 的核/中心 XYZ、`init.xyz` 和力文件。按数据卡约定从 Å 转 Bohr、读取 Bohr 盒长，按 O,H,H 顺序对齐力并从 DFT 输出或元数据核实力单位。逐构型 E、应力及其约定另核，特征或导数不能替代原始成员。

## 本实例产出
- 数据审计：可追溯组/构型 ID、范围、文件和标签计数、弃用理由、核对结果、版本、哈希、许可和计算设置。
- 训练、验证、独立测试分组清单及摘要；训练端来源与其归一化拟合记录交 s02，独立持出组交 s03。仅从实际读取、审计通过的实物生成划分。

## 本实例质量门禁
- 训练验证测试严格隔离
- 标签计算设置可追溯
- 母轨迹及其母 Config 和三场响应不得跨集合；近重复构型跨组须纠正后再划分。缩放量只用训练组拟合，验证和测试沿用已冻结尺度。

## 可调资源（edge:resource，仅真实存在）
- datasets/scfnn-water-reference-v2：按版本和同名 Config 解析目标场组，组级文件、许可与标注均须有可读证据。

## 验收/缺失策略（继承场景）
- 无可读目标组、血缘、覆盖或匹配的必要 E/F/应力时，完整审计 BLOCKED；可单列已核对字段，不交空划分，不启动依赖完整审计的训练。待取得可读组级输入及标签证据后续接；论文 Source Data 和相邻材料势均不能填补缺项。
