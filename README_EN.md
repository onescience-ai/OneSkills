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

Recommended installation methods for each agent:

|    Agent    |                           Usage                           |                             Notes                             |
| :---------: | :-------------------------------------------------------: | :----------------------------------------------------------: |
| **Claude Code** | `/plugin marketplace add https://github.com/onescience-ai/oneskills`<br>`/plugin install oneskills@oneskills` | Install via Claude Code plugin marketplace, then restart Claude Code |
|    **Codex**    | `npx codex-marketplace add https://github.com/onescience-ai/oneskills --skills`<br>`npx codex-marketplace remove --global --skill --yes onescience-cli` | Install skills via Codex marketplace, then remove onescience-cli to avoid conflicts |
|    **Trae**    | Install via OneScience Copilot VSIX package | Install from VSIX in Trae extension manager |
|  **OpenCode**  | Follow instructions in [.opencode/INSTALL.md](.opencode/INSTALL.md) | Check out and install from current repository |

## Capabilities

- **Task understanding and orchestration**: uses `onescience-orchestrator` as the main controller and coordinates `resource`, `expert`, and `executor` skills in layers to complete resource retrieval, intent recognition, expert planning, global plan merging, execution scheduling, and task status updates
- **Primitive resource retrieval**: supports retrieving models, components, data pipelines, application cards, workflow plans, and contract resources from natural-language requirements, covering domains such as bioinformatics, fluids, weather/climate, and materials chemistry
- **Data tasks**: supports data processing plan design, code generation for data tasks, dataset construction startup script generation, quality checks, and metadata generation, with a code generation pass rate for data tasks of **70%**
- **Model tasks**: covers mainstream weather-domain models such as FourCastNet and Pangu-Weather, with a model-task code generation pass rate of **87.5%**
- **Paper reproduction tasks**: supports paper information extraction, task decomposition, code implementation, and verification, covering key steps such as data access, model adaptation, and configuration completion
- **Engineering tasks**: supports code generation, configuration repair, entry script completion, and distributed training adaptation for scientific code refactoring and project structure cleanup
- **Runtime tasks**: supports remote environment identification, dependency installation, job submission, log synchronization, and failure diagnosis, as well as SCNet supercomputing platform job and file management
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
