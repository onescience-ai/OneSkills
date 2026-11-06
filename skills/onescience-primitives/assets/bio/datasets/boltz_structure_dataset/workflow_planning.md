## description

为Boltz 结构训练与推理输入资源包选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

Boltz 本地 RCSB/OpenFold 结构及 MSA 资源原语，绑定 Manifest、结构 NPZ、MSA NPZ、CCD/mols 和 FoldBench YAML 推理输入，区分下载缓存与可用训练资源。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/Boltz_dataset`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：结构任务输入 Manifest/Record 和对应 Structure/MSA/CCD；推理任务输入所选 YAML/A3M/化学实体。输出特征必须绑定具体 Boltz 数据类型版本。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 先区分训练结构、推理 YAML 和缓存，选择明确 manifest/输入清单。
4. 核对 structure/MSA 引用、链 ID 与化学字典；重定位 YAML 路径后做样本级特征验证。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

本地 manifest 未在本轮核实官方 train/validation/test 协议；记录来源、cluster_id 和时间筛选规则，由消费配置绑定。FoldBench 推理输入是评测来源，不能无说明混入训练。

必须验证结构→chain→MSA 的引用一致性及化学字典版本。YAML 中 MSA 有绝对本地路径，迁移时在输入副本中重定位并核对存在性。validation/boltz_adapter_report.json 当前无读取权限，因此不能宣称整个适配包已验证通过。

## next_phase_recommendation

Manifest/Record → Structure/MSA/化学组件 → Boltz 特征 adapter；推理为 YAML 实体/链和 MSA 映射 → 对应版本解析器。可复用已有 boltz_data_pipeline，但需保留本地来源约束。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

引用文件缺失或适配报告不可读时列出目标及依赖差异，只报告已验证样本；不以 official_train_download/.cache 充当完整训练数据。
