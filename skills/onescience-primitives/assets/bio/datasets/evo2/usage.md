
## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/evo2/data_mini`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/evo2/data_mini`。data_mini 下包含 chr20.fa、chr21.fa、chr22.fa 及 gz 版本、genome_data 和 preprocessed_data。

## data_schema
样本通常是超长染色体序列、token 化结果和窗口化训练片段。

## task_usage
适用于 Evo2 预训练、长上下文语言建模、基因组切窗和序列回归任务。

## integration_paths
优先使用专用 tokenizer 和预处理后的窗口数据；若直接读 FASTA，必须先定义 token 化、截窗和 loss mask。

## preparation_requirements
先检查染色体 FASTA 是否完整，再确认预处理数据与 tokenizer 版本一致。

## consumption_interfaces
消费端通常需要 tokens、position_ids、seq_idx 和 loss_mask。

## operation_limits
不要把数据目录、数据库目录和模型权重目录混为一类；不要假设所有子目录都能直接作为训练样本；如果某个目录只是参考数据库，应先把它定位为外部依赖，再决定是否写入 datapipe。
