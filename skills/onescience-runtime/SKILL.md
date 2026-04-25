---
name: onescience-runtime
description: 在代码生成完成后，基于项目根目录的 `onescience.json` 与 `tpl.slurm` 创建远程连接、生成运行脚本，并将作业提交到目标远程环境运行。
---

# OneScience Runtime Skill

## 职责

在运行任务里：

1. 读取 `onescience-hardware` 提供的完整硬件画像
2. 读取项目根目录的 `onescience.json`
3. 读取项目根目录的 `tpl.slurm`
4. 基于配置生成运行脚本与提交脚本
5. 创建远程连接
6. 传输文件并提交作业到远程环境

如果需要进一步判断字段归属或层间交接，读取 `./references/runtime_contract.md`。
如果需要处理“远程环境未配置”或“远程信息不完整”的异常场景，读取 `../../references/remote_fallback.md`。

## 输入约定

- `onescience.json`：位于当前项目根目录
- `tpl.slurm`：位于当前项目根目录；本仓库内的标准模板资产位于 `./assets/tpl.slurm`，使用时应复制到用户工程根目录
- `runtime.script.code_path`：用户代码脚本路径
- `runtime.script.path`：生成后的 SLURM 脚本路径
- `onescience-hardware` 输出的完整硬件画像：Host、平台、队列、模块和环境约束

如果缺少 `onescience.json`、`tpl.slurm` 或可用的完整硬件画像，直接报告，不要擅自猜测。不要把给 `onescience-coder` 用的代码生成交接摘要误当成运行输入。

## 执行流程

1. 校验 `onescience.json`、`tpl.slurm`、`runtime.script.code_path` 是否存在。
2. 读取 `onescience-hardware` 提供的完整硬件画像中的 Host、平台、队列、模块和环境信息。
3. 从 `onescience.json` 提取集群、模块、conda、脚本和环境变量配置。
4. 结合模板与硬件画像生成运行脚本；仅使用 `tpl.slurm` 中已有变量做替换，不向模板外追加新段落。
5. 如有需要，确保作业脚本使用的日志目录存在。
6. 创建远程连接，并把提交脚本与用户代码脚本传到远端环境。
7. 在远端执行运行命令或 `sbatch` 提交命令。
8. 返回作业 ID、提交主机、脚本路径和后续查看日志的方法。

## 模板规则

- `tpl.slurm` 是固定模板
- 允许做变量替换，不允许改模板结构
- 变量优先来自 `onescience.json`
- 缺失变量时，优先报告配置问题，不要静默猜测

## 与硬件分层关系

- `onescience-hardware` 负责先感知目标硬件和远程环境
- `onescience-coder` 只消费代码生成交接摘要，不提供远程连接所需的完整环境事实
- `onescience-runtime` 负责在代码生成后真正创建连接、传输文件、运行脚本和提交作业
- 运行与提交发生在远端环境，本地不要求安装 `sbatch`

## 输出要求

至少给出：

1. 使用的配置文件路径
2. 选择的远程主机
3. 生成的提交脚本路径
4. 作业 ID 或提交失败原因
5. 日志查看方式

## 约束

- 不要引用 `.trae/skills/onescience.json` 之类的私有路径
- 不要自动修改用户的 `onescience.json`
- 不要跳过 `onescience-hardware` 已确认的硬件约束
- 不要把代码生成交接摘要误用为完整硬件画像
- 不要在代码尚不存在时直接提交空作业
- 当运行任务依赖远程事实但信息缺失时，返回阻断，不要假设默认 Host 或队列
