# 审计工作流

## 目标

对 `reproduction_spec.md` 执行跨领域通用审计。审计不是只列问题，而是把论文解析和结构化信息提取结果重新对照论文内容校验；发现错误、遗漏、混淆或证据不足时，必须修复 `reproduction_spec.md`，再重新审计，直到 spec 中的内容与论文证据一致，或明确留下 `MISSING:` / `ASSUMPTION:`。

审计工作流根据 `paper_content_summary.md` 召回 `../assets/domain_knowledge/` 下的领域知识。领域知识只提供检查清单，不提供论文事实。

## 审计输入

- `paper_text.md`
- `paper_text_full.md`（如存在）
- `figures_tables.md`
- `paper_sections/`（如存在）
- 附录和补充材料文本
- `paper_content_summary.md`
- 待审计的 `reproduction_spec.md`
- 按摘要召回的领域知识文件

## 迭代修复循环

1. 从 `reproduction_spec.md` 抽取所有关键声明，包括任务、数据、变量、shape、模型、损失、训练、推理、评估、配置、领域专属细节和假设。
2. 对每条声明回查论文证据位置；证据缺失则修复为 `MISSING:` / `ASSUMPTION:` 或删除确定表述。
3. 对照 `paper_text.md`、表格、图注、算法框、附录和补充材料查找遗漏信息；发现遗漏则补入 spec。
4. 使用召回的领域知识作为检查清单，确认该领域常见关键字段是否已被论文证据覆盖、标缺或假设。
5. 修复 spec 后重新执行审计；直到没有已知错误、矛盾或未标注假设。
6. 在 `## 14. 审计结论` 中记录每轮发现的问题、修复内容、仍需确认项和机械校验结果。

如果修复需要用户材料或论文中不存在的信息，停止编造，保留 `MISSING:` 并说明需要补充的最小材料。

## Spec 正确性完成条件

只有同时满足以下条件，`reproduction_spec.md` 才算正确：

- 所有确定性描述都有论文正文、表格、图注、公式、算法框、附录、补充材料或用户材料证据。
- 论文中与复现相关的任务、数据、处理、模型、损失、训练、推理、评估、配置、领域专属信息没有已知遗漏。
- 数值、变量、shape、horizon、指标、超参和组件描述不存在自相矛盾。
- 论文未说明但实现必须选择的内容均标为 `MISSING:` 或 `ASSUMPTION:`。
- 已运行适用的机械校验脚本，并把结果写入审计结论。
- 若存在无法解决的冲突，已记录冲突证据、保守选择和需要用户确认的最小问题。

## 通用审计项

### 1. 证据与事实边界

- 每个关键实现要求必须有论文或用户材料证据。
- 推断项保留 `INFERRED:`。
- 实现假设保留 `ASSUMPTION:`。
- 缺失但会影响实现的项保留 `MISSING:`。
- 不得把论文未说明的公式、数据格式、目录结构、代码结构、训练技巧写成事实。

### 2. 数量与通道一致性

- 涉及变量数、字段数、通道数、类别数、层数、token 数、原子/残基数、节点/边数时，必须建立结构化 ledger。
- 能机械校验的变量/通道计数必须写入 `variable_channel_ledger.json`，并运行：

```text
python skills/onescience-paper-repro/scripts/variable_channel_audit.py <paper_workdir>/variable_channel_ledger.json
```

- 脚本失败时不得交接给 coder；先修正 ledger/spec，或把冲突写成明确缺口。
- 不得混用“对象数量”和“展开后的 scalar channel 数量”。

### 3. Shape 与维度流闭合

- shape ledger 必须逐步说明 batch、time/history、space/node/token、level、channel、feature 等维度含义。
- 每个模块输入 shape 必须能从上一个模块输出 shape 推导。
- reshape、flatten、unflatten、scatter/gather、interpolation、pooling、patch/token 化、graph message passing 等操作必须说明维度变化。
- 多时间步、多模态或多分辨率输入必须说明融合方式。

### 4. 结构语义与伪实现一致性

- 如果写模块顺序、伪代码或 block 结构，必须和论文结构声明一致。
- normalization、residual、attention/message passing/MLP、gating、edge/node update 的相对顺序必须明确。
- 论文未给内部顺序时，不能生成看似确定的伪代码；只能写 `MISSING:` 或 `ASSUMPTION:`。

### 5. 阶段语义边界

- 训练配置、训练目标、推理能力、评估协议、结果展示范围必须分开记录。
- 训练阶段的 rollout/horizon/augmentation/teacher forcing 约束不能自动套到推理或评估阶段。
- 推理和评估的 horizon、case 范围、输出频率、保存格式必须由论文证据或明确假设支撑。

### 6. 目标与损失一致性

- 区分模型预测量、训练 loss target、rollout 更新量和评估 target。
- 如果论文说明使用 state、delta、residual、tendency、noise、score、class label 或其它 target，必须原样进入 spec。
- 如果未说明，标记 `MISSING:`，不得默认。

### 7. 评估完整性

- 主文、表格、图、附录、限制章节和领域评估段落都要检查。
- 不得只摘主结果表；用于说明能力边界、失败模式或业务价值的指标也要进入评估协议或缺口。
- 领域资产可提示常见指标类型，但只有论文出现的指标才能写成确定要求。

### 8. 实现假设审计

- 文件格式、存储后端、loader、batch 组织、默认超参、近似公式、缺失数据处理等，如果论文未指定，必须写入 `ASSUMPTION:`。
- 假设应说明理由、可替换选项和代码中应如何暴露配置。

## 领域知识召回规则

1. 读取 `paper_content_summary.md`，提取领域候选、任务关键词、数据对象、模型关键词和评估关键词。
2. 读取 `../assets/domain_knowledge/` 下各领域文件顶部的摘要表头，选择相关领域文件；可以选择多个，也可以在领域不清时不选择。
3. 读取被召回的领域文件全文，并将其作为审计检查清单。
4. 将领域知识逐项映射到论文证据：有证据则补入或校正 spec；无证据但实现需要选择则写 `MISSING:` / `ASSUMPTION:`；无关项忽略。
5. 不得因为领域知识中列出某个指标、变量、数据格式或建模习惯，就把它写成论文确定要求。

## 审计输出

在 `reproduction_spec.md` 的 `## 14. 审计结论` 中写入：

- 已通过的审计项。
- 发现并已修正的冲突。
- 仍需假设或用户确认的缺口。
- 已运行的机械校验脚本和结果。
- `coder_task_description.md` 必须覆盖的高风险条目。

如果审计发现阻塞项，停止交接，要求补充材料或明确假设。
