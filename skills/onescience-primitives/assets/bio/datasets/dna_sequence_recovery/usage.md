## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/Carbon/eval/sequence-recovery`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/sequence-recovery`。



已绑定的资源入口：

- `Carbon/eval/sequence-recovery/bacteria/test.parquet`
- `Carbon/eval/sequence-recovery/eukaryote/test.parquet`
- `Carbon/eval/sequence-recovery/others/test.parquet`
- `Carbon/eval/sequence-recovery/eukaryote/test_new.parquet`

## data_schema

三个标准 test 均有 `sequence:string,label:string`；bacteria 另有 record_id、taxonomy(list)、length、domain/phylum/class/type，others 有 record_id、taxonomy(list)、length、species_type，eukaryote 标准版仅再有 type。**test_new** 则为 `record_id,taxonomy:string,gene_type,species_type,strand,sequence,start,end,gene_sequence`，没有 label，taxonomy 类型也不同。

## task_usage

标准任务输入 sequence，生成后续 128 bp 并按明确协议比较 label；不同物种配置和长度单独报告。test_new 先做 schema/任务定义核对。

## integration_paths

标准 test → tokenizer 和左截断策略 → DNA 续写 adapter；test_new 走单独视图核验，任务契约明确后再接入。

## preparation_requirements

核实标准 label 长度、输入字符和来源重复；记录实际 token/bp 长度、解码和 exact-match/碱基级指标。test_new 核对 start/end 的坐标和 gene_sequence 关系。

## consumption_interfaces

标准输入 sequence、字符串 label、来源/物种元信息与实际上下文；test_new 只交接其具名字段和未确认的目标定义。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

缩短标准输入时依据 README 采用 left truncation，保留靠近续写点的末端，并报告实际上下文长度。不能把 label 拼进模型输入，或把 gene_sequence 无依据截成 128 bp 目标。
