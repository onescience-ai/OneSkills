
## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/la-proteina`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/la-proteina`。训练样本主路径为 `dataset/`。dataset 下可见 pdb 和 pdb_train；顶层还有 AFDB、ca_model_weights、checkpoints_laproteina、vanilla_model_weights。

## data_schema
样本通常由蛋白序列、结构、训练划分和模型权重路径组成。

## task_usage
适用于蛋白结构生成、设计模型预训练和结构验证。

## integration_paths
先确认是训练集还是结构库，再将 PDB 或 AFDB 样本映射到模型输入。

## preparation_requirements
先检查 pdb_train 的训练划分和 AFDB 结构是否一致，再核对权重版本。

## consumption_interfaces
消费端通常需要序列、坐标、训练 split 和权重配置。

## operation_limits
不要把数据目录、数据库目录和模型权重目录混为一类；不要假设所有子目录都能直接作为训练样本；如果某个目录只是参考数据库，应先把它定位为外部依赖，再决定是否写入 datapipe。
