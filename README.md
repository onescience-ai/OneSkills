# <div align="center">OneSkills</div>

OneSkills是面向AI4S的科研智能体技能库，聚焦科研开发、实验运行与环境交付等关键环节，提供可复用、可组合、可落地的任务执行能力。

## 支持Agent
**NOTE:** 拉取skills仓库

```bash 
git clone https://gitee.com/onescience-ai/oneskills.git
cd oneskills
```

| Agent |                                     使用方式                                      |                                                                                          备注                                                                                           |
| :--: |:-----------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|   Claude Code   |  python3 install/install_oneskills.py --agent claude --project /your/project  | 1. 若需同时安装运行资产，可增加 `--profile runtime` 参数。更多参数见 [install/README.md](install/README.md)。<br>2. 安装后会在 `/your/project` 文件夹中生成 `.claude` 隐藏文件夹，并将 OneSkills 相应技能与所需的其它文件按 Claude 能识别的方式存储。 |
|Codex|  python3 install/install_oneskills.py --agent codex --project /your/project   |                                                                                          同上                                                                                           |
|Trae|   python3 install/install_oneskills.py --agent trae --project /your/project   |                                                                                          同上                                                                                           |
|OpencCode| python3 install/install_oneskills.py --agent opencode --project /your/project |   同上      |

## 功能介绍

- **任务理解与编排**：通过 onescience-workflow 与 onescience-role 技能链，任务路由准确率达 **100%**，角色协作执行准确率达 **90%**，编排协调准确率达 **100%**
- **数据任务**：在数据集接入等场景中，结合 onescience-coder 技能，数据类任务代码生成通过率达 **70%**
- **模型任务**：模型接入、训练/推理脚本改造场景中，能够完成配置补全、脚本改造与实验准备，覆盖 FourCastNet、Pangu-Weather 等气象领域主流模型，模型类任务代码生成通过率达**87.5%**
- **论文复现任务**：气象、遥感等领域论文模型复现中，能够完成任务拆解、代码实现与验证，覆盖数据接入、模型改造与配置补全等关键环节
- **工程任务**：科研代码重构、项目结构整理场景中，能够完成代码生成、配置修复与入口脚本补齐
- **运行任务**：通过 onescience-runtime 与 onescience-installer 技能，能够完成远程环境识别、依赖安装、任务提交与故障诊断
- **评测任务**：能够完成实验验证路径梳理、测试方案选择与结果检查

## 使用场景

- 复现论文
  - "使用 OneScience 技能复现 https://arxiv.org/abs/2406.01465 论文"
- 接入一个新的数据集或 Earth DataPipe
  - "使用 OneScience 技能接入 OneScience 平台的 ERA5 数据集并生成对应的 Earth DataPipe"
- 改造或补全一个模型的训练、推理和配置文件
  - "使用 OneScience 实现任务：结合 FourCastNet 的全局感受野优势和 Pangu-Weather 的局地精细建模能力，构建一个混合天气预报模型"
- 在远程 GPU / DCU 环境安装并运行 OneScience
  - "使用 OneScience 技能在远程 DCU 环境安装运行依赖并启动训练任务"
- 提交科研任务到远端环境并排查运行失败原因
  - "使用 OneScience 技能把这个训练任务提交到远端 GPU 集群并诊断运行失败原因"
- 判断一个科研需求应该如何拆解、如何执行、如何验证
  - "使用 OneScience 技能帮我拆解这个科研需求并规划执行与验证路径"

## Contribution Notes

本仓库公开通用技能、公开参考资料与用户可用文档。

如果你想了解如何在本仓库里扩展自定义技能，优先阅读：

- `docs/open-source/custom_skill_contribution.md`

## Project Governance

- `LICENSE`
- `CONTRIBUTING.md`
- `SECURITY.md`
