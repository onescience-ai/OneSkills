## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/State_dataset/SE-167M-Human-smoke`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/State_dataset/SE-167M-Human-smoke`。



已绑定的资源入口：

- `State_dataset/SE-167M-Human-smoke/19k_human_filtered_scbasecount`
- `State_dataset/SE-167M-Human-smoke/all_embeddings_Preprint-SE-167M-Human.pt`

## data_schema

四个 H5AD 的 X 为 CSR，var 含 `gene_symbols,feature_types` 和 QC 列；obs 含 `SRX_accession,gene_count,umi_count` 及计数 QC。未见 cell_type 监督标签列，未见额外 layers。PT 为配套基因 embedding 资源，其对象布局、向量维度和基因键顺序本轮未反序列化确认。

## task_usage

用于 smoke 数据加载、基因 embedding 对齐及 SE 模型输入检查；无现成监督标签时采用明确的自监督目标。

## integration_paths

H5AD 基因轴检查 → PT 布局与基因键确认 → 显式 ID join → SE 表示 adapter。

## preparation_requirements

检查 SRX 来源、X 稀疏结构、var 唯一性、PT 键与向量维度、缺失基因处理及输出顺序；分批读取矩阵。

## consumption_interfaces

表达向量、基因索引/符号、accession，及经过验证的对应基因 embedding；不自动提供 cell_type 或 perturbation 标签。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

四文件基因维度相同仍需核对索引顺序。不能将基因 embedding 当作细胞 embedding，也不能从 PT 文件名推断 token 字典。
