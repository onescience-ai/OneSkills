## content_principle

GUE 基因组分类基准数据集合的数据原语，覆盖本地 `DNABERT-2_dataset` 中的监督分类 CSV。数据根目录为 `/public/share/sugonhpcapp01/onestore/onedatasets/DNABERT-2_dataset`，包含 `GUE`、`GUE_v2/GUE` 两个完整目录分支和 `sample_data` 示例分支。

蒸馏依据为 2026-11-05 对上述目录的只读核查：完整枚举 CSV 路径、读取全部 219 个 CSV 的表头，并对指定文件抽查记录。目录与字段是本地实测事实；上游发布版本、许可证、完整类别释义和官方评测口径尚未核实。原语版本 `1.0.0` 表示卡片版本，不表示数据集上游版本。

## data_schema

一行是一条带标签的分类样本，存在两种原始列结构；列名区分大小写。

| 适用目录 | CSV 列名及顺序 | 样本单位 |
| --- | --- | --- |
| `EMP`、`fungi`、`mouse`、`prom`、`splice`、`tf`、`virus`；以及 `sample_data` | `sequence,label` | 一条 DNA 序列及其任务内分类标签 |
| `EPI/<cell_line>` | `enhancer,promoter,label` | 一对增强子、启动子 DNA 序列及其任务内分类标签 |

序列按字符串读取，标签先保留原始值，再依据当前任务的标签映射转为分类 ID。原始 CSV 没有统一的 `task`、`split`、`branch` 或样本 ID 列；这些信息由读取端根据路径补充。EPI 的两个序列字段必须保持配对关系。

## directory_layout

```text
DNABERT-2_dataset/
├── GUE/
│   ├── EMP/<mark>/{train,dev,test}.csv
│   ├── EPI/<cell_line>/{train,dev,test}.csv
│   ├── fungi/species_20/{train,dev,test}.csv
│   ├── mouse/<0..4>/{train,dev,test}.csv
│   ├── prom/<prom_task>/{train,dev,test}.csv
│   ├── splice/reconstructed/{train,dev,test}.csv
│   ├── tf/<0..4>/{train,dev,test}.csv
│   └── virus/{covid,species_40}/{train,dev,test}.csv
├── GUE_v2/
│   └── GUE/                         # 与上方具有相同任务目录结构
├── sample_data/{train,dev,test}.csv
├── .GUE_v2.zip.efileUploading         # 上传状态文件，不作为数据输入
└── GUE_v2.zip.efilePart               # 上传分片，不作为完整压缩包读取
```

花括号及 `<...>` 表示路径模式，不是实际目录名。两个完整分支目录结构相同，不代表文件内容或数据版本相同。

## storage_format

已核查的样本文件为带表头的逗号分隔 CSV，可用标准 CSV 解析器读取；无需先解压上传分片。序列长度以碱基字符数计，不等于模型 tokenizer 产生的 token 数。缓存或转换产物应写入独立输出目录，并记录来源分支、任务、split 和预处理配置。

## scale_spec

`GUE` 与 `GUE_v2/GUE` 各有 8 个一级任务组、36 个任务目录和 108 个 CSV，每个任务目录均有 `train.csv`、`dev.csv`、`test.csv`。每个完整分支有 90 个单序列 CSV 和 18 个 EPI 序列对 CSV。这里的 36 是本地目录数量，不等同于上游定义的独立科学任务数量。

`sample_data` 另有 3 个 CSV，完整读取所得记录数为 train 4、dev 2、test 2；仅适合接口检查。

下表为 `GUE` 指定训练文件前 64 条记录的长度观察值，不是全量长度约束；完整基准样本总数未统计。

| 相对任务目录 | 抽查序列长度（碱基） |
| --- | --- |
| `prom/prom_300_all` | 300 |
| `splice/reconstructed` | 400 |
| `EMP/H3` | 500 |
| `tf/0`、`mouse/0` | 101 |
| `virus/covid` | 999 |
| `fungi/species_20` | 10000 |
| `EPI/GM12878` | enhancer 3000；promoter 2000 |

`GUE_v2/GUE/EPI/GM12878/train.csv` 前 64 条也观察到 enhancer 3000、promoter 2000；其他 v2 文件的长度分布未逐一核查。

## coverage_spec

以下目录清单在两个完整分支中均已核实。用途用于任务路由，精确标签语义仍需对应任务说明支持。

| 任务组 | 已有任务子目录 | 用途与边界 |
| --- | --- | --- |
| `EMP` | `H3`、`H3K14ac`、`H3K36me3`、`H3K4me1`、`H3K4me2`、`H3K4me3`、`H3K79me3`、`H3K9ac`、`H4`、`H4ac` | 组蛋白相关表观遗传分类 |
| `EPI` | `GM12878`、`HUVEC`、`HeLa-S3`、`IMR90`、`K562`、`NHEK` | 按细胞系组织的增强子—启动子互作分类，采用序列对输入 |
| `fungi` | `species_20` | 真菌物种相关分类，类别映射需补齐 |
| `mouse` | `0`、`1`、`2`、`3`、`4` | 小鼠相关序列分类；编号含义未核实 |
| `prom` | `prom_300_all`、`prom_300_notata`、`prom_300_tata`、`prom_core_all`、`prom_core_notata`、`prom_core_tata` | 启动子相关分类，保留各子任务边界 |
| `splice` | `reconstructed` | 剪接相关分类，精确类别含义需补齐 |
| `tf` | `0`、`1`、`2`、`3`、`4` | 转录因子相关序列分类；编号对应对象未核实 |
| `virus` | `covid`、`species_40` | 病毒相关分类，类别含义以任务说明为准 |

## label_spec

抽查记录的 `label` 为整数字符串：`EMP/H3`、`EPI/GM12878`、`prom/prom_300_all`、`tf/0`、`mouse/0` 观察到 `0,1`；`splice/reconstructed` 观察到 `0,1,2`；`virus/covid` 观察到 `0` 至 `8`；`fungi/species_20` 观察到 `0` 至 `19`。这些是指定文件前 64 条的观察值，不构成全量类别数证明。

不同任务的同值标签不共享生物学语义，不能统一假定 `0=阴性`、`1=阳性`。正式训练前应统计当前任务各 split 的完整标签值域，取得类别释义，并固定标签映射；类别映射和类别数不得从 test 集动态拟合。标签释义缺失时保留原始 ID，并报告语义限制。

## split_strategy

沿用每个任务已有的 `train.csv`、`dev.csv`、`test.csv`：train 用于拟合，dev 用于选择模型和参数，test 用于最终评测。禁止合并后重新随机划分并仍宣称使用原始 GUE 划分。需要从当前数据学习的变换只在 train 上拟合，包括新训练的 tokenizer；使用预训练 tokenizer 时固定其版本与配置。

一次接入必须显式选择 `GUE` 或 `GUE_v2/GUE`，所有 split 来自同一分支、同一任务。`tf/0..4` 和 `mouse/0..4` 的编号不能未经说明就解释成可合并折。`sample_data` 单独标记为示例，不与完整基准混合计算指标。

## constraints

- `virus/covid/train.csv` 的前 64 条中已观察到 IUPAC 模糊碱基 `R`；输入校验不能无条件限定为 A/C/G/T。应明确 tokenizer 对模糊碱基、大小写和未知字符的处理方式，保留转换记录。
- 读取完整文件后再确认长度分布与标签值域；长序列截断、分块及 EPI 配对编码必须显式配置，不能静默丢弃 promoter 或 enhancer。
- 不凭目录名认定两个分支相同、编号代表交叉验证折、或类别 ID 对应某个物种/功能。需要比较分支时另行核验文件内容及来源。
- 本卡未验证上游许可证、官方版本对应关系、官方指标和全量跨 split 重复情况；正式发布或复现实验前补齐相应证据。
