## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/Carbon/finetune/malinois-mpra-regression`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/finetune/malinois-mpra-regression`。



已绑定的资源入口：

- `Carbon/finetune/malinois-mpra-regression/data`

## data_schema

标识与来源：`id,split,chromosome,data_project,oligo,variant_class`；序列：`sequence,sequence_length,reverse_complement,forward_rc_concat`；活性：`K562_log2FC,HepG2_log2FC,SKNSH_log2FC`；标准误：三个 `*_lfcSE`；训练标准化目标：三个 `*_log2FC_train_zscore`；筛选：`all_se_le_1,any_log2fc_gt_0_5`。目标为三维连续回归。

## task_usage

用于单序列或显式正反链拼接的三目标回归；按选定目标空间及 all_se_le_1 策略报告各细胞类型指标。

## integration_paths

保留 chromosome split → 选择 sequence 或 forward_rc_concat → 三目标回归 adapter；训练 z-score 与目标顺序随模型一起记录。

## preparation_requirements

检查 split 字段与文件和染色体一致，验证三目标/SE 有限值、布尔筛选及长度；核对 z-score 统计来源与包装/tokenizer 兼容性。

## consumption_interfaces

指定序列输入、顺序固定的三维 targets、标准误/筛选标记、chromosome、id 和 split；模型训练不将目标相关筛选标记偷渡为输入特征。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

SE 过滤改变评测分母，必须显式报告。forward_rc_concat 已包含正反两段 <dna> 包装，不能再次无意追加反向互补。不要执行来源 create_dataset.py 中的上传操作。
