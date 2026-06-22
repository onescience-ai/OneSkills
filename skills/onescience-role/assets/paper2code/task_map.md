# Paper2Code 任务映射

本文件给 `onescience-role` 提供论文复现任务的具体任务桶拆解与角色交接物规范。

## 任务桶总览

论文复现任务拆分为以下任务桶，与 `onescience-paper-repro` 前处理流水线对应：

| 任务桶 | 对应阶段 | 角色 | 产出 |
|--------|----------|------|------|
| `paper-setup` | Stage 1: 论文获取与解析 | paper-analyst | `.paper2code_work/<paper_key>/`、论文文本、图表/方程摘录 |
| `paper-extraction` | Stage 2: 复现信息抽取 | paper-analyst | `reproduction_spec.md` |
| `paper-audit` | Stage 3: 歧义审计 | paper-analyst | 写入 `reproduction_spec.md` 的缺口与假设 |
| `paper-coder-brief` | Stage 4: Coder 任务描述 | paper-reproducer | `coder_task_description.md` |

## 任务桶详细说明

### `paper-setup` — 论文获取与解析

**输入**：`paper_source`、可选 `arxiv_id`、mode、framework、真实 `domain_route`、可选 `output_dir`
**行为**：
1. 识别论文来源：本地 PDF、URL、arXiv/DOI、标题或粘贴文本。
2. 规范化工作目录：能识别 arXiv ID 时使用 `.paper2code_work/<arxiv_id>/`，例如 `.paper2code_work/2406.01465/`；带版本号时目录去掉版本号。
3. 下载或复制论文材料到工作目录，PDF 保存为 `paper.pdf`；粘贴文本保存到 `paper_text.md`。
4. 解析正文、图注、表格、算法框、附录、补充材料和实验设置，写入 `paper_text.md`、`paper_sections/`、`figures_tables.md`。
5. 题名、作者、年份、arXiv ID/版本、DOI、来源 URL 或本地原始路径、访问时间、证据位置和 `implementation_code_used=false` 后续直接写入 `reproduction_spec.md`；不要生成 `paper_source.json` 或 `evidence_index.md`。
6. 下载或解析失败时写入 `download_errors.md`。
7. 不检索、不打开、不记录官方/第三方实现仓库；若论文正文自然包含代码链接，也只在审计说明中标记为未使用。

**验证点**：
- 论文文本或用户粘贴内容可读且包含足够的标题/摘要/方法/实验信息
- 论文工作目录符合 `.paper2code_work/<arxiv_id-or-paper_key>/`
- 交接摘要明确记录 `implementation_code_used=false`

### `paper-extraction` — 复现信息抽取

**输入**：paper_setup 的产出 + 论文文本
**行为**：
1. 精读论文正文、图注、表格、算法框、附录和补充材料
2. 抽取任务、数据、数据处理、模型结构、损失、训练、推理、评估、可复现配置和领域专属信息
3. 记录每个关键结论的证据位置
4. 区分明确给出、推断得到、未说明但实现必须选择的项
5. 在论文工作目录中生成 `reproduction_spec.md`

**产出**：`reproduction_spec.md`

### `paper-audit` — 歧义审计

**输入**：`reproduction_spec.md` + 论文全文
**行为**：
1. 遍历任务、数据、架构、损失、训练、推理、评估和配置细节
2. 对每个细节分类：明确给出 / 推断得到 / 未说明但实现必须选择
3. 用 `MISSING:`、`INFERRED:`、`ASSUMPTION:` 标记缺口、推断和必要假设
4. 记录数据泄漏、shape 不完整、split 不明确、评估协议缺失等高风险项

**产出**：更新后的 `reproduction_spec.md`

### `paper-coder-brief` — Coder 任务描述

**输入**：审计后的 `reproduction_spec.md`
**行为**：
1. 将复现规格展开为完整、自包含的自然语言实现任务
2. 明确领域、任务类型、输入输出、数据处理、模型结构、损失、训练、推理、评估和实现缺口
3. 确保 `coder_task_description.md` 完整覆盖 `reproduction_spec.md` 中所有已确定内容，不能只写摘要
4. 附带 `paper_repro_handoff=true`、`task_description_path`、`task_description_content`、`paper_workdir`、`coder_reference_mode=assets_only`
5. 交给 `onescience-coder`，由 coder 只消费 `coder_task_description.md` 与 OneScience 内部资产生成代码；`reproduction_spec.md` 只用于用户审计和上游追溯

**产出**：`coder_task_description.md`

## 最小角色链

规划阶段或用户尚未授权实现时：

```
当前角色: paper-reproducer
角色链: [research-lead, paper-reproducer]
交接物: paper_source, mode, framework, domain_route, output_dir(可选), workdir_rule=.paper2code_work/<arxiv_id-or-paper_key>, task_buckets overview
执行入口: onescience-paper-repro（未来）
当前下一跳: onescience-role（停留在角色层；仅记录未来执行入口）
```

用户已授权实现时：

```
当前角色: paper-reproducer
角色链: [research-lead, paper-reproducer]
交接物: paper_source, mode, framework, domain_route, output_dir(可选), paper_workdir=.paper2code_work/<arxiv_id-or-paper_key>, required_outputs=[reproduction_spec.md, coder_task_description.md], implementation_code_used=false
执行入口: onescience-paper-repro
当前下一跳: onescience-skill（由执行层继续路由到 onescience-paper-repro，再由其交接 onescience-coder）
```
