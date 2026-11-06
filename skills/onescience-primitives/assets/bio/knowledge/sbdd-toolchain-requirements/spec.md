# SBDD/扩散分子工具链与资源需求（平台侧，非环境安装步骤）

## scope

运行 SBDD 分子生成与评估链路的工具清单（RDKit/AutoDock Vina/Alphaville2 /TargetDiff 权重）

## condition

在科研/论文复现中规划 SBDD 分子工作（生成/排序/评估）时；安装动作由 installer 处理，本卡仅作资源与依赖清单

## 知识正文

- 【依赖】RDKit（化学结构/QED/SA 计算）、AutoDock Vina（对接打分，多配对）、AlphaFold2/ AlphaSpace 类（子口袋提取，DecompDiff 配套）
- 【模型】DecompDiff / TargetDiff 预训练权重（GitHub 公开）
- 【能力】PyTorch Geometric 等图学习栈（引导分子用 guide 网络）

## source_refs（可回溯）

| kid | uri | version | locator |
|---|---|---|---|
| KNOW-R-BD-003 | papers/2501.15631.pdf | v1 | §4 + §Evaluation |
| KNOW-R-TM-002 | papers/2406.01650.pdf | v1 | §4.4 + Appendix |

## 来源条目原文（kid -> body）

### KNOW-R-BD-003 (resource_requirement)

> 软件工具: RDKit(QED/SA), AutoDock Vina(对接), DecompDiff预训练权重(绕不开), AlphaSpace2(口袋提取, BoKDiff改造)。

### KNOW-R-TM-002 (resource_requirement)

> 软件: RDKit(QED/SA), AutoDock Vina, PyTorch Geometric/等变GNN, TargetDiff预训练权重。
