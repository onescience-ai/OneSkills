# TEM-1 Beta-Lactamase Deep Mutational Scanning Data Source

## 适用范围

本卡片描述 TEM-1 β-内酰胺酶（BLAT_ECOLX）深度突变扫描（DMS）数据集的公开来源、获取方式与格式规范，适用于需要获取真实 DMS 数据进行蛋白变异效应预测的任务。

## 输入

- 数据获取：从 Ranganathan Lab GitHub 仓库或 MaveDB 数据库下载
- 格式验证：CSV 文件，需验证列名与行数完整性

## 输出

- 标准 CSV 文件：BLAT_ECOLX_Ranganathan2015.csv
- 格式规范：至少包含 mutant、func_score 两列

## 流程节点

1. **数据源定位** → 确定 Ranganathan Lab GitHub 仓库路径或 MaveDB 条目
2. **下载与校验** → 下载 CSV 文件，验证行数（应为数千条突变）与列名
3. **格式转换** → 转换为任务所需的 input_files 格式

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据集标识 | BLAT_ECOLX_Ranganathan2015 | [1] | UniProt 蛋白标识符 + 作者 + 年份 |
| 突变数量 | ~5000 单点突变 | [1] | 覆盖 TEM-1 全部 263 个残基位点 |
| 功能得分列 | func_score | [1] | 对数富集比，反映突变对功能的影响 |
| 突变列 | mutant | [1] | 格式如 A23T（位置+野生型+突变型） |
| 野生型 | 序列起始于 MVSK | [1] | TEM-1 β-内酰胺酶标准序列 |

## 边界与分流

- **GitHub 仓库不可达**：尝试 MaveDB 替代数据源（https://www.mavedb.org/）
- **数据格式不匹配**：使用 dms_tools 或 dms-view 工具进行格式转换
- **缺少 func_score**：检查是否为 enrichment ratio 格式，需转换为 log-enrichment

## 质量检查

- 验证 CSV 行数：应在 5000-6000 条之间（覆盖 263 残基 × 19 替换）
- 验证列名：mutant、func_score 必须存在
- 验证野生型氨基酸：随机抽查 5 个位点，确认 func_score ≈ 0（中性）

## 回退策略

- 若主数据源不可用，使用 MaveDB API 查询 BLAT_ECOLX 条目
- 若格式转换失败，参考 dms_tools 文档（https://jbloomlab.github.io/dms_tools2/）手动映射列名

## 资源召回建议

- 在执行 TEM-1 DMS 数据下载步骤（s01）时召回本卡
- 配套资源：ESM-1v 模型卡（bio/models/esm1v-variant-effect-prediction）

## 补充证据

[D1] Ranganathan Lab DMS Data Repository, GitHub, URL: https://github.com/RanganathanLab/DMS-data（accessed_at 2026-09-21）
[D2] MaveDB - Multiplex Assays of Variant Effect Database, MaveDB Consortium, URL: https://www.mavedb.org/（accessed_at 2026-09-21）

## 证据来源

[1] Stiffler, M.A., Hekstra, D.R., Ranganathan, R. "Evolvability as a Function of Purifying Selection in TEM-1 β-Lactamase", Cell, 2015, DOI: 10.1016/j.cell.2015.09.049
[2] Fowler, D.M., Dobbs, A.J., et al. "Software for the analysis and visualization of deep mutational scanning data", BMC Bioinformatics, 2015, DOI: 10.1186/s12859-015-0494-4
[3] Hong, Z., Shimagaki, K.S., Barton, J.P. "popDMS infers mutation effects from deep mutational scanning data", Bioinformatics, 2024, DOI: 10.1093/bioinformatics/btae499
