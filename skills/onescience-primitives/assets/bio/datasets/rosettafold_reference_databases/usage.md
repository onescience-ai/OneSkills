## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/RoseTTAFold`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/RoseTTAFold`。



已绑定的资源入口：

- `RoseTTAFold/bfd`
- `RoseTTAFold/pdb100_2021Mar03`
- `RoseTTAFold/UniRef30_2020_06`
- `RoseTTAFold/uniref30`

## data_schema

HH-suite 参考库以 prefix + `_a3m/_hhm/_cs219` 的 `.ffdata/.ffindex` 成对组织，PDB100 另有 `_pdb.ffdata/.ffindex`。ffindex 定位条目 ID、偏移与长度，ffdata 为载荷；不是按行样本/label 表。

| 目录/入口 | 实际版本与前缀 |
| --- | --- |
| bfd | `bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt`，亦有 `bfd_*` 链接别名 |
| pdb100_2021Mar03 | `pdb100_2021Mar03` |
| UniRef30_2020_06 | `UniRef30_2020_06`，独立旧版文件 |
| uniref30/uniref30_* | 软链接到 `alphafold2.3.0/uniref30/UniRef30_2021_03_*` |

## task_usage

为 HH-suite/相关同源搜索提供明确版本的库前缀及只读挂载，选择 BFD、UniRef30 或 PDB100 模板库；不能直接作为模型训练 batch。

## integration_paths

确定搜索器与 release → 前缀/软链接/文件对核查 → 独立工作目录中的小样本检索验证 → MSA/模板 adapter。

## preparation_requirements

确认所需 a3m/hhm/cs219/pdb 文件对、链接可读、索引条目边界与载荷容量；正式使用可按来源 checksum 和搜索器最小查询做额外校验。

## consumption_interfaces

数据库角色、release、解析后的前缀、相关文件对、只读路径和可用性状态；消费方为搜索/模板工具而非序列分类 loader。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

检查软链接解析后的真实路径、成对文件、文件非空和搜索器版本兼容。归档/安装脚本、BLAST 程序和模型权重与参考库分开登记；存在 md5sums 不代表已执行校验。
