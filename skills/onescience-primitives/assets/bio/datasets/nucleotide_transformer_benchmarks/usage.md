## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/Carbon/finetune/nucleotide_transformer_downstream_tasks`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/finetune/nucleotide_transformer_downstream_tasks`。



另有 smoke 路径 `${ONESCIENCE_DATASETS_DIR}/Carbon/finetune/smoke/gue_promoter`，默认根目录与上述数据根采用同一 onedatasets 挂载。

已绑定的资源入口：

- `Carbon/finetune/nucleotide_transformer_downstream_tasks`
- `Carbon/finetune/smoke/gue_promoter`

## data_schema

所有已核查 Parquet 均为 `sequence:string,name:string,label:int32,task:string`，一行是一条序列及任务内类别。配套 `.fna` 是文本序列视图，不能假设单独读取 FNA 就具备与 Parquet 相同的 label/task 列。

另登记 `Carbon/finetune/smoke/gue_promoter/{train,test}.jsonl`：实际字段为 `sequence,name,label,task`，两文件 task 均为 `promoter_all`。该入口虽命名 gue_promoter，具体上游来源未核实，作为独立 smoke 样例接入，不据名称认定它与 GUE 或 NT 正式快照等价。

## task_usage

用于 NT/其他 DNA 模型下游分类；以具备标签的 Parquet 为监督入口，FNA 用于独立序列解析或经 ID 校验的适配。

## integration_paths

任务选择 → Parquet 标签/ID 解析 → tokenizer 与分类头 → 保留 train/test 的任务级评测；跨资源复用先比对样本身份。

## preparation_requirements

核对 task 字段与目录一致、name/sequence 重复、标签值域和长度；比较 FNA/Parquet 时验证顺序与 ID；固定派生 validation 和 tokenizer。

## consumption_interfaces

sequence、任务内 label、name、task 与原始 split；所有批次必须明确当前 task 的类别映射。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

该集合不能因为包含 promoter/组蛋白任务就冒称 GUE 或 BEND。HyenaDNA 中存在 enhancer 等目录命名差异，未经内容比对不能自动认定为同一快照或互换 split。
