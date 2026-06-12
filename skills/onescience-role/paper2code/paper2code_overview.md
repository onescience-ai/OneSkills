# Paper2Code 论文复现流水线概览

本文件给 `onescience-role` 提供论文复现任务的领域语义约束、流水线阶段定义与角色链组装依据。

## 领域画像

论文复现（paper2code）是一个横向科研任务方法，而不是独占科学领域。它可以与 `earth`、`biology`、`materials`、`cfd` 或 `general-science` 等真实 `domain_route` 组合，其特点是：

- **输入**：一篇学术论文来源（arXiv ID/URL、PDF/HTML URL、本地 PDF、DOI、论文标题、粘贴文本或已知论文名）
- **输出**：`onescience-paper-repro` 生成的论文工作目录、审计用 `reproduction_spec.md`、自包含 `coder_task_description.md`，随后由 `onescience-coder` 只基于 `coder_task_description.md` 和 OneScience 内部资产生成代码
- **核心挑战**：论文描述往往存在歧义，需要系统性地识别并处理未明确指定的实现细节

## 工作目录约定

论文复现的下载材料与中间分析文件由 `onescience-paper-repro` 保存到当前项目根目录下的 `.paper2code_work/<paper_key>/`。role 层必须在交接物中传递这一约束：

- 能识别 arXiv ID 时，`paper_key` 固定为不带版本号的 arXiv 编码，例如 `2406.01465`，工作目录为 `.paper2code_work/2406.01465/`。
- 输入为 `2406.01465v2` 时，工作目录仍为 `.paper2code_work/2406.01465/`，版本号写入 `reproduction_spec.md` 的论文来源与元数据。
- 若只有标题或 DOI，先由 `onescience-paper-repro` 解析论文/arXiv 来源；暂时无法识别 arXiv ID 时可使用标题 slug 或 DOI slug 作为临时 `paper_key`，后续解析到 arXiv ID 后迁移到 `.paper2code_work/<arxiv_id>/`。
- 用户指定的 `output_dir` 只表示最终复现代码生成位置，不用于保存论文 PDF、解析文本、中间分析、`reproduction_spec.md` 或 `coder_task_description.md`。

推荐工作目录产物包括：`paper.pdf`、`paper_text.md`、`paper_sections/`、`figures_tables.md`、`extraction_notes.md`、`reproduction_spec.md`、`coder_task_description.md` 和按需生成的 `download_errors.md`。不要额外生成 `paper_source.json` 或 `evidence_index.md`；来源信息和证据位置写入 `reproduction_spec.md`。

## 四阶段前处理流水线

论文复现先由 `onescience-paper-repro` 完成四阶段前处理。阶段顺序不可倒置；如果上游已经提供并可校验某阶段 artifact，可以将该阶段标记为已满足，但不能在缺少复现规格与歧义审计时直接进入 `onescience-coder`：

### Stage 1: 论文获取与解析 (Paper Acquisition)
- 职责：识别论文来源，规范化 `.paper2code_work/<paper_key>/`，下载或复制论文材料，解析正文、图注、表格、算法框、附录和补充材料
- 产出：`paper.pdf`、`paper_text.md`、`paper_sections/`、`figures_tables.md`；论文来源和证据位置后续写入 `reproduction_spec.md`

### Stage 2: 复现信息抽取 (Reproduction Extraction)
- 职责：按任务、数据、处理、模型、损失、训练、推理、评估、配置和领域专属信息抽取复现规格
- 产出：`reproduction_spec.md`

### Stage 3: 歧义审计 (Ambiguity Audit)
- 职责：在写代码之前，系统性审查实现相关细节，分类为明确给出、推断得到、未说明但实现需要选择
- 产出：写入 `reproduction_spec.md` 的 `MISSING:`、`INFERRED:`、`ASSUMPTION:` 和 `implementation_code_used=false` 约束

### Stage 4: Coder 任务描述 (Coder Task Description)
- 职责：把论文复现规格展开成 `onescience-coder` 可直接消费的完整自然语言任务描述，完整覆盖 `reproduction_spec.md` 中所有已确定内容
- 产出：`coder_task_description.md`

随后由 `onescience-paper-repro` 交接 `paper_repro_handoff=true`、`task_description_path` 和 `task_description_content` 给 `onescience-coder`。`coder_task_description.md` 必须完整覆盖 `reproduction_spec.md` 中所有已确定内容；`reproduction_spec.md` 只作为用户审计和追溯产物，不作为 coder 编码输入。代码目录、训练脚本、配置和 notebook 由 coder 阶段生成。
交接中还必须包含 `paper_workdir=.paper2code_work/<paper_key>`；若用户指定最终代码位置，再附带 `output_dir=<用户指定目录>`。

## 模式约束

- **minimal**（默认）：只实现核心贡献。如果贡献不涉及训练，不生成 train.py
- **full**：核心贡献 + 完整训练/数据/评估管线
- **educational**：同 minimal，但附带教育性注释和 PAPER_GUIDE.md

## 框架约束

- **pytorch**（默认）
- **jax**
- **numpy**

## 核心原则

1. **证据锚定**：复现规格中的关键结论必须锚定到论文 section/table/figure/equation/page。
2. **诚实标记**：论文未说明但实现必须选择的项必须标记为 `MISSING:`、`INFERRED:` 或 `ASSUMPTION:`。
3. **歧义优先于猜测**：遇到歧义时记录歧义，不要把推断写成论文事实。
4. **稳定交接**：`coder_task_description.md`、`task_description_content` 和 `paper_workdir` 是进入 `onescience-coder` 的必要输入；`reproduction_spec.md` 是前处理审计产物。
5. **禁止实现仓库路径**：不要搜索、打开、下载、clone、复制或参考官方/第三方已实现代码；复现必须从论文文本、用户材料和 skills 规则重新生成。

## 与通用 OneScience 执行链的关系

论文复现是端到端流程，但实际获取、解析、复现规格抽取和完整任务描述生成由 `onescience-paper-repro` 承接；代码生成与 notebook 写出由 `onescience-coder` 消费 `coder_task_description.md` 完成。role 层的职责是拆解阶段、识别角色链、产出交接物，而不是直接下载论文、解析正文或写代码。
