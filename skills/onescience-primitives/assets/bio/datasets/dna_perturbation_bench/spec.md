## content_principle

DNA 序列扰动配对偏好基准。Carbon 本地 DNA Perturbation Bench，覆盖人/鼠同义密码子替换、CAG 插入、启动子反向互补及历史 tata/codon 分支，保留原序列与扰动序列配对、坐标和操作元数据。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/perturbation-bench`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。读取 README，核对六分支与三个 smoke 的 Parquet schema/行数。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

每个分支都有 `original_sequence,sequence`，其余字段不统一。syn_human/syn_mouse 含 benchmark_id、参考版本/注释、位点、CDS 与 patch 边界、n_codons_changed、fraction_codons_changed 等；motif_human 含 motif/patch_len_bp；promoter_revcomp 含 TSS/promoter 布局；tata/synonymous_codons 仅有 `chr,start,end,strand,length` 及序列对，没有 benchmark_id。

## directory_layout

```text
Carbon/eval/
├── perturbation-bench/
│   ├── README.md
│   ├── {syn_human,syn_mouse,motif_human,promoter_revcomp}/test-00000-of-00001.parquet
│   └── {tata,synonymous_codons}/data.parquet
└── smoke/perturbation/{syn_human,syn_mouse,motif_human}.parquet
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

Parquet，一行是一对原序列与经过指定操作的序列，不是两条独立样本。按分支 schema 分流，历史分支没有现代分支的全部定位字段。

## scale_spec

footer 核实 syn_human、syn_mouse、motif_human 各 20,000 对；promoter_revcomp 16,451 对；tata 和 synonymous_codons 各 5,000 对；三个 smoke 各 8 对。未证明历史分支与新分支互不重叠，不能据相加行数宣称独立样本规模。

## coverage_spec

README 详细说明 GRCh38/GENCODE v45 人类和 GRCm39/GENCODE vM34 小鼠的同义替换，以及 CAG repeat insertion。promoter_revcomp 和历史分支按各自字段与后续任务说明解释，不能统一视为同一类功能实验。

## label_spec

README 对 syn_human/syn_mouse/motif_human 将 original_sequence 定义为真实正序列、sequence 为结构改变的负序列，供配对偏好评测。它们不是临床 pathogenic/benign 标签，也不能将同义替换一概解释为致病。其他分支的正负与操作定义需单独确认。

## split_strategy

现代分支作为 test 入口；data.parquet 历史分支没有显式 split 列。每对始终同组，同位点/转录本关联样本不能随意跨训练和测试；smoke 与完整集分开。

## constraints

保留原/扰动方向、链方向、参考组装和 CDS/patch 的坐标约定。不能把六分支 schema 强行补成一套已存在的字段，也不能仅按列名判断所有分支功能含义相同。
