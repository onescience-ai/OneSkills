## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/Geneformer`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/Geneformer`。



已绑定的资源入口：

- `Geneformer/Genecorpus-30M/genecorpus_30M_2048.dataset`
- `Geneformer/Genecorpus-104M/genecorpus_104M_4096.dataset`
- `Geneformer/Genecorpus-30M/example_input_files`
- `Geneformer/Genecorpus-30M/token_dictionary.pkl`

## data_schema

| 版本 | 已核实 Arrow 字段 | 语义 |
| --- | --- | --- |
| 30M / 2048 | `input_ids: list<int64>`、`length: int64` | 每个细胞的基因排序 token 与长度 |
| 104M / 4096 | `input_ids: list<int32>` | 每个细胞的排序 token；本地没有独立 `length` 字段 |

不是表达计数矩阵，也不是 DNA 碱基 token。30M README 的 `lengths` 与本地实际字段 `length` 不同，读取以 Arrow/schema 为准。104M 长度可从列表计算，不应假定每条恰好 4096。

## task_usage

用于 Geneformer 类基因排序语言模型的语料读取与适配；下游监督微调另行绑定 example_input_files 中的任务标签，不能将无注释语料冒充已标注细胞分类集。

## integration_paths

版本选择 → 词表与模型配置对齐 → Arrow 数据读取 → 任务所需的 mask/padding/collator；基因 ID 应按相应词表的 Ensembl 映射解释。

## preparation_requirements

核对 state.json 分片清单、Arrow 类型、token 范围及列表长度；确认词表映射方向和特殊 ID，验证 padding 与有效长度一致。下游示例需独立检查样本 ID 与标签连接。

## consumption_interfaces

主输入为 `input_ids`，30M 可提供 `length`，104M 可派生长度；任务 collator 负责 mask 与训练目标。示例 gene/cell 标签不属于所有主语料样本。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

30M 与 104M 的词表、特殊 token 和模型长度预算不同，不能拼接后直接共用 ID。30M README 描述 pad/mask，104M 描述 cls/eos/pad/mask；104M 所需 token_dictionary_104M.pkl 未在该本地根目录确认，接入前从匹配版本补齐。不要反向恢复或宣称提供原始表达计数。
