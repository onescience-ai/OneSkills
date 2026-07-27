
## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/alphafold3`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/alphafold3`。顶层包含 alignDB、infer_input_data、jackhmmer_split、mmseqsDB、public_databases。

## data_schema
典型输入是多链蛋白、核酸或配体相关序列，输出依赖数据库检索和对齐输入。

## task_usage
适用于 AlphaFold 3 推理、数据库挂载和检索前处理。

## integration_paths
先确认是搜索库还是输入样本，再按 alphaFold3 的工作流分开处理。

## preparation_requirements
先检查数据库目录和输入目录是否分离，再核对 split 和索引是否完整。

## consumption_interfaces
消费端通常是 AF3 搜索、对齐和推理入口。

## operation_limits
不要把数据目录、数据库目录和模型权重目录混为一类；不要假设所有子目录都能直接作为训练样本；如果某个目录只是参考数据库，应先把它定位为外部依赖，再决定是否写入 datapipe。
