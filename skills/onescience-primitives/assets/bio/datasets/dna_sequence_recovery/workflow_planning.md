## description

为DNA Next K-mer 序列恢复与扩展视图选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

Carbon 本地 DNA Next K-mer Prediction 评测数据，覆盖 bacteria/eukaryote/others 的序列后续 128 bp 目标，并单列 schema 不同的 eukaryote/test_new 基因序列视图。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/sequence-recovery`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：标准输入 sequence、字符串 label、来源/物种元信息与实际上下文；test_new 只交接其具名字段和未确认的目标定义。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 先根据是否有 label 区分标准 test 和 test_new，不自动合并。
4. 标准任务固定截断方向、生成长度和指标；扩展视图先验证坐标与任务说明。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

三个标准配置均为 test，无现成训练划分。test_new 是候选数据视图，不是天然 validation 或独立测试版本；未核实去重前不能合并规模。

缩短标准输入时依据 README 采用 left truncation，保留靠近续写点的末端，并报告实际上下文长度。不能把 label 拼进模型输入，或把 gene_sequence 无依据截成 128 bp 目标。

## next_phase_recommendation

标准 test → tokenizer 和左截断策略 → DNA 续写 adapter；test_new 走单独视图核验，任务契约明确后再接入。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

模型容量不足时明确选择较短上下文并保留输入末端；test_new 任务不明时仅登记结构，不将其冒充标准 benchmark。
