
## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/esmfold`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/esmfold`。顶层仅见 data 和 weight 两个目录，适合做推理或复现的依赖挂载。

## data_schema
通常输入是蛋白序列或 FASTA，输出是结构预测或中间特征。

## task_usage
适用于 ESMFold 推理、结构预测和模型复现。

## integration_paths
应按推理资源包处理，先确认权重版本，再决定是否需要额外序列数据。

## preparation_requirements
先检查 weight 是否完整，再确认 data 目录中是否包含所需的缓存或参考输入。

## consumption_interfaces
消费端通常是 ESMFold 模型入口和序列批处理脚本。

## operation_limits
不要把数据目录、数据库目录和模型权重目录混为一类；不要假设所有子目录都能直接作为训练样本；如果某个目录只是参考数据库，应先把它定位为外部依赖，再决定是否写入 datapipe。
