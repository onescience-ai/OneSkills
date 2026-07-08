# description

把核酸构件设计请求转为模板化约束、轻量筛选脚本、结构化结果表和实验验证 handoff。

# when_to_use

用于 primer/probe、CRISPR guide/editing、restriction cloning、plasmid verification、RNA secondary structure 或结构探针相关分子生物学设计任务。

# inputs

- 目标序列或 locus。
- 物种、参考版本或质粒拓扑。
- assay context、设计约束、筛选过滤器和验证策略。
- CRISPR 编辑窗口、PAM、donor/off-target 策略；或 RNA 结构约束；或克隆/质粒 feature 字段。
- 需要交付的表格、报告或模板。

# outputs

- 填写后的请求模板。
- 候选表和筛选 flag。
- 编辑、酶切、质粒或 RNA 结构交接字段。
- 验证计划和人工审核点。

# procedure

1. 根据任务标签判断 primer/probe、CRISPR、restriction cloning、plasmid verification 或 RNA structure 分支。
2. 对照本卡的输入字段、限制条件和模板入口。
3. 选择模板和轻量脚本。
4. coder 生成参数化命令或补全模板。
5. 若需要外部数据库、实验级 off-target、热力学折叠或设备执行，生成后续执行 handoff。

# constraints

- 不得在缺少序列/参考/物种时给最终候选。
- 不得省略 off-target、SNP/repeat、isoform、质粒拓扑等影响因素。
- 不得把轻量脚本输出解释为实验验证结论。

# next_phase_recommendation

需要联网检索时转入知识库类应用；需要执行脚本时交给运行层；需要实验记录时转入 protocol automation 或 ELN 模板。

# fallback

若输入不足，只生成请求模板和缺失字段清单；若目标超出轻量脚本能力，输出外部工具接入建议和 handoff。
