
## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/GenScore`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/GenScore`。训练/推理数据主路径为 `genscore_data/`。genscore_data 下包含训练、测试与推理样本目录，test_data 保存 smoke test 权重或小样本，trained_models 保存模型权重。

## data_schema
训练侧样本通常是 protein_graph、ligand_graph、label；推理侧会从 pocket 和 ligand 文件实时构图。

## task_usage
适用于结合亲和力预测、虚筛排序和口袋-配体图打分。

## integration_paths
训练时先区分 PDBbind 与 CASF 评测集，再按需要加载图缓存或在线构图；推理时应优先使用 pocket 生成路径。

## preparation_requirements
先确认图缓存版本和标签来源，再核对测试集是否与训练集分离。

## consumption_interfaces
消费端通常读取蛋白图、配体图和标量标签或排序分值。

## operation_limits
不要把数据目录、数据库目录和模型权重目录混为一类；不要假设所有子目录都能直接作为训练样本；如果某个目录只是参考数据库，应先把它定位为外部依赖，再决定是否写入 datapipe。
