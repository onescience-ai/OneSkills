# Release Notes

## 2026.07.08

本次发布版本主要围绕技能安装标准化与 OneScience 架构重构展开：

- 标准化 OneSkills 在 Claude Code、Codex、Trae、OpenCode 等智能体中的公开安装入口，统一在公开 README 中给出推荐安装方式与使用备注
- 补齐公开仓库首页的能力说明、典型使用场景、贡献入口与项目治理导航，提升 `docs/open-source/public_repo_README.md` 的可读性与用户上手体验
- 将科研任务入口明确为自然语言需求，覆盖论文复现、模型训练、数据分析、数据集构建、推理评估与工作流编排等场景
- 重构 OneScience 架构说明，形成 `onescience-orchestrator`、Resource Layer、Expert Layer、Executor Layer 的分层模型
- 明确 `Task State` 作为系统唯一事实源，串联意图理解、资源召回、专家规划、执行调度、结果观察与反馈再规划闭环
- 将 AI 原语资源与轻量规划知识统一沉淀到 Resource Layer，并约定 orchestrator、expert、executor 在不同阶段召回不同粒度的资源内容
- 明确新能力接入路径：可资源化为 AI 原语或 Planning Knowledge，也可封装为执行技能，或进一步专家化为领域规划技能
- 梳理能力演进路径，从隐式经验、资源化沉淀、反复验证，到技能化固化与内核无感扩展

## 2026.05.15

本次发布版本主要收紧 `onescience-workflow -> onescience-role -> onescience-skill` 的协作边界：

- 明确 `onescience-workflow` 负责输出 `domain_route`、`domain_task_family`、`stage_intent` 与 `planning_only`
- 明确 `onescience-role` 优先消费 workflow handoff，只继续细化角色链、领域任务桶、交接物和未来执行入口
- 明确 `onescience-skill` 优先消费 role 的 `execution_entry` 与 `handoff_artifacts`，不反向重做领域识别或角色判断
- 为 CFD benchmark、生信模型推理和材料 MACE 微调补充代表性 routing 用例
- 扩展 skill routing QA，开始校验领域路线、粗任务族、阶段意图和规划阶段语义
- 建立 `bio_domain` 边界契约与资产清单，并将 bio-inference 校验工具和公共模板迁到 runtime，将 single-cell、bio model、分子生物设计、population genetics、cell imaging、feature matrix、biomarker 与 ctDNA 等实现工具迁到 coder 资产
- 将 SimpleFold/ESM 离线环境准备脚本迁到 installer 资产，删除 role 子树下的 `scripts/` 执行副本，并由 QA 禁止 role 继续持有 scripts

## 2026.05.11

本次发布版本主要补齐 runtime / installer 的执行前确认与失败交接契约：

- 明确用户语义中的 Host、队列、区域、设备类型等只作为候选线索，必须通过 SSH/SLURM 或 SCnet MCP 实际通道确认后才能升级为环境事实
- 新增 runtime probe 契约，覆盖 `ssh_slurm` 与 `scnet_mcp` 的环境探测输入、输出、状态语义和安全边界
- 补充 SCnet MCP 队列可访问、服务不可用、远端路径不可写、已有任务日志未就绪等探测示例
- 补充 runtime phase 示例，覆盖 `sbatch` 提交失败、等待超时和语义环境线索待确认场景
- 补充 installer verify 失败示例，确保安装命令完成但验证失败时不会错误交回 runtime
- 补齐 SCnet DAS / torch 与 SSH/SLURM module 环境探测规则，避免把裸 `python3` 结果误判为目标软件环境不可用
- 收紧 DCU readiness 判定，要求实际确认 DTK 用户态 runtime 或封装 DTK 的 `sghpc` 环境
- 明确 runtime 只负责 readiness confirmation，installer 负责环境安装、修复和 verify
- 同步 QA 校验，持续约束 probe 示例、phase handoff 和公开导出边界

## 2026.05.07

本次发布版本主要完成了以下整理：

- 将安装目标统一收敛到 `.<agent>/oneskills/...` 私有目录，减少不同技能包之间的目录冲突风险
- 同步 installer 清单、安装说明与 QA 校验，确保 `skills / references / integrations` 的安装路径一致
- 将安装入口补充为 `profile` 语义，区分默认基础安装与面向实际运行的 runtime 安装
- 为 `codex` 默认补齐用户级 bridge，使一键安装后即可被当前 Codex 发现
- 为后续处理 Trae 对相对路径解析差异的问题，先补齐本轮可测试的公开发布版本

## 2026.05.06

本次发布版本主要完成了以下整理：

- 将运行阶段统一收敛为 `onescience-runtime` 单一公开入口
- 将 SCnet 能力并入 `execution_channel=scnet_mcp` 通道，并补齐对应示例与 QA 校验
- 补强 `ssh_slurm` 运行契约、结果样例与主机确认场景覆盖
- 修复安装器对共享 `references/` 的正式安装流程，并保留旧运行 skill 残留清理
- 梳理公开发布导出规则、QA 目录说明与维护文档导航

## 2026.04.29

本次发布版本主要完成了以下整理：

- 梳理 `workflow -> role -> skill -> execution skills` 主链
- 明确 `hardware / runtime / installer / debug` 的共享远程执行契约
- 重构 installer 资产分层，拆分 backend、workspace bootstrap、domain、request、resolution
- 收敛公开文档边界，提升技能说明与参考文档的一致性
- 新增统一文档分层规范，减少公开文档与维护文档混写
- 补齐相关 QA 说明与校验脚本

用户如果拿到的是发布版本 skills，优先查看：

- 仓库根目录 `VERSION`
- 已安装 skills 目录下的 `VERSION`
