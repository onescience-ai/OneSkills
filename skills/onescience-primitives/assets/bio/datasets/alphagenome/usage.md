
## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/AlphaGenome`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/AlphaGenome`。reference 下可见 HOMO_SAPIENS、MUS_MUSCULUS 等物种参考，v1 下有 train 和 ALL_FOLDS 结构。

## data_schema
典型样本包括参考序列、fold 划分、训练片段和物种标签。

## task_usage
适用于基因组基础模型、跨物种建模、参考序列对齐和训练/验证切分。

## integration_paths
先根据 v1 或 reference 目录确定任务版本，再按物种或 fold 划分数据。

## preparation_requirements
先检查 reference 物种是否满足任务要求，再核对 train 与 ALL_FOLDS 的版本对应关系。

## consumption_interfaces
消费端通常读取序列、物种标识、fold 编号和训练片段。

## operation_limits
不要把数据目录、数据库目录和模型权重目录混为一类；不要假设所有子目录都能直接作为训练样本；如果某个目录只是参考数据库，应先把它定位为外部依赖，再决定是否写入 datapipe。
