# Converter 编写规范：Tier1 Adapter 与 Tier2 LLM 合成

本文档定义两层转换器的编写规则、接口约定与选择逻辑。

## Tier 判定规则

```python
def select_tier(domain: str, dataset_name: str) -> tuple[int, str]:
    adapter_rel = f"scripts/adapters/{domain}/{dataset_name.lower().replace('-', '_')}.py"
    adapter_abs = SKILL_ROOT / adapter_rel
    if adapter_abs.exists():
        return 1, f"adapter:{domain}/{dataset_name.lower()}"
    return 2, "llm_synth:v1"
```

**大小写与连字符归一化**：`dataset_name` 转小写、`-` 替换为 `_` 后与 adapter 文件名比对。例如 `DeepCFD` → `deepcfd.py`；`s2ef-200k` → `s2ef_200k.py`。

## Tier1: Adapter 编写规范

### 文件位置

`scripts/adapters/<domain>/<dataset_name_lowercase>.py`

### 必须继承的基类

```python
from scripts.adapters._base import BaseAdapter

class MyAdapter(BaseAdapter):
    domain = "climate"
    dataset_name = "ERA5"
    primary_format = "hdf5"

    def probe(self, source_dir: Path) -> dict:
        """探测 raw 数据结构，返回探测报告（dict）"""

    def plan(self, probe_report: dict, spec: dict) -> dict:
        """基于探测报告与 primitives spec，输出转换计划"""

    def convert(self, source_dir: Path, target_dir: Path, plan: dict) -> None:
        """执行转换，把结果写入 target_dir"""

    def post_process(self, target_dir: Path) -> None:
        """可选：生成 stats/splits/static 等派生产物"""
```

### CLI 契约

每个 adapter 必须支持独立 CLI 调用：

```bash
python scripts/adapters/<domain>/<name>.py \
  --source-dir <绝对路径> \
  --target-dir <绝对路径> \
  [--spec-json <primitives spec 序列化 JSON 路径>] \
  [--dry-run]
```

- `--source-dir` / `--target-dir` **必须**从 argv 读入，禁止硬编码。
- `--spec-json` 可选，未提供时 adapter 从内置默认契约推断。
- `--dry-run` 只输出计划不执行写入，用于诊断。

### 输出义务

Adapter 执行完毕后，必须调用基类提供的辅助函数：

```python
self.write_dataset_card(target_dir, card_dict)   # 写 dataset_card.json
self.write_readme(target_dir, readme_str)        # 写 README.md
```

`dataset_card.json` 必须满足 [ai_ready_contract.md](./ai_ready_contract.md) 定义的 schema。

### 依赖声明

Adapter 顶部必须有 `# requirements:` 注释行，列出运行所需 pip 包：

```python
# requirements: h5py>=3.0, netCDF4>=1.6, numpy>=1.24, xarray>=2023.1
```

主入口 `standardize.py` 会读取该行并在依赖缺失时给出诊断信息（不自动安装，避免污染环境）。

### 错误处理

- 依赖缺失 → 抛出 `AdapterDependencyError("missing: h5py; install with: pip install h5py")`。
- 输入格式不符合预期 → 抛出 `AdapterInputError("expected NetCDF, got <ext>")`。
- 转换过程失败 → 抛出 `AdapterConversionError("<细节>")`，且必须在 `target_dir` 留下 `.failed` 标记文件以便诊断。
- 主入口捕获上述异常后映射到 `execution_result.status=failed, blocked_reason=converter_failed`。

### 本期交付的四个参考 Adapter

| domain | 文件 | 转换内容 |
|---|---|---|
| climate | `scripts/adapters/climate/era5.py` | raw NetCDF/grib → 年度 HDF5 (`data/YYYY.h5`) + `static/` + `stats/global_means.npy` + `stats/global_stds.npy` |
| cfd | `scripts/adapters/cfd/deepcfd.py` | raw pickle 目录 → 规范化 `data/dataX.pkl` + `data/dataY.pkl` 配对，校验样本数一致、通道数、shape |
| bio | `scripts/adapters/bio/targetdiff.py` | raw PDB pocket + SDF ligand + index.pkl → LMDB 图缓存 (`data/<split>.lmdb`) + `splits/` |
| matchem | `scripts/adapters/matchem/oc20.py` | raw extxyz (`s2ef_200k_uncompressed/*.extxyz`) → ASE LMDB 分片 (`data/train/data.000N.aselmdb`) + `metadata.npz` |

每个 adapter 都是**可独立运行的最小闭环**，不依赖 primitives 之外的私有知识。

## Tier2: LLM 合成 Converter

### 触发条件

`scripts/adapters/<domain>/<name>.py` 不存在时进入。

### 合成流程

`scripts/llm_converter/synthesize.py` 编排：

1. **探测 raw**（`probe_raw`）：
   - 递归列目录（最多 3 层深度，最多 200 条条目）；
   - 抽样读文件头（前 4KB）识别 magic bytes；
   - 按扩展名归类：`.nc/.h5/.hdf5/.pkl/.npz/.npy/.pdb/.cif/.mmcif/.sdf/.mol2/.csv/.tsv/.lmdb/.aselmdb/.extxyz/.h5ad/.zarr/.fasta/.json/.yaml`；
   - 对可解析格式抽样打开一个文件读元信息（shape/dtype/keys/attrs）；
   - 输出 `raw_probe_report.json`（结构见下）。

2. **拉取 primitives spec**（由主流程阶段 3 已完成，直接消费）。

3. **组装 prompt**：
   - `prompts/system.md` 作为 system message；
   - `prompts/user.md.j2` 作为 user message，注入变量：
     - `spec_md_full` / `usage_md_full`（primitives 返回的正文）；
     - `raw_probe_report`（JSON 字符串）；
     - `ai_ready_contract`（[ai_ready_contract.md](./ai_ready_contract.md) 全文）；
     - `domain` / `dataset_name`；
     - `few_shot_adapter_source`（**同 domain 的 Tier1 adapter 源码**，如 bio 用 targetdiff.py；该 domain 无 Tier1 时跨 domain 取 ERA5 作为通用样例）。

4. **委托生成**：
   - 优先向 orchestrator 建议下一步调用 `onescience-coder`（`step_goal=生成数据转换脚本`, `resource_bindings=[spec.md, raw_probe_report, ai_ready_contract]`）；
   - orchestrator 不可达或宿主环境无 coder → 回退到宿主 Agent 直接生成（即本技能所在的 Agent runtime）。

5. **静态校验**（`scripts/llm_converter/validate_generated.py`）：
   - `ast.parse` 通过（语法有效）；
   - 禁止：字符串常量形式的绝对路径（正则 `["\']/(home|data|public|mnt|Users|C:)` 命中即拒）；
   - 禁止：`os.environ.get` 硬取路径（对齐 [onescience-data-profile SKILL.md](file:///e:/works/zhognkeshuguang/data_management/oneskills-work/skills/onescience-data-profile/SKILL.md) 中 "生成的代码必须从参数读取输入输出路径" 约束）；
   - 必须：`import argparse` 或 `from argparse`；
   - 必须：调用 `write_dataset_card`（或内联写 `dataset_card.json` 的等价代码）；
   - 必须：定义 `def main(` 或 `if __name__ == "__main__":` 入口。
   - 校验失败 → 反馈错误给生成方，最多重试 2 次；仍失败 → `status=failed, blocked_reason=converter_failed`。

6. **落盘**：脚本写入 `<target_dir>/_converter/convert_<dataset_name_lowercase>.py`；同时保存 `prompt_snapshot.md` 与 `raw_probe_report.json` 供审计。

7. **执行**：
   - 优先委托 `onescience-runtime`；
   - 降级为 `subprocess.run([sys.executable, script, "--source-dir", src, "--target-dir", tgt], check=True, timeout=<configurable>)`。

### raw_probe_report.json 结构

```json
{
  "source_dir": "<绝对路径>",
  "total_files": 1234,
  "total_bytes": 5678901234,
  "directory_tree": [
    {"path": "data/", "type": "dir", "children_count": 100},
    {"path": "data/1979.nc", "type": "file", "size": 12345, "ext": ".nc"}
  ],
  "format_histogram": {
    ".nc": 100, ".h5": 50, ".pkl": 20
  },
  "samples": [
    {
      "path": "data/1979.nc",
      "format": "netcdf",
      "variables": ["t2m", "u10", "v10"],
      "dimensions": {"time": 1460, "latitude": 721, "longitude": 1440},
      "attrs": {"Conventions": "CF-1.6"}
    }
  ],
  "detected_patterns": [
    "按年分文件的 NetCDF 时序数据",
    "存在 static 场候选（geopotential.nc）"
  ]
}
```

### Prompt 关键约束（写入 `prompts/system.md`）

- 只输出**一个可执行 Python 脚本**，不接受解释性文本、Markdown 代码块围栏外的任何内容。
- 脚本必须从 `argparse` 读 `--source-dir` 与 `--target-dir`；禁止硬编码路径。
- 必须写 `<target_dir>/dataset_card.json`（schema 见 ai_ready_contract.md）与 `<target_dir>/README.md`。
- 必须在 `<target_dir>/data/` 下组织主数据；`static/stats/splits/` 按需创建。
- 必须处理 raw 探测报告中列出的**全部**主要文件格式；不得忽略。
- 依赖必须在脚本顶部 `# requirements:` 注释中列出。
- 遇到无法处理的格式必须抛出 `RuntimeError` 并附诊断信息，不得静默跳过。
- 输出脚本必须通过 `validate_generated.py` 的 AST 静态校验。

## Tier2 生成脚本提升为 Tier1 的路径

当某个数据集的 Tier2 脚本被反复使用（例如注册表中同一 `name` 被更新 3 次以上），建议人工审校后提升：

1. 复制 `<target_dir>/_converter/convert_<dataset>.py` 到 `scripts/adapters/<domain>/<dataset>.py`；
2. 重构为继承 `BaseAdapter` 的类形式；
3. 补充 `probe` / `plan` / `convert` / `post_process` 四段接口；
4. 在 adapter 顶部添加 `# requirements:` 行；
5. 提交 PR，`converter_authoring.md` 的参考 adapter 清单同步更新。

## 常见陷阱

- **不要在 adapter 里做 primitives 的 spec 拉取**：spec 由主流程阶段 3 拉取后以 `--spec-json` 传入；adapter 内部再拉会违反 primitives 强制协议。
- **不要在 Tier2 prompt 里包含 `onescience-primitives/assets/` 的文件路径**：只包含 `spec.md` 正文内容，避免生成脚本尝试直读 primitives 目录。
- **不要跳过 `dataset_card.json`**：这是本技能与下游（如 `dataset_report`）的唯一契约锚点。
- **不要把 raw 数据复制到 target_dir**：只保留转换后的产物；raw 数据通过 `dataset_card.json.source.dir` 引用。
