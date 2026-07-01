# <div align="center">OneSkills</div>

<div align="center">

AI4S-oriented skill library for research agents

</div>

<div align="center">

![AI4S](https://img.shields.io/badge/AI4S-Scientific%20Agents-2563eb)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Supported-0f766e)
![Codex](https://img.shields.io/badge/Codex-Supported-0f766e)
![Trae](https://img.shields.io/badge/Trae-Supported-0f766e)
![OpenCode](https://img.shields.io/badge/OpenCode-Supported-0f766e)
![Runtime](https://img.shields.io/badge/Runtime-Profile%20Available-f59e0b)
![License](https://img.shields.io/badge/License-Apache--2.0-16a34a)

</div>

<div align="center">

[Installation](./install/README.md)

</div>

<div align="center">

[中文](./README.md) | [English](./README_EN.md)

</div>

---

OneSkills is an AI4S-oriented skill library for research agents. It focuses on scientific development, experiment execution, and environment delivery, and provides reusable, composable, and production-oriented task capabilities.

## Supported Agents

**NOTE: You need to clone the skills repository first.**

```bash 
git clone https://gitee.com/onescience-ai/oneskills.git
cd oneskills
```

|    Agent    |                           Usage                           |                             Notes                             |
| :---------: | :-------------------------------------------------------: | :----------------------------------------------------------: |
| **Claude Code** | python3 install/install_oneskills.py --agent claude --project /your/project | 1. To install runtime assets as well, add the `--profile runtime` flag. See [install/README.md](install/README.md) for more options.<br>2. After installation, a hidden `.claude` directory will be created under `/your/project`, and the corresponding OneSkills files will be stored in a layout recognized by Claude. |
|    **Codex**    | python3 install/install_oneskills.py --agent codex --project /your/project | 1. After installation, a hidden `.Codex` directory will be created under `/your/project`, and the corresponding OneSkills files will be stored in a layout recognized by Codex. |
|    **Trae**    | python3 install/install_oneskills.py --agent trae --project /your/project | 1. After installation, a hidden `.trae` directory will be created under `/your/project`, and the corresponding OneSkills files will be stored in a layout recognized by Trae. |
|  **OpencCode**  | python3 install/install_oneskills.py --agent opencode --project /your/project | 1. After installation, a hidden `.opencode` directory will be created under `/your/project`, and the corresponding OneSkills files will be stored in a layout recognized by opencode. |

## Capabilities

- **Task understanding and orchestration**: task routing accuracy reaches **100%**, role-based collaborative execution reaches **90%**, and orchestration coordination reaches **100%**
- **Data tasks**: code generation pass rate for data-oriented tasks reaches **70%**
- **Model tasks**: covers major weather-domain models such as FourCastNet and Pangu-Weather, with a model-task code generation pass rate of **87.5%**
- **Paper reproduction tasks**: supports task decomposition, code implementation, and verification, covering data access, model adaptation, and configuration completion
- **Engineering tasks**: supports scientific code refactoring, project structure cleanup, configuration repair, and entry script completion
- **Runtime tasks**: supports remote environment inspection, dependency installation, job submission, and failure diagnosis
- **Evaluation tasks**: supports experiment verification path planning, test strategy selection, and result inspection

## Use Cases

- Reproducing a paper: `Use OneScience skills to reproduce the paper at https://arxiv.org/abs/2406.01465`
- Integrating a dataset: `Use OneSkills skills to integrate the ERA5 dataset from the OneScience platform and generate the corresponding Earth DataPipe`
- Extending or completing a model: `Use OneScience to implement a task by combining FourCastNet's global receptive field advantages with Pangu-Weather's local fine-grained modeling capability to build a hybrid weather forecasting model`
- Installing and running OneScience in a remote GPU / DCU environment: `Use OneScience skills to install runtime dependencies and launch a training job in a remote DCU environment`
- Submitting a scientific task to a remote environment and diagnosing why it failed: `Use OneScience skills to submit this training task to a remote GPU cluster and diagnose why it failed`
- Determining how to decompose, execute, and validate a scientific requirement: `Use OneScience skills to help me break down this research requirement and plan the execution and validation path`

## Contribution Notes

This repository exposes general-purpose skills, public references, and user-facing documents. If you want to learn how to extend custom skills in this repository, start with [docs/open-source/custom_skill_contribution.md](custom_skill_contribution.md)

## Project Governance

- [LICENSE](../../LICENSE)
- [CONTRIBUTING.md](../../CONTRIBUTING.md)
- [SECURITY.md](../../SECURITY.md)
