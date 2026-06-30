# <div align="center">OneSkills</div>

<div align="center">

面向 AI4S 的科研智能体技能库

</div>

<div align="center">

![AI4S](https://img.shields.io/badge/AI4S-%E7%A7%91%E7%A0%94%E6%99%BA%E8%83%BD%E4%BD%93-2563eb)
![Claude Code](https://img.shields.io/badge/Claude%20Code-%E6%94%AF%E6%8C%81-0f766e)
![Codex](https://img.shields.io/badge/Codex-%E6%94%AF%E6%8C%81-0f766e)
![Trae](https://img.shields.io/badge/Trae-%E6%94%AF%E6%8C%81-0f766e)
![OpenCode](https://img.shields.io/badge/OpenCode-%E6%94%AF%E6%8C%81-0f766e)
![Runtime](https://img.shields.io/badge/Runtime-%E5%8F%AF%E9%80%89%E6%A1%A3%E4%BD%8D-f59e0b)
![License](https://img.shields.io/badge/License-Apache--2.0-16a34a)

</div>

<div align="center">

[安装 / Installation](../../install/README.md)

</div>

<div align="center">

[中文](./README.md) | [English](./README_EN.md)

</div>

---

OneSkills 是面向 AI4S 的科研智能体技能库，聚焦科研开发、实验运行与环境交付等关键环节，提供可复用、可组合、可落地的任务执行能力。

## 支持的智能体

**说明：需要先拉取 skills 仓库**

```bash 
git clone https://gitee.com/onescience-ai/oneskills.git
cd oneskills
```

|    Agent    |                           使用方式                           |                             备注                             |
| :---------: | :----------------------------------------------------------: | :----------------------------------------------------------: |
| **Claude Code** | python3 install/install_oneskills.py --agent claude --project /your/project | 1. 若需同时安装运行资产，可增加 `--profile runtime` 参数。更多参数见 [install/README.md](install/README.md)。<br>2. 安装后会在 `/your/project` 文件夹中生成 `.claude` 隐藏文件夹，并将 OneSkills 相应技能与所需的其它文件按 Claude 能识别的方式存储。 |
|    **Codex**    | python3 install/install_oneskills.py --agent codex --project /your/project | 1. 安装后会在 `/your/project` 文件夹中生成 `.Codex` 隐藏文件夹，并将 OneSkills 相应技能与所需的其它文件按 Codex 能识别的方式存储。 |
|    **Trae**    | python3 install/install_oneskills.py --agent trae --project /your/project | 1. 安装后会在 `/your/project` 文件夹中生成 `.trae` 隐藏文件夹，并将 OneSkills 相应技能与所需的其它文件按 Trae 能识别的方式存储。 |
|  **OpencCode**  | python3 install/install_oneskills.py --agent opencode --project /your/project | 1. 安装后会在 `/your/project` 文件夹中生成 `.opencode` 隐藏文件夹，并将 OneSkills 相应技能与所需的其它文件按 opencode 能识别的方式存储。 |

## 功能介绍

- **任务理解与编排**：任务路由准确率达 **100%**，角色协作执行准确率达 **90%**，编排协调准确率达 **100%**
- **数据任务**：数据类任务代码生成通过率达 **70%**
- **模型任务**：覆盖FourCastNet、Pangu-Weather等气象领域主流模型，模型类任务代码生成通过率达**87.5%**
- **论文复现任务**：能够完成任务拆解、代码实现与验证，覆盖数据接入、模型改造与配置补全等关键环节
- **工程任务**：科研代码重构、项目结构整理中，能够完成代码生成、配置修复与入口脚本补齐
- **运行任务**：能够完成远程环境识别、依赖安装、任务提交与故障诊断
- **评测任务**：能够完成实验验证路径梳理、测试方案选择与结果检查

## 使用场景

- 复现论文：`使用OneScience技能复现https://arxiv.org/abs/2406.01465论文`
- 接入数据集：`使用OneSkills技能接入OneScience平台的ERA5数据集并生成对应的Earth DataPipe`
- 改造或补全一个模型：`使用OneScience实现任务,结合FourCastNet的全局感受野优势和Pangu-Weather的局地精细建模能力，构建一个混合天气预报模型`
- 在远程 GPU / DCU 环境安装并运行OneScience：`使用OneScience技能在远程DCU环境安装运行依赖并启动训练任务`
- 提交科研任务到远端环境并排查运行失败原因：`使用OneScience技能把这个训练任务提交到远端GPU集群并诊断运行失败原因`
- 判断一个科研需求应该如何拆解、执行、验证：`使用OneScience技能帮我拆解这个科研需求并规划执行与验证路径`

## 贡献说明

本仓库公开通用技能、公开参考资料与用户可用文档。如果你想了解如何在本仓库中扩展自定义技能，优先阅读：[docs/open-source/custom_skill_contribution.md](custom_skill_contribution.md)

## 项目治理

- [LICENSE](../../LICENSE)
- [CONTRIBUTING.md](../../CONTRIBUTING.md)
- [SECURITY.md](../../SECURITY.md)
