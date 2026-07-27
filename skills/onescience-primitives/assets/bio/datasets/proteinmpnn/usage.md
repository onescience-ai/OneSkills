
## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/proteinmpnn/pdb_2021aug02_sample`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/proteinmpnn/pdb_2021aug02_sample`。目录下有 README、list.csv、test_clusters.txt、valid_clusters.txt、pdb/、l3/；单个链文件为 PDBID_CHAINID.pt，配套元数据为 PDBID.pt。

## data_schema
PDBID_CHAINID.pt 包含 seq、xyz、mask、bfac、occ；PDBID.pt 包含 method、date、resolution、chains、tm、asmb_ids、asmb_details、asmb_method 和 assembly 变换。

## task_usage
适用于 ProteinMPNN 序列设计、链级条件生成、结构约束采样和 cluster split 训练/验证。

## integration_paths
先按 list.csv 或 cluster 文件定位链，再按 PDBID 读取单链或 assembly 元信息；训练时应保持 cluster 分割，不要跨 cluster 随机切分。

## preparation_requirements
先检查链级 pt 是否齐全，再确认验证/测试 cluster 与训练 cluster 不重叠。

## consumption_interfaces
消费端通常需要 seq、xyz、mask、chain ID、resolution 和 cluster 信息，以构建 batch 训练样本。

## operation_limits
不要把数据目录、数据库目录和模型权重目录混为一类；不要假设所有子目录都能直接作为训练样本；如果某个目录只是参考数据库，应先把它定位为外部依赖，再决定是否写入 datapipe。
