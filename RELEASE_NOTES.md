# Release Notes

## 2026.06.05

本次发布主要为 OpenCode 安装体验增强：

- OpenCode 安装器默认会下载 OneScience 源码快照到项目 `.opencode/onescience/`，供代码阅读与实现类 skill 使用
- OpenCode 安装布局与默认发现路径对齐：skills 安装到 `.opencode/skills/`，并生成 `.opencode/opencode.jsonc.snippet` 供需要时合并配置
- 支持通过 `--namespace-root` 将 skills 安装到自定义目录（如 `vendor/oneskills/<version>/`）
- 在 `onescience-workflow`、`onescience-role`、`onescience-skill` 中补充 Catalog 协作说明：何时搜索 AI 原语、何时直接用已选原语、skill 发现优先级
- 新增 `references/catalog_integration.md`，统一说明 skill 与 AI 原语的发现与加载约定

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
