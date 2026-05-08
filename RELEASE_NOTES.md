# Release Notes

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
