## description

为State SE-167M-Human smoke 单细胞与基因 embedding选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

State SE-167M-Human 本地 smoke 数据原语，绑定四个 scbasecount H5AD 样例与基因 embedding PT，明确基因映射、样例范围和无通用监督标签边界。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/State_dataset/SE-167M-Human-smoke`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：表达向量、基因索引/符号、accession，及经过验证的对应基因 embedding；不自动提供 cell_type 或 perturbation 标签。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 先确认当前任务仅使用四文件 smoke 范围，核对共同基因轴。
4. 检查 PT 的对象布局和基因映射后再连接表达，不凭顺序连接。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

四个 SRX 文件表示来源入口，不是预设四折或 train/test。下游划分按 accession/研究来源固定，并记录 smoke 范围。

四文件基因维度相同仍需核对索引顺序。不能将基因 embedding 当作细胞 embedding，也不能从 PT 文件名推断 token 字典。

## next_phase_recommendation

H5AD 基因轴检查 → PT 布局与基因键确认 → 显式 ID join → SE 表示 adapter。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

embedding schema 或映射未确认时可只交付 H5AD 结构检查结果，保留缺失项；不生成随机 embedding 替代。
