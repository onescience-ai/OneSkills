## description

为State Parse 过滤后 PBMC 扰动数据选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

State Parse Biosciences 人类 PBMC 单细胞扰动数据原语，绑定 parse_concat_full.h5ad 和 few-shot/zero-shot TOML，保留供体、细胞类型与细胞因子划分以及 HVG/State 表示。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/State_dataset/State-Parse-Filtered`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：细胞表达或指定的 X_hvg/X_state、供体/细胞类型、cytokine/treatment、控制标记和明确的 split；保留原始细胞索引。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 选择一个 TOML 协议，在配置副本中重定位 datasets.parse。
4. 按 cell_type_clean、donor 或 donor_ct_clean 匹配组，再核对扰动和 control，验证 split 互斥。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

沿用所选 TOML：training 默认 parse=train，zeroshot 将整个组指定为 test，fewshot 为该组分别指定 val/test 扰动。例如 split_1_zeroshot 将 parse.B_Intermediate_Memory 整组留出。细胞类型、供体和 split_1..5 方案分别使用，不叠加为一个随机细胞划分。

obsm 的 X_hvg/X_state 是派生表示，不能与 X 的基因轴互换。不得将 TOML 中的组名未经映射直接匹配 obs。保留 CC-NC-4.0-License.txt 和 README 的使用限制；元信息 visibility=public 不改变数据条款。

## next_phase_recommendation

TOML 解析与路径重定位 → clean 分组和扰动集合映射 → 稀疏表达/所选 obsm → State 数据 adapter。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

组名或扰动不匹配时输出差异清单并修正配置映射，不能将未匹配细胞自动放回训练。内存不足时仅做元数据/分块读取。
