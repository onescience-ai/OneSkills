---
name: onescience-bio-domain
description: OneScience 生物信息领域总路由。用于 biology、bioinformatics、biosciences、生信、蛋白、基因、组学、单细胞、空间组学、变异检测、结构预测、蛋白设计、药物设计、公共数据库、实验室数据、临床研究等请求中，按范畴选择具体生信 skill，区分 OneScience 模型任务与通用生信分析任务，并生成角色交接物。
---

# OneScience 生物信息领域总路由

你负责给 `onescience-role` 补充生物信息领域的范畴路由：先判断用户任务属于哪个生信能力范畴，再读取该范畴下的具体 skill。不要只停留在“workflow / tools”这种粗粒度标签；要继续下钻到可执行、可交接的具体生信 skill。

本 skill 不写最终代码，不替代 `onescience-coder`。它负责把生信任务整理成清晰边界、最小角色链和下游执行入口。

需要确认本层职责边界时，先读取 `./boundary_contract.md`。
需要判断 `references/`、`templates/`、`scripts/` 当前应如何使用或后续如何迁移时，读取 `./asset_inventory.md`。

## 范畴划分

按下面顺序选择最小范畴：

1. **OneScience 生信模型推理**：执行当前 OneScience 代码仓已有生信模型的 inference / predict / sampling / generation，关注输入协议、checkpoint、设备、命令入口、输出校验和失败恢复。
   - 读取 `./bio-inference/SKILL.md`。
2. **OneScience 生信模型开发**：模型结构、模块替换、训练、微调、checkpoint、batch 协议、datapipe adapter、`examples/biosciences` 源码改造。
   - 读取 `./onescience-models/SKILL.md`。
3. **端到端生信流程**：RNA-seq、单细胞、空间组学、变异、表观组、微生物组、蛋白质组、代谢组、多组学、免疫信息，以及需要编排多个 OneScience 生信模型的蛋白设计到结构验证分析链路。
   - 读取 `./workflows/SKILL.md`。
4. **数据基础设施**：序列读写、FASTQ QC、比对文件、VCF/BED、公共数据接入、samplesheet。
   - 读取 `./data-foundation/SKILL.md`。
5. **分析工具箱**：Python/R 分析库、单细胞工具、化学信息、质谱、统计可视化。
   - 读取 `./analysis-tools/SKILL.md`。
6. **知识库与数据库**：文献、序列、变异、通路、结构、化合物、单细胞图谱数据库查询。
   - 读取 `./knowledge-databases/SKILL.md`。
7. **临床、实验室与质量**：实验设计、临床方案、仪器数据标准化、QC 报告和可复现交付。
   - 读取 `./clinical-lab-quality/SKILL.md`。
8. **分子生物学设计与验证**：引物/探针、CRISPR guide、限制性酶切、克隆图谱、质粒注释、RNA 二级结构。
   - 读取 `./molecular-biology-design/SKILL.md`。
9. **细胞图像、流式与空间表型**：FCS/流式门控、CyTOF/IMC、显微图像分割、全切片病理图像、显微图像管理。
   - 读取 `./cell-imaging-cytometry/SKILL.md`。
10. **群体遗传、系统发育与进化基因组学**：GWAS、群体结构、选择扫描、系统树、比较基因组、单倍型、病原基因组监测。
   - 读取 `./population-phylo-evolution/SKILL.md`。
11. **转化医学与生物标志物**：cfDNA/ctDNA、临床变异、肿瘤基因组、因果基因组学、标志物机器学习、药物基因组与风险评分。
   - 读取 `./translational-biomarker/SKILL.md`。
12. **实验协议与自动化交接**：液体处理、实验协议检索、ELN/样本注册、Western blot/凝胶等实验图像定量。
   - 读取 `./experimental-protocol-automation/SKILL.md`。

## 总路由原则

1. 优先消费 workflow handoff 中的 `domain_route=biology`、`domain_task_family`、`stage_intent` 与 `planning_only`。
2. 先判定 `bio_task_family`，再判定是否 `onescience_model_related`。
3. 只要是执行已有 OneScience 生信模型推理，先进入 `bio-inference`；只有涉及模型结构、训练、微调、数据 batch 协议改造或模型内部模块，才进入 `onescience-models`，并以 OneScience 源码和 `onescience-coder` 模型卡为准。
4. 传统生信分析不默认归入 OneScience 模型。FASTQ、BAM、VCF、count matrix、h5ad、mzML、FCS、TIFF、WSI、Newick、GWAS summary stats 等输入通常先进入对应领域范畴。
5. 数据库和工具任务不虚构成完整 pipeline；只交接查询字段、输入格式、返回字段、可复现版本。
6. 如果任务要在远程硬件运行，仍按主链交给 `onescience-skill`，再由执行层进入 `onescience-runtime` 的 `discover/preflight/execute/diagnose` 闭环；若 preflight 发现环境未 ready，再回退 `onescience-installer`。
7. `templates/` 与 leaf `references/` 是领域资产，不是 role 层执行动作；执行脚本必须位于 coder/runtime/installer 资产层或 `{onescience_path}/onescience` 下的 OneScience 仓库资产，role 只引用资产路径形成交接摘要，不直接运行或写入最终文件。

## 最小输出

至少给出：

1. `bio_task_family`
2. `onescience_model_related`
3. `selected_category_skill`
4. `selected_concrete_skill`
5. `current_role`
6. `role_chain`
7. `handoff_artifacts`
8. `execution_entry`
9. `planning_only`

如果命中 OneScience 生信模型推理或开发，再额外给出：

10. `onescience_model_family`
11. `input_protocol`
12. `source_anchors`
13. `coder_assets_to_read`
14. `inference_preflight_status`
15. `output_validation_plan`

## 禁止事项

- 不要只输出范畴名；必须继续选择范畴下的具体 skill。
- 不要把传统 RNA-seq、variant calling、single-cell QC 等 workflow 硬路由成 OneScience 模型。
- 不要把 clinical trial、LIMS、Allotrope 这类生命科学运营任务误判成核心生信建模任务。
- 不要在未确认数据模态、物种、参考版本、输入格式和交付目标前，拉起完整执行链。
- 不要在 role 层直接运行工具脚本、重新新增 `scripts/` 目录，或生成最终 `templates/` 文件。
- 不要把 `bio_domain` 下的 leaf `SKILL.md` 宣称为顶层公开 skill。
