## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/Carbon/eval/brca2`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/brca2`。



已绑定的资源入口：

- `Carbon/eval/brca2/brca2_vep.parquet`
- `Carbon/eval/brca2/brca2_cache/chr13_hg19.fa`
- `Carbon/eval/brca2/brca2_cache/huang2025_brca2.xlsx`
- `Carbon/eval/smoke/brca2_vep.parquet`

## data_schema

`chrom:int64,pos:int64,ref:string,alt:string,score:double,class:string,ref_seq:string,var_seq:string`。第一条窗口各 8192 bp；score 是来源功能测量/处理结果，class 为功能类别，不是模型输出。坐标协议与 score→class 阈值须从配套来源进一步核实。

## task_usage

用于 BRCA2 序列对 VEP，与来源功能分数或已验证的 class 映射比较；固定似然差方向与序列窗口打分范围。

## integration_paths

配对窗口校验 → 模型 ref/alt 打分 → 经核实的功能 class/score 评测；参考/XLSX 仅作为来源回查。

## preparation_requirements

检查 chrom/pos/ref/alt、窗口长度/差异位置、重复位点与 score/class 值域；需要二分类时先补齐来源阈值和方向。

## consumption_interfaces

ref_seq/var_seq、变异身份、来源 score/class 和模型独立预测；保留参考版本和窗口策略。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

重建窗口时先核实坐标与 hg19 参考缓存，不可与 TraitGym hg38 窗口混用。实验功能与临床致病性不同；阈值来源不清时只报告原始分数/类别。
