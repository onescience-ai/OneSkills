
## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/alphafold2.3.0`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/alphafold2.3.0`。顶层包含 params、bfd、mgnify、pdb70、pdb_mmcif、pdb_seqres、small_bfd、uniprot、uniref30、uniref90。

## data_schema
输入通常是蛋白序列，输出依赖参数文件、序列数据库和模板数据库。

## task_usage
适用于 AlphaFold 2 推理、数据库复现和同源搜索准备。

## integration_paths
优先作为数据库和参数目录挂载，训练或推理脚本应通过外部配置指定具体数据库路径。

## preparation_requirements
先确认 params 与公共数据库版本是否配套，再检查索引和压缩包是否完整。

## consumption_interfaces
消费端通常是 AlphaFold 搜索和推理流水线。

## operation_limits
不要把数据目录、数据库目录和模型权重目录混为一类；不要假设所有子目录都能直接作为训练样本；如果某个目录只是参考数据库，应先把它定位为外部依赖，再决定是否写入 datapipe。
