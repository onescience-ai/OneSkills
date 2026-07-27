
## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/HyenaDNA`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/HyenaDNA`。目录下有 genomic_benchmark、species、hg38 和 nucleotide_transformer 等分支；benchmark 子目录按任务名称组织训练/测试数据。

## data_schema
典型样本是序列、标签和任务划分，部分任务还会带染色体或物种元信息。

## task_usage
适用于启动子识别、增强子预测、基因组分类、物种分层和长序列语言建模。

## integration_paths
先根据 benchmark 名称确定任务，再选择 FASTA/片段化序列或 token 化输出；如果任务是长序列模型，应显式控制截窗和分块策略。

## preparation_requirements
先确认 train/test 目录和任务标签口径，再核对序列长度和物种分布。

## consumption_interfaces
消费端通常需要序列 token、位置编码和标签或分类目标。

## operation_limits
不要把数据目录、数据库目录和模型权重目录混为一类；不要假设所有子目录都能直接作为训练样本；如果某个目录只是参考数据库，应先把它定位为外部依赖，再决定是否写入 datapipe。
