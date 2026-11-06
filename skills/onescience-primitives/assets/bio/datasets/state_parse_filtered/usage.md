## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/State_dataset/State-Parse-Filtered`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/State_dataset/State-Parse-Filtered`。



已绑定的资源入口：

- `State_dataset/State-Parse-Filtered/parse_concat_full.h5ad`
- `State_dataset/State-Parse-Filtered/celltype.toml`
- `State_dataset/State-Parse-Filtered/donor.toml`
- `State_dataset/State-Parse-Filtered/split_1_zeroshot.toml`

## data_schema

X 为 CSR cells × genes。已核实 obs 含 `donor,cytokine,treatment,cell_type,donor_ct,cell_type_clean,donor_ct_clean`；var 没有额外注释列，基因身份须读 var 索引；obsm 含 `X_hvg,X_state`。TOML 有 `[datasets]`、`[training]`、`[zeroshot]`、`[fewshot]`，fewshot 以 `parse.<group>` 索引并列出 val/test 扰动。

## task_usage

先选择 HVG 或 State 表示及细胞类型/供体泛化协议，再匹配 cytokine/treatment 和控制细胞，建立条件到响应的任务。

## integration_paths

TOML 解析与路径重定位 → clean 分组和扰动集合映射 → 稀疏表达/所选 obsm → State 数据 adapter。

## preparation_requirements

检查 TOML 中每个组和 val/test 扰动是否真实存在，核对 clean 值与原始列的映射；检查供体/条件重叠和所选表示维度，记录 control 定义。

## consumption_interfaces

细胞表达或指定的 X_hvg/X_state、供体/细胞类型、cytokine/treatment、控制标记和明确的 split；保留原始细胞索引。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

obsm 的 X_hvg/X_state 是派生表示，不能与 X 的基因轴互换。不得将 TOML 中的组名未经映射直接匹配 obs。保留 CC-NC-4.0-License.txt 和 README 的使用限制；元信息 visibility=public 不改变数据条款。
