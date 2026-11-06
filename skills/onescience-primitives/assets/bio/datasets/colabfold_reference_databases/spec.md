## content_principle

ColabFold environmental/UniRef30 本地归档包。OpenDDE 本地 ColabFold 参考数据库归档原语，登记 environmental 202108 与 UniRef30 2103 版本、首个 tar 成员及重复下载候选，标明小归档截断和 MMseqs 搜索索引尚未验证。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/OpenDDE/colabfold_db`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。核对三文件大小和各自第一个 tar 成员，对 89,776 B 小归档读取得到 EOFError；未遍历大归档或运行搜索。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

资源单位为版本化 gzip/tar 归档。envdb 首个 tar 成员为 `colabfold_envdb_202108_h.tsv`；两个 UniRef30 候选首成员均为 `uniref30_2103.tsv`。当前不是已核实的可搜索 MMseqs 数据库前缀，首个成员可读也不代表整个归档完整。

## directory_layout

```text
OpenDDE/colabfold_db/
├── colabfold_envdb_202108.tar.gz
├── uniref30_2103.tar.gz                 # 89,776 B，gzip 读取报 EOFError
├── uniref30_2103.tar.gz.1               # 大型候选，不是第二个分片
└── {i.sh,ins.sh,i.log,log}               # 来源操作记录，不作为数据执行
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

gzip 压缩 tar。恢复/转换需要独立磁盘空间与匹配的 MMseqs/ColabFold 建库协议；本卡仅登记资源与检查步骤，不执行解压或索引构建。

## scale_spec

本地文件大小：envdb 117,965,643,010 B；小 UniRef30 89,776 B；.1 候选 75,336,202,245 B。小文件读取已报 compressed file ended before end-of-stream；大文件只做 tar 首头检查，未完成全流完整性验证。

## coverage_spec

ColabFold environmental 202108 和 UniRef30 2103 归档来源，用于后续蛋白同源搜索数据库准备。不能与 RoseTTAFold 的 HH-suite UniRef30 文件格式混用。

## label_spec

归档不提供监督标签或 train/test。条目及 TSV 的完整字段和索引布局待恢复后核实，不能仅据 archive 名称编写已存在的 MMseqs 参数/索引路径。

## split_strategy

这是参考数据库资源，不是训练样本集。归档版本和候选文件必须单独固定，.tar.gz 与 .tar.gz.1 不视为多分片，不拼接恢复。

## constraints

小 UniRef30 文件明确不可作为完整输入；.1 仅为候选，需来源 checksum/全流校验。未发现并核实可直接搜索的索引，不宣称本地可运行 MSA 搜索。不能自动执行来源 shell 脚本。
