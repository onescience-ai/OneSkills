## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/DNABERT-2_dataset`；未设置 `ONESCIENCE_DATASETS_DIR` 时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/DNABERT-2_dataset`。访问前检查根目录与所选 CSV 是否可读。

接入参数至少应明确数据根目录、分支和任务，例如分支 `GUE`、任务 `prom/prom_300_all`；对应训练文件为 `<root>/GUE/prom/prom_300_all/train.csv`。选择 v2 本地分支时，路径为 `<root>/GUE_v2/GUE/<task>/train.csv`，不能省略内层 `GUE`。只有明确选择示例模式时才读取 `<root>/sample_data/{train,dev,test}.csv`。

## data_schema

按实际表头分派解析：`sequence,label` 使用单序列读取；`enhancer,promoter,label` 使用序列对读取。检查缺列、空序列、空标签和解析失败行，记录文件名与行号。不要为 EPI 伪造一个缺失的 `sequence` 列，或只保留其中一个输入。

解析端应保留原始序列与标签，并附加来源分支、相对任务路径和 split。附加信息属于读取端元数据，不是原始 CSV 已有字段。

## task_usage

单序列任务可用于 DNA 序列编码器加分类头的适配与评测；EPI 用于增强子—启动子序列对分类。应先选定任务，再确定输出类别数、tokenizer、最大输入长度和指标。不能因为数据位于 `DNABERT-2_dataset` 就假定其只允许 DNABERT-2 消费，其他模型也需通过同样的输入契约检查。

`sample_data` 可检查 CSV 解析、tokenization 与 batch 组装，样本量不足以支持正式基准结论。

## integration_paths

单序列路线为 CSV → 保留任务和 split 的样本 → DNA tokenizer → 单序列 batch → 分类输出。EPI 路线为 CSV → 保持 enhancer/promoter 配对的样本 → 支持配对输入的 tokenizer 或模型 adapter → 序列对 batch → 分类输出。

缓存应按分支、任务、split、tokenizer 版本和长度策略区分。EPI 的字段顺序、分隔方式及两段序列的长度预算须写入 adapter 配置。模型只支持单序列时，先定义并验证配对编码协议，再接入 EPI。

## preparation_requirements

1. 确认所选分支、任务的三个 split 均存在，并逐个核对表头。
2. 统计各 split 的样本数、空值、标签值域、序列长度和字符集合；抽样结果只能用于初步适配。
3. 获取任务标签释义与评测口径，固定标签映射和分类头维度，核对 dev/test 标签是否兼容。
4. 检查 tokenizer 对 `R` 等 IUPAC 模糊碱基的支持，以及 token 长度是否超出模型限制；记录归一化、未知字符和截断策略。
5. 检查跨 split 完全相同的单序列或 EPI 序列对并报告结果；发现重复时保留原始划分，后续清理作为单独的数据版本处理。

## consumption_interfaces

本卡定义逻辑消费契约，不提供专用 loader API。CSV 可由标准库 `csv.DictReader` 或兼容的表格读取器解析。

| 消费类型 | 必需逻辑输入 | 路径派生信息 |
| --- | --- | --- |
| 单序列分类 | `sequence`、`label` | `branch`、`task`、`split`、源文件与记录位置 |
| 序列对分类 | `enhancer`、`promoter`、`label` | `branch`、`task`、`split`、源文件与记录位置 |

模型端输入由选定 adapter 决定，通常包括 token ID、模型需要的 mask 和映射后的分类标签。不能假设所有 DNA tokenizer 都有相同的特殊 token、padding 或配对接口。推理输出应保留来源信息和原始标签，便于回查预测。

## operation_limits

读取源数据时保持只读，预处理产物写入独立目录。忽略 `.efileUploading` 与 `.efilePart` 文件，不将未完成上传分片当作有效数据包。不得静默跨分支替换缺失文件、拼接编号目录、改变 split 或以示例集替代完整测试集。

本原语交付数据接入知识，不附带转换、训练或推理脚本。实际模型兼容性与完整数据质量需由后续 adapter 和验证过程确认。
