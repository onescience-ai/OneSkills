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
3. 选择模板和最小 Python 脚本集合，并确定用户输入、输出路径和脚本参数。
4. 从用户明确提供的项目目录创建或复用 `<project_dir>/app/`；复制选中的 `.py` 入口及其本地 Python 依赖闭包并保持相对结构，目标同名文件已存在时先比较内容，未经确认不得覆盖。
5. 静态分析复制后脚本的 import，把标准库、本地模块和第三方包分开，形成所需包及版本约束清单。
6. 在当前 Python 环境检查第三方包是否已安装、已安装版本是否满足约束，并以只读依赖解析检查安装或升级是否会破坏现有包约束。
7. 若依赖均已存在且兼容，跳过安装；若有已安装但版本冲突的依赖，报告包名、当前版本、要求版本和受影响包，等待用户选择环境隔离、调整版本或停止。
8. 若依赖缺失且解析无冲突，向用户说明待安装包、版本和目标环境并询问是否安装；得到明确同意后才可安装。若缺失依赖的安装会产生冲突，报告冲突和可选方案，由用户选择，禁止自动安装。
9. 依赖门禁通过后，coder 生成指向 `<project_dir>/app/` 内复制脚本的参数化命令或补全模板，并使用用户已确认的输入执行。若需要外部数据库、实验级 off-target、热力学折叠或设备执行，生成后续执行 handoff。

# constraints

- 不得在缺少序列/参考/物种时给最终候选。
- 不得省略 off-target、SNP/repeat、isoform、质粒拓扑等影响因素。
- 不得把轻量脚本输出解释为实验验证结论。

# next_phase_recommendation

需要联网检索时转入知识库类应用；需要执行脚本时交给运行层；需要实验记录时转入 protocol automation 或 ELN 模板。

# fallback

若输入不足，只生成请求模板和缺失字段清单；若目标超出轻量脚本能力，输出外部工具接入建议和 handoff。
