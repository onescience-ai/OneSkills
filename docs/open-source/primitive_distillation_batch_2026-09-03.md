# Primitive Distillation Batch: 2026-09-03

本批次把 `scientific-agent-skills` 中可复用的科研能力蒸馏为 `onescience-primitives` 资源，采用 `resource_only` 策略，不复制上游弃用脚本，也不把源技能目录直接搬入目标仓库。

## 批次范围

| 来源技能 | Primitive ID | 类别 | 连接关系 |
| --- | --- | --- | --- |
| `scanpy` | `bio.tools.scanpy` | tool | 被单细胞 application 消费 |
| `anndata` | `bio.components.anndata` | component | 单细胞共享数据容器 |
| `cellxgene-census` | `bio.datasets.cellxgene_census` | dataset | 公共参考图谱查询 |
| `scvelo` | `bio.tools.scvelo` | tool | 单细胞 velocity 分支 |
| `scvi-tools` | `bio.tools.scvi_tools` | tool | 模型、整合、迁移学习分支 |
| `pydeseq2` | `bio.tools.pydeseq2` | tool | pseudobulk / bulk DE 分支 |
| `experimental-design` | `general.workflow-planning.experimental_design` | workflow-planning | 试验前设计和随机化 |
| `statistical-analysis` | `general.tools.statistical_analysis` | tool | 统计方法和结果解释 |
| `statistical-power` | `general.workflow-planning.statistical_power` | workflow-planning | 样本量和效能规划 |
| `scientific-visualization` | `general.visualization.scientific_visualization` | visualization | 图形设计和交付审查 |
| `database-lookup` | `general.databases.public_database_lookup` | database | 公共 API 检索契约 |
| `citation-management` | `general.databases.citation_management` | database | 学术元数据和引用核验 |
| `nextflow` | `general.workflow-planning.nextflow_workflow` | workflow-planning | 可复现流程编排 |
| `literature-review` | `general.workflow-planning.literature_review` | workflow-planning | 系统综述和证据综合 |
| `scientific-writing` | `general.workflow-planning.scientific_writing` | workflow-planning | 证据绑定的论文/报告写作 |
| `markdown-mermaid-writing` | `general.output-format.markdown_mermaid` | output-format | 文档和结构图文本源 |
| `docx` | `general.output-format.docx` | output-format | Word 文档交付 |
| `pdf` | `general.output-format.pdf` | output-format | 固定版式和归档交付 |
| `pptx` | `general.output-format.pptx` | output-format | 研究演示文稿交付 |

## 统一蒸馏规则

- `metadata.json` 保存稳定 `primitive_id`、provider、来源版本和蒸馏状态。
- `spec.md` 保存输入、输出、依赖、边界和实现风险。
- `usage.md` 保存安装、典型用法和操作限制。
- `workflow_planning.md` 保存适用范围、步骤、fallback 和 handoff 字段。
- 所有本批次资源均为 `resource_only`，`copied_execution_assets: false`。
- 只有经过白名单、hash 和运行边界审查后，才考虑将具体脚本提升为 execution asset。

## 消费者接入

`bio.application.bio_single_cell_analysis_app` 已显式依赖：

- `bio.components.anndata`
- `bio.datasets.cellxgene_census`
- `bio.tools.scanpy`
- `bio.tools.scvi_tools`
- `bio.tools.scvelo`
- `bio.tools.pydeseq2`

应用卡仍只描述任务边界和交接字段；实际安装、命令执行、模型训练和结果收集由对应 executor/runtime 负责。

## 后续批次

后续继续按同一规则扩展：

1. 优先补齐 `bio` 中常用数据库、数据管线和实验平台能力。
2. 批量覆盖 `cfd`、`climate`、`matchem` 的第三方工具和数据源。
3. 对重复出现且输入输出稳定的资源，再单独评估 executor 化。
4. 保留来源和版本，不把上游 skill 的历史脚本当成 OneScience 自有执行能力。
