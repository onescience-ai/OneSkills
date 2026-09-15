# AI-Ready 输出目录通用契约

本文档定义**跨 domain 通用**的 AI-Ready 数据集输出结构。所有 Tier1 adapter 与 Tier2 合成 converter 必须遵守此契约。domain 特有细节以 primitives 的 `spec.md` 为准，与本契约冲突时以 `spec.md` 优先。

## 目录结构

```text
<target_dir>/
├── data/                   # 必需：主数据文件
├── static/                 # 可选：静态场/参考序列/结构模板/参考数据库
├── stats/                  # 可选：全局或逐变量统计量
├── splits/                 # 可选：train/val/test 索引
├── _converter/             # 仅 Tier2：保留 LLM 合成脚本审计痕迹
│   ├── convert_<dataset>.py
│   ├── prompt_snapshot.md
│   └── raw_probe_report.json
├── dataset_card.json       # 必需：数据集元信息
└── README.md               # 必需：人类可读说明
```

**必需项**：`data/`、`dataset_card.json`、`README.md`。缺失任一即视为 `validation.format_valid=false`。

**可选项**：`static/`、`stats/`、`splits/` 按 primitives `spec.md` 决定是否创建；未创建时不必留空目录。

## data/ 目录组织

按 domain 惯例：

| domain | 推荐格式 | 组织方式 |
|---|---|---|
| climate | HDF5 (`.h5`) 或 NetCDF (`.nc`) 或 Zarr | 按年/月/变量分文件（对齐 ERA5 `data/YYYY.h5`） |
| cfd | pickle / HDF5 / npz | 按 case 或按 `dataX.pkl` + `dataY.pkl` 配对（对齐 DeepCFD） |
| bio | LMDB / h5ad / PDB+索引 / npz | 按样本 ID 或按 split 分文件（对齐 targetdiff LMDB 缓存） |
| matchem | ASE LMDB (`.aselmdb`) / extxyz / DeepMD `set.000/*.npy` | 按 split 分片（对齐 OC20 `data.000N.aselmdb`） |

`data/` 内部允许嵌套子目录，但必须在 `dataset_card.json.data_layout` 中显式描述。

## dataset_card.json schema

```json
{
  "schema_version": "1.0",
  "name": "<dataset_name>",
  "domain": "<cfd|bio|climate|matchem>",
  "version": "<语义化版本或原始数据版本>",
  "handler": "<adapter:climate/era5 | llm_synth:v1 | ...>",
  "source": {
    "dir": "<raw 数据绝对路径>",
    "resolution_method": "explicit | local_probe | modelscope_download",
    "modelscope_repo_id": "<可选>",
    "checksum": "<可选，raw 目录聚合 sha256>"
  },
  "target": {
    "dir": "<AI-Ready 绝对路径>",
    "created_at": "<ISO8601 UTC>",
    "checksum": "<AI-Ready 目录聚合 sha256>"
  },
  "target_schema": {
    "spec_source": "onescience-primitives:<domain>/datasets/<name>/spec.md",
    "data_layout": {
      "data/": "<格式与组织说明>",
      "static/": "<可选>",
      "stats/": "<可选>",
      "splits/": "<可选>"
    },
    "primary_format": "<hdf5|netcdf|lmdb|aselmdb|pickle|npz|h5ad|pdb|...>",
    "tensor_shape": "<可选，如 [T, C, H, W]>",
    "dtype": "<可选，如 float32>",
    "dimensions": {
      "<dim_name>": "<含义>"
    }
  },
  "statistics": {
    "num_samples": "<int 或按 split 的 dict>",
    "total_bytes": "<int>",
    "files_count": "<int>"
  },
  "splits": {
    "strategy": "<按年因果划分|随机划分|按 split 目录|...>",
    "train": "<样本数或索引文件路径>",
    "val": "<可选>",
    "test": "<可选>"
  },
  "provenance": {
    "converter_script": "<_converter/convert_<dataset>.py 或 adapter 路径>",
    "converter_tier": 1,
    "llm_model": "<Tier2 时使用的模型标识，可选>",
    "execution_runtime": "subprocess | onescience-runtime",
    "duration_seconds": "<float>"
  },
  "quality_checks": {
    "format_valid": true,
    "required_files_present": ["data/", "dataset_card.json", "README.md"],
    "spec_alignment": "<对齐 spec.md 的关键点列表>",
    "warnings": []
  }
}
```

**字段约束**：
- `name` / `domain` / `handler` / `source.dir` / `target.dir` / `target.created_at` / `target_schema.spec_source` / `quality_checks.format_valid` 为**强制字段**。
- 其余字段尽力填充；确实不可得时置 `null` 或省略，不得编造。

## README.md 模板

```markdown
# <dataset_name> AI-Ready Dataset

- **Domain**: <domain>
- **Handler**: <handler>
- **Generated at**: <ISO8601>
- **Source spec**: onescience-primitives:<domain>/datasets/<name>/spec.md

## Directory Layout

<从 dataset_card.json.target_schema.data_layout 渲染>

## Loading Example

<开箱即用示例，必须包含四部分：(1) 按 primary_format 读取主数据；(2) 遍历
split（train/val/test 或分片）；(3) 构造 batch；(4) 最小训练循环骨架
（model/optimizer 用占位注释标明，不引入具体深度学习框架）。从 primitives
usage.md 摘录或按 primary_format 生成，确保下游 trainer/用户复制即可接入训练。>

## Splits

<从 dataset_card.json.splits 渲染>

## Provenance

- Converter: <converter_script>
- Tier: <1|2>
- Duration: <seconds>s

## Regeneration

```bash
python <path-to-standardize.py> \
  --dataset-name <name> \
  --domain <domain> \
  --source-dir <source> \
  --target-dir <target>
```
```

## 校验规则

`scripts/standardize.py::validate_output` 强制执行：

1. `<target_dir>/dataset_card.json` 存在且 JSON 可解析。
2. `dataset_card.json` 包含全部强制字段。
3. `<target_dir>/data/` 存在且非空。
4. `<target_dir>/README.md` 存在且非空。
5. `dataset_card.json.name` == 传入的 `dataset_name`（大小写敏感）。
6. `dataset_card.json.domain` ∈ `{cfd, bio, climate, matchem}`。
7. `dataset_card.json.target.dir` == 传入的 `target_dir`（`realpath` 归一化后）。
8. 抽样 1 个 `data/` 下文件，尝试按 `primary_format` 打开；失败仅记 warning 不 fail（避免因可选依赖缺失导致误报）。

校验结果写入 `execution_result.observation.validation`。

## 与 primitives spec.md 的对齐原则

- `spec.md` 定义了每个数据集的**具体目标形态**（例如 ERA5 的 `fields: [T, C, H, W] = (1460, 243, 721, 1440)`）。
- 本契约定义**跨数据集的通用骨架**（目录结构、card schema、README）。
- 冲突时以 `spec.md` 为准；本契约未覆盖的字段由 adapter/converter 自行补齐并写入 `dataset_card.json.target_schema`。
