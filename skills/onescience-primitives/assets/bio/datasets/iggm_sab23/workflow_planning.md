## description

为IGGM SAb-23 抗体/纳米抗体设计输入集选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

IGGM 本地 SAb-23-H2-Ab/Nano 抗体设计数据原语，绑定 native FASTA/PDB、prot_ids 与含 X 掩码的 CDR design FASTA，区分重轻链/抗原及两子集不同的 PDB 目录名。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/IGGM/dataset`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：prot_id、子集、native 链序列/结构、design FASTA、掩码/待设计位置与抗原条件；输出为独立设计，不把掩码输入当预测。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 先按 Ab/Nano 选择正确 native PDB 目录和链角色。
4. 核对 X 掩码与 native/结构的残基位置，确认 CDR 编号后建立设计条件。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

Ab/Nano 是对象类型分组，各 CDR 目录是同一复合物的设计设置，不是 train/test。未发现已核实 split 清单；若学习则按复合物/同源簇分割，保证同一 native 的掩码变体同组。

两子集 PDB 目录名不同，loader 必须显式分派。文件名中的 NA 不代表实际轻链。X 掩码必须保留给设计 adapter，不能删除后改变序列与坐标长度。

## next_phase_recommendation

prot_ids → native FASTA/PDB 角色核对 → design 掩码与坐标映射 → 抗体设计 adapter；生成结果另存，不覆盖 native。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

编号或结构映射未确认时保留输入并输出缺失链/残基清单；不要自动补造轻链或将 X 随机替换成氨基酸。
