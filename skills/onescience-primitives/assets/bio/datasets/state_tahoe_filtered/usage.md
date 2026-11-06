## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/State_dataset/State-Tahoe-Filtered-smoke`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/State_dataset/State-Tahoe-Filtered-smoke`。



已绑定的资源入口：

- `State_dataset/State-Tahoe-Filtered-smoke/c36.h5ad`
- `State_dataset/State-Tahoe-Filtered-smoke/c39.h5ad`
- `State_dataset/State-Tahoe-Filtered-smoke/c44.h5ad`

## data_schema

三文件 X 均为 CSR；obs 含 `drugname_drugconc,drug,cell_line,plate,gene,gem_group` 及 QC 字段；var 无额外列，读取索引确认基因；obsm 含 `X_hvg,X_state`。`drugname_drugconc` 保留药物、浓度、单位组合的字符串，不是单一药物 ID。

## task_usage

用于药物扰动响应 adapter、条件编码及小范围 State 接入验证。保持药物和剂量组合，选定 HVG 或 State 表示。

## integration_paths

c36/c39/c44 选择 → 基因轴和条件解析 → 显式 holdout → State adapter；不能用 Parse 的 cytokine 列协议替代 Tahoe 药物协议。

## preparation_requirements

核对三个文件基因索引顺序、drugname_drugconc 的解析规则、control 条件和 plate 分布，记录模型表示及归一化来源。

## consumption_interfaces

所选表达/embedding、药物及剂量、细胞系、plate、control 与 split；保留文件分支和原始细胞索引。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

同一药物不同剂量不可静默合并；相同基因维度不证明三文件基因顺序一致。X_hvg/X_state 与 X 采用不同坐标语义，使用前核对。
