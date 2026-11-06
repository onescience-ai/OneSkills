## description

为FoldBench full1515 多分子结构评测资源选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

FoldBench 本地 full1515_v20260821 结构评测原语，绑定 AF3 canonical inputs、目标/链映射、MSA registry 和 ground_truth_20250520，区分单体与各类界面评测及权限受限的 manifest。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/foldbench`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：target_category、assembly pdb_id、目标链/界面、canonical input、chain mapping、MSA/reference 路径和验证状态；不默认所有目标可执行。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 按 9 类目标各自 schema 读取，并保留 assembly 与链角色。
4. 逐项连接 canonical/chain mapping/MSA/参考；manifest 不可读时明确可验证目标范围。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

本包是评测资源，不提供本轮已验证的 train/test 划分。按目标类别和 assembly 分组，多个链/界面共享 assembly 时保留关联，避免将类别行随机拆分当独立样本。

manifest/foldbench_run_manifest.csv 与 manifest_metadata.json 当前权限不足，不能据此宣称完整运行清单验证成功。配体界面与其他界面的字段不同；MSA registry 只表示资源索引，引用存在性需逐项检查。

## next_phase_recommendation

目标类别/assembly → 原生与推理链映射 → 工具输入 adapter → 对应参考结构 → 分类别结构/界面评测。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

受限 manifest 时可基于可读目标表建立明确标记的局部索引，不冒称原始完整清单；缺参考或链映射的目标记录失败，不换成单体坐标代替。
