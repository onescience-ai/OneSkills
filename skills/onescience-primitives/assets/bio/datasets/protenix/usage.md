
## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/protenix`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/protenix`。关键文件包括 seq_to_pdb_index.json、components.v20240608.cif、mmcif_msa、mmcif_bioassembly、posebusters_* 与 recentPDB_* 索引。

## data_schema
seq_to_pdb_index.json 提供序列到结构检索索引；mmcif/mmcif_msa/mmcif_bioassembly 目录保存结构与比对文件；indices 目录保存采样或过滤后的列表。

## task_usage
适用于蛋白结构预测、复合物建模、结构检索、MSA 组织和 Protenix 风格推理输入准备。

## integration_paths
优先先读索引再定位结构文件，再按链级或复合物级组织样本；若下游需要单链/多链输入，应从 bioassembly 和 mmCIF 路径中区分。

## preparation_requirements
先确认序列映射、样本命名规则和 bioassembly 版本；若使用 MSA 或模板，需检查每个样本是否同时有 mmcif 与对应比对文件。

## consumption_interfaces
典型消费协议是结构文件路径、链映射、MSA 字段和样本 ID，供结构推理或打分模型使用。

## operation_limits
不要把数据目录、数据库目录和模型权重目录混为一类；不要假设所有子目录都能直接作为训练样本；如果某个目录只是参考数据库，应先把它定位为外部依赖，再决定是否写入 datapipe。
