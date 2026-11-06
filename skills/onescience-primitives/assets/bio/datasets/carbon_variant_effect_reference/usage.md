## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/Carbon/eval/variant-effect-prediction`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/variant-effect-prediction`。



已绑定的资源入口：

- `Carbon/eval/variant-effect-prediction/hg38.parquet`
- `Carbon/eval/variant-effect-prediction/ClinVar_VEP_results.parquet`

## data_schema

hg38.parquet 只有 **`ID,Sequence`**（大小写不可改），为 string 参考序列记录。ClinVar_VEP_results 为 `chrom,pos,ref,alt,label,type,refseq_id` 及 CADD/phyloP/phastCons/GPN-MSA/NT/HyenaDNA/Evo2/GENERator 等预计算分数，没有 ref_seq/var_seq 窗口。二者是不同样本单位。

## task_usage

参考资源用于经核实坐标的窗口重建；结果表用于历史 VEP score 复核和比较。两者分开加载，再以明确的变异坐标与参考映射连接。

## integration_paths

参考 ID/版本核查 → 位点坐标/ref 校验 → 独立窗口生成 adapter；预计算模型结果保持只读并单独比较。

## preparation_requirements

检查参考 ID 与染色体映射、Sequence 大小写/模糊碱基、坐标范围和 label 定义；对比不同 ClinVar 版本时按 variant key 显式求交并报告分母。

## consumption_interfaces

参考消费接口为 ID→Sequence/窗口查询；结果消费接口为 variant key、label 与指定模型 score，不提供已生成 ref/alt 序列。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

Sequence 为可能很长的字符串，流式/选择性读取，不一次复制整个参考到内存。基因组 ID、pos 坐标、assembly、ref 匹配未确认前不能据此为任意 ClinVar 表生成窗口。
