---
name: onescience-paper-repro
description: 面向 OneScience 的论文复现前处理技能。用于用户要求复现论文、实现论文、paper to code、根据论文生成代码，或上游传递 task_method=paper2code / domain_task_family=paper-reproduction 时，负责下载或读取论文、解析论文内容、抽取复现所需信息，只生成 reproduction_spec.md 与 coder_task_description.md 两个核心产物；coder_task_description.md 必须完整承载 reproduction_spec.md 中所有已确定的实现相关内容，并作为 onescience-coder 唯一消费的编码任务输入。
---

# OneScience 论文复现前处理

## 职责边界

本技能只负责把论文转成可执行的复现规格，不直接实现模型代码。

当用户提供论文标题、DOI、arXiv 链接、PDF 链接、本地 PDF、正文片段，或明确要求“复现论文 / 实现论文 / 根据论文生成代码 / paper to code”时，先使用本技能完成论文获取、解析、信息抽取和任务描述生成，再把产物交给 `onescience-coder`。

不要搜索、打开、下载、clone、复制或参考 GitHub/GitLab/Bitbucket、official code、repository、source code、model zoo、package implementation、官方实现或第三方复现。论文复现规格必须来自论文正文、附录、补充材料、用户提供材料和公开数据/论文页面信息；若论文没有说明，实现必须选择的项要标记为待决策假设。

## 总控流程

本技能把论文材料转换成 `onescience-coder` 可直接消费的复现任务书。总控流程只负责编排阶段，不在主技能文件中写领域特例或单篇论文特例。

核心产物只有：

- `reproduction_spec.md`：前处理阶段的结构化事实源和审计产物。
- `coder_task_description.md`：下游唯一编码输入，必须完整承载 `reproduction_spec.md` 中所有已确定内容。

`onescience-coder` 只消费 `coder_task_description.md` 的路径和全文，不读取 `reproduction_spec.md` 补齐细节。

执行时按顺序读取以下独立 workflow：

1. `./references/acquisition_text_workflow.md`
   - 负责论文来源识别、PDF/正文获取、文本提取、内容完整性校验和工作目录组织。
2. `./references/structured_extraction_workflow.md`
   - 负责解析论文正文、表格、图注、算法框、附录和补充材料，先生成 `paper_content_summary.md`，再根据摘要召回领域知识并生成结构化 `reproduction_spec.md`。
3. `./references/audit_workflow.md`
   - 负责把 `reproduction_spec.md` 对照论文内容迭代校验和修复，直到 spec 正确或只剩明确 `MISSING:` / `ASSUMPTION:`。
4. `./references/coder_handoff_workflow.md`
   - 负责从审计后的 `reproduction_spec.md` 展开生成自包含 `coder_task_description.md`，并完成交接。

解析论文和审计时，先总结论文内容，生成 `paper_content_summary.md`；再根据摘要中的任务、数据对象、模型关键词和评估关键词，读取 `./assets/domain_knowledge/` 下各领域文件的表头摘要，召回对应领域知识：

- `earth.md`：气象、海洋、地球系统。
- `cfd.md`：流体、PDE、CFD。
- `materials.md`：材料、化学、原子尺度建模。
- `biology.md`：生信、生命科学。

领域知识只能辅助提取和审计，不得覆盖论文证据；如果领域经验与论文描述冲突，以论文正文、表格、公式、算法框、附录和补充材料为准。领域知识中的字段只有被论文或用户材料支持时，才能写入确定要求。

## 工作顺序

1. 识别论文来源：本地 PDF、URL、arXiv/DOI、标题检索或用户粘贴正文。
2. 解析并规范化论文工作目录：
   - 必须把下载或复制的论文材料保存到 `.paper2code_work/<id>/`。
   - `<id>` 优先使用不带版本号的 arXiv ID；没有 arXiv ID 时使用 DOI slug；仍无法识别时使用标题 slug。
   - 若能识别 arXiv ID，固定使用 `.paper2code_work/<arxiv_id>/`，例如 `.paper2code_work/2406.01465/`。
   - 下载的论文 PDF、补充材料、解析文本、摘要、结构化规格和交接任务书都写入该目录。
   - 用户指定的输出目录只表示最终复现代码落点，不改变论文解析工作目录。
3. 按顺序加载并执行：
   - `./references/acquisition_text_workflow.md`：下载、提取文本和内容完整性校验。
   - `./references/structured_extraction_workflow.md`：解析论文、生成 `paper_content_summary.md`，根据摘要召回领域知识，并生成结构化 `reproduction_spec.md`。
   - `./references/audit_workflow.md`：对照论文内容审计并修复 `reproduction_spec.md`，直到 spec 正确或只剩明确缺口/假设。
   - `./references/coder_handoff_workflow.md`：生成自包含 `coder_task_description.md` 并交接给 coder。
4. 在论文工作目录中生成两个核心产物：
   - `reproduction_spec.md`：中文为主、全面且准确的结构化复现规格，必须覆盖论文来源元数据、证据位置、任务、数据、处理、模型、损失、训练、推理、评估、配置、领域专属信息、缺口和假设；不能只抽取摘要或主方法。
   - `coder_task_description.md`：中文为主、清楚详细且自包含的自然语言实现任务描述，必须从 `reproduction_spec.md` 展开生成，并完整覆盖其中所有已确定内容；不得只写摘要、不得要求 `onescience-coder` 再读取 `reproduction_spec.md` 才能获得完整细节。
   - 不要生成 `paper_source.json`、`evidence_index.md` 这类额外交接文件；来源信息和证据位置直接写入 `reproduction_spec.md`。
   - 生成后必须逐条核对 `reproduction_spec.md` 的每个非空、非纯缺失项是否已进入 `coder_task_description.md`；没有进入的内容要补写，不能留给下游自行综合。
   - 生成前必须完成一致性审计：变量清单与通道数、输入/输出 shape、时间步融合、per-node/per-edge learnable features、loss target、权重公式、评估指标和所有实现假设不得自相矛盾；论文未明确给出的公式或数据格式只能写为 `ASSUMPTION:`，不能写成事实。
   - 涉及变量数和通道数时，必须生成 `variable_channel_ledger.json` 并用 `./scripts/variable_channel_audit.py` 做机械校验；校验失败不得交接给 `onescience-coder`。
5. 交接给 `onescience-coder` 时必须显式提供：
   - `paper_repro_handoff=true`
   - `task_method=paper2code`
   - `domain_task_family=paper-reproduction`
   - `task_description_path=<coder_task_description.md 路径>`
   - `task_description_content=<coder_task_description.md 全文>`
   - `paper_workdir=<.paper2code_work/<arxiv_id>/ 路径>`
   - `coder_reference_mode=assets_only`
   - `coder_static_review_required=true`
6. `reproduction_spec_path` 可在给用户的结果中保留用于审计和追溯，但不要把它作为 `onescience-coder` 的编码输入；`onescience-coder` 只消费 `coder_task_description.md` 的路径和全文执行编码任务。
7. 交接给 `onescience-coder` 前，必须在回复中复述 `coder_task_description.md` 的完整内容；不能只给路径，也不能只复述主要内容。

## 输出要求

最终回复至少包含：

- 已解析的论文来源与保存位置
- 论文工作目录，例如 `.paper2code_work/2406.01465/`
- `reproduction_spec.md` 路径
- `coder_task_description.md` 路径
- `coder_task_description.md` 的完整内容复述
- 关键缺口或实现假设
- 下一步交接：`next_action=onescience-coder`

如果论文无法获取或解析，不要编造细节；输出已获得信息、缺失项和需要用户补充的最小材料。
