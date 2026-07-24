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

[中文](./public_repo_README.md) | [English](./public_repo_README_EN.md)

</div>

---

OneSkills 是面向 AI4S 的科研智能体技能库，聚焦科研开发、实验运行与环境交付等关键环节，提供可复用、可组合、可落地的任务执行能力。

## 功能介绍

| 能力 | 说明 |
| :--- | :--- |
| **任务检索** | 以 `onescience-orchestrator` 为主控，按 resource → expert → executor 三层技能协作，完成科研任务的意图识别、规划融合与执行调度 |
| **资源检索** | 按自然语言需求检索模型、组件、数据管线、工作流规划等科研原语资源，覆盖气象/气候、生信、材料化学、流体力学四个领域 |
| **论文复现与编码** | 从论文 PDF/arXiv 链接提取结构化信息，生成复现规格与编码任务，覆盖数据接入、模型改造、配置补全等环节 |
| **数据处理与构建** | 支持数据处理方案规划、代码生成、数据集构建脚本生成与质量验证 |
| **模型推理与训练** | 支持科学模型推理工作流（HuggingFace / 本地 checkpoint）与训练脚本生成（含 PP/TP 分布式并行改造） |
| **运行与环境** | 远程环境识别、依赖安装、SLURM 作业提交、日志同步与故障诊断，支持 SCNet 超算平台作业和文件管理 |

---

## 安装

根据使用的 Agent 环境选择对应方式：

| Agent | 使用方式 | 备注 | 详细指南 |
| :---: | :--- | :--- | :--- |
| **Claude Code** | `/plugin marketplace add https://github.com/onescience-ai/oneskills`<br>`/plugin install oneskills@oneskills` | 添加 OneSkills marketplace 后安装 `oneskills@oneskills` 插件 | [安装说明](claude_code_install.md) |
| **Codex** | `npx codex-marketplace add https://github.com/onescience-ai/oneskills --skills` | 通过 Codex marketplace 从 OneSkills 仓库安装 skills | [安装说明](codex_install.md) |
| **Trae** | 在"扩展"面板的"更多"菜单中选择"从 VSIX 安装" | 从 https://gitee.com/onescience-ai/onescience-vscode-plugin/releases/tag/latest 下载 `onescience-copilot*.vsix` 后导入安装 | [安装说明](trae_install.md) |
| **OpenCode** | 将以下提示词粘贴到 OpenCode 中执行：<br>`请获取并按照 https://github.com/onescience-ai/oneskills/blob/master/.opencode/INSTALL.md 中的说明，从当前仓库检出为 OpenCode 安装 OneSkills` | OpenCode 会按安装说明从当前仓库检出安装 | [安装说明](opencode_install.md) |

---

## 使用指南

### 使用方式

安装完成后，在 Agent 对话中输入：

```
使用 onescience 技能 + 任务描述
```

例如：

```
使用 onescience 技能，基于已有天气模型新增一个降水预测模块
```

Agent 将自动调用 OneSkills 技能链完成任务的编排与执行。

### 使用示例

#### 任务描述建议

为提升任务执行效果，建议在提示词中明确以下信息：

* **目标**：需要完成的具体任务
* **来源**：论文、代码仓库、数据集等参考信息
* **产出**：代码位置、结果格式
* **运行要求**：是否需要测试、训练或提交任务

示例：

```
使用onescience技能，基于experiments/weather/项目中的模型代码，补充完整的训练脚本，保存到scripts/train.py，生成后在本机运行一次验证。
```

#### 论文复现

```
使用onescience技能，复现 https://arxiv.org/abs/2406.01465 论文，将代码生成到 experiments/paper_fourcastnet/ 目录下，完成后在本地运行一次验证。
```

#### 数据接入

```
使用onescience技能，接入ERA5再分析数据集的温度和湿度变量，生成Earth DataPipe数据管线，输出到 data_pipelines/era5/ 目录下。
```

#### 模型开发

```
使用onescience技能，结合FourCastNet的全局感受野优势和Pangu-Weather的局地精细建模能力，构建一个混合天气预报模型。
```

#### 模型训练

```
使用onescience技能，基于 experiments/baseline/ 中的模型代码，补充完整的训练脚本，配置分布式训练策略，保存到 scripts/train.py，通过 Slurm 提交到远程 GPU 集群启动训练。
```

#### 环境安装与运行

```
使用onescience技能，在远程DCU环境安装运行依赖并启动训练任务。
```

#### 任务提交与诊断

```
使用onescience技能，将当前项目的训练任务提交到远端 GPU 集群，若运行失败则分析 slurm_job.log 中的错误原因，将诊断报告保存到 reports/diagnosis.md。
```

#### 需求拆解与验证规划

```
使用onescience技能，针对"基于ERA5数据训练一个区域降水预测模型"这一需求，拆解出数据准备、模型实现、训练运行、效果评估四个阶段，并给出每个阶段的验证指标。
```

---

## 支持的运行环境

OneSkills 支持多种运行方式，详细配置请参考：[运行环境配置](runtime_configuration.md)

---

## 自定义技能

如果你想为 OneSkills 扩展新的科研技能，请参考：[自定义技能开发指南](custom_skill_contribution.md)

---

## 项目治理
- [LICENSE](../../LICENSE)
- [贡献指南](../../CONTRIBUTING.md) 
- [安全策略](../../SECURITY.md) 
