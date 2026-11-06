## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/Carbon/eval/genomic-niah`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/genomic-niah`。



已绑定的资源入口：

- `Carbon/eval/genomic-niah/data`

## data_schema

共有 `uid,haystack_mode,source,context_length_tokens,context_length_bp,depth,condition,num_distractors,key_len_bp,value_len_bp,key,value,negative_value,prompt,positive_sequence,negative_sequence`。plain 另有 `target_insert_start_bp,target_insert_end_bp`；near-duplicate 另有 `task,mutation_distance,distractor_keys,distractor_values`，没有 plain 的两个插入位置列。样本单位是一项检索问题，而非带类别标签的基因。

## task_usage

按本地 README 的 gen_exact_match（限制 DNA token 的 greedy 生成）和 ll_correct（正续写似然高于负续写）分别评估，按难度、长度、深度和 kingdom 报告。

## integration_paths

选择配置 → tokenizer 实际长度检查 → 完整 prompt 生成或正负续写打分 → 按配置/深度聚合。

## preparation_requirements

核对 prompt/positive/negative 的关系、uid、目标长度、context 与模型容量；确认 DNA token 约束和续写区间打分，不用完整序列长度差异制造偏好。

## consumption_interfaces

生成消费 prompt 并回查 value；似然评测消费 positive_sequence/negative_sequence，保留 uid、config、source、depth 和长度。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

截断 prompt 会改变检索任务及 needle 位置，不能静默裁剪后继续沿用同一上下文结果。DNA 生成 exact match 与 ll_correct 是不同指标，不能互相代替。
