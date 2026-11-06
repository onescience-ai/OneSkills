## description

为scGPT 单细胞注释、整合与扰动基准集合选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

scGPT 本地单细胞基准数据原语，覆盖 BMMC、肺/COVID、胰腺、髓系/MS、PBMC 和 Adamson/Norman，区分 H5AD 表达层、子集标签及 reference/query、train/test 角色。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/scGPT`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：输入是有固定基因顺序的表达向量、所选基因标识和 batch；监督目标为对应细胞类型或扰动后的表达，附带 control/condition 与数据角色。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 根据实际列名映射细胞类型、batch、condition 与 control，明确 X/layers。
4. 保留已有数据角色；对扰动任务先固定 held-out perturbation 规则，再生成模型输入。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

保留 pancreas 的 demo_train/demo_test、myeloid 的 reference/query 与 BMMC 的 is_train。reference/query 不天然等价于监督 train/test。Adamson/Norman 应按扰动身份及组合泛化协议划分，不能简单随机拆细胞后宣称未见扰动评测。其余分割需明确协议。

根部 Immune_ALL_human.h5ad 为 0 字节，必须排除；perturbation 下同名文件非空，但不能无说明地替换。不能将不同子集的 cell_type/Celltype/celltype 自动混为一列，或在未核查基因顺序时拼接矩阵。

## next_phase_recommendation

子集与任务选择 → AnnData/10x 解析 → 基因标识及表达层核对 → scGPT adapter。GO 辅助文件与基因 ID 映射另行绑定，不能作为分类标签替代。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

空文件直接记录为不可用；某子集缺失表达层、标签或基因映射时，只交付该子集可确认的元数据，不自动借用其他子集补齐。
