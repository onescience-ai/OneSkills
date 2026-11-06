## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/IGGM/dataset`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/IGGM/dataset`。



已绑定的资源入口：

- `IGGM/dataset/SAb-23-H2-Ab`
- `IGGM/dataset/SAb-23-H2-Nano`

## data_schema

prot_ids.txt 为复合物身份列表；native/design FASTA 使用 `>H`（重链）、`>L`（轻链，Nano 样本无该链）、`>A`（抗原）。抽查 native PDB 亦有 H/L/A 或 H/A 链，具体每个复合物仍需验证。design FASTA 的 CDR 区可含 `X` 掩码，不是已生成的完整设计序列。

## task_usage

用于 IGGM 类 CDR 掩码设计、native 恢复和结构条件适配；按 prot_id 和 CDR 设置选择输入与参考。

## integration_paths

prot_ids → native FASTA/PDB 角色核对 → design 掩码与坐标映射 → 抗体设计 adapter；生成结果另存，不覆盖 native。

## preparation_requirements

验证 ID 配对、H/L/A 链角色与长度、native 到 PDB 残基映射、缺失残基和 X 位置；明确 CDR 编号与设计评价协议。

## consumption_interfaces

prot_id、子集、native 链序列/结构、design FASTA、掩码/待设计位置与抗原条件；输出为独立设计，不把掩码输入当预测。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

两子集 PDB 目录名不同，loader 必须显式分派。文件名中的 NA 不代表实际轻链。X 掩码必须保留给设计 adapter，不能删除后改变序列与坐标长度。
