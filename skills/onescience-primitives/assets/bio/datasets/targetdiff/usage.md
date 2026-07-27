
## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/targetdiff`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/targetdiff`。训练/样本主路径为 `data/`。data 下按靶点目录分层，examples 提供 1h36、3ug2 等示例文件，常见处理流程会从 index.pkl、pocket PDB 和配体 SDF/MOL2 构建缓存。

## data_schema
PocketLigandPairDataset 以 pocket_fn 和 ligand_fn 为索引，输出 ProteinLigandData；PDBBind 路径会额外携带 y 和 kind。

## task_usage
适用于靶点条件分子生成、口袋对接、亲和力相关训练和样例验证。

## integration_paths
优先确认 index.pkl、口袋 PDB 和配体文件是否同目录成套，再决定是否生成 LMDB 缓存。

## preparation_requirements
先检查靶点子目录是否同时有 protein 和 ligand，再验证缓存版本和 split 文件。

## consumption_interfaces
消费端通常需要蛋白原子图、配体原子图、坐标和可选标签。

## operation_limits
不要把数据目录、数据库目录和模型权重目录混为一类；不要假设所有子目录都能直接作为训练样本；如果某个目录只是参考数据库，应先把它定位为外部依赖，再决定是否写入 datapipe。
