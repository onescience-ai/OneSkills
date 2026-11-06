## description

为Replogle-Nadig 多细胞系遗传扰动数据选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

State 本地 Replogle-Nadig 遗传扰动单细胞数据原语，覆盖 HepG2、Jurkat、K562、RPE1 及 replogle 汇总文件，区分 raw/normalized 版本和扰动、细胞系、基因轴。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/State_dataset/Replogle-Nadig-Preprint`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：基因表达向量、固定基因轴、扰动 gene/sgID、控制状态、细胞系、原始细胞索引和显式 split。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 明确选择单细胞系原始/归一化文件还是汇总视图，不重复计数。
4. 固定 perturbation/control、基因映射与 held-out 规则，检查跨视图和跨 split 重复。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

本地文件名没有统一 train/test 定义。按实验协议固定干预基因/细胞系 holdout，排除汇总视图与源文件之间的重复泄漏，不将五文件随机混合划分。

raw 与 normalized 文件不可在未统一处理口径时直接合并。各文件基因维度不同，汇总文件也不能被当成四个文件的简单拼接。所有尺度拟合和 HVG 选择应明确训练来源。

## next_phase_recommendation

文件和视图选择 → var 基因轴映射 → 遗传扰动与控制定义 → held-out gene/cell_line 划分 → State/扰动 adapter。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

控制或归一化定义缺失时只保留可确认的字段和视图，不生成带科学解释的响应比较；优先完成任务协议再训练。
