## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/OpenDDE/colabfold_db`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/OpenDDE/colabfold_db`。



已绑定的资源入口：

- `OpenDDE/colabfold_db/colabfold_envdb_202108.tar.gz`
- `OpenDDE/colabfold_db/uniref30_2103.tar.gz`
- `OpenDDE/colabfold_db/uniref30_2103.tar.gz.1`

## data_schema

资源单位为版本化 gzip/tar 归档。envdb 首个 tar 成员为 `colabfold_envdb_202108_h.tsv`；两个 UniRef30 候选首成员均为 `uniref30_2103.tsv`。当前不是已核实的可搜索 MMseqs 数据库前缀，首个成员可读也不代表整个归档完整。

## task_usage

用于数据库资源发现、归档候选选择和恢复规划。先完成完整性检查，再解压到独立目录，并由匹配版本工具验证/建立索引。

## integration_paths

归档候选选择 → 完整性/来源校验 → 独立位置恢复 → 核对 TSV/数据库产物 → MMseqs/ColabFold 建库与最小查询。

## preparation_requirements

记录候选文件大小/哈希与来源、可用空间和输出位置；完整 gzip/tar 校验后核查成员和版本，索引构建参数及工具版本写入派生记录。

## consumption_interfaces

archive_path、release、候选/截断状态与待验证事项；只有完成恢复与索引验证后才交付可搜索前缀，当前不提供虚构的索引路径。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

小 UniRef30 文件明确不可作为完整输入；.1 仅为候选，需来源 checksum/全流校验。未发现并核实可直接搜索的索引，不宣称本地可运行 MSA 搜索。不能自动执行来源 shell 脚本。
