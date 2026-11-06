## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/Carbon/eval/traitgym`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/traitgym`。



已绑定的资源入口：

- `Carbon/eval/traitgym/mendelian_traits_vep.parquet`
- `Carbon/eval/traitgym/complex_traits_vep.parquet`
- `Carbon/eval/smoke/traitgym_mendelian.parquet`

## data_schema

`chrom:string,pos:int64,ref:string,alt:string,label:int64,class:string,consequence:string,tss_dist:int64,match_group:string,ref_seq:string,var_seq:string,score`。complex 的 score 为 double，Mendelian 的 score 为 null。README 定义 pos 是 1-based hg38，ref_seq/var_seq 为 8192 bp、变异位于 0-based 索引 4096 的窗口。

## task_usage

用于非编码变异零样本/冻结模型 VEP；来源 README 描述 delta=LL(var_seq)-LL(ref_seq)，可选正反链平均，报告 AUROC/AUPRC 和染色体加权 AUPRC。

## integration_paths

选择 trait 配置 → 验证窗口与组 → 固定似然打分方向和正反链策略 → 按 match_group/染色体汇总；模型分数单独保存。

## preparation_requirements

确认坐标、SNV、窗口中心、label 值、组大小及去重；记录序列 tokenizer、打分范围、分数方向和是否 reverse-complement averaging。

## consumption_interfaces

ref_seq/var_seq 成对输入，附 chrom/pos/ref/alt、label 和 match_group；score 为来源 PIP 元数据而非待比较模型输出。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

完整性检查须确认 ref/alt 与窗口中心、长度和参考一致。不要把 score/PIP 当作输入特征泄漏标签。跨染色体指标汇总与匹配分组均须遵循选定协议。
