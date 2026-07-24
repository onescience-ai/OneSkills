# <div align="center">OneSkills</div>

> Development workspace working copy. The public release README is based on [`docs/open-source/public_repo_README.md`](docs/open-source/public_repo_README.md). When exported to `oneskills`, it overwrites the public repository root `README.md`.

<p align="center">
  A skills library for AI-native scientific research built around <strong>OneScience</strong>.
</p>

<p align="center">
Reusable skills for <strong>task orchestration</strong>, <strong>resource retrieval</strong>, <strong>expert planning</strong>, <strong>execution</strong>, and <strong>runtime delivery</strong>.
</p>

<p align="center">
  Works with <strong>Claude Code</strong>, <strong>Codex CLI</strong>, <strong>Trae</strong>, <strong>OpenCode</strong>, and other skill-based agents through optional integration adapters.
</p>

---

## What is OneSkills?

`OneSkills` is a research agent skill repository for AI4S (AI for Science) scenarios. The current architecture no longer centers on a fixed linear skill chain. Instead, it organizes research tasks as an extensible **AI Execution OS**:

- `onescience-orchestrator` maintains Task State, understands intent, merges plans, and dispatches execution.
- `type=resource` skills handle resource retrieval, providing knowledge of models, components, data pipelines, applications, workflow plans, and contracts.
- `type=expert` skills handle complex task planning, producing mergeable planner proposals.
- `type=executor` skills handle deterministic execution, returning artifacts, observations, and verification statuses.

Core repository directories:

- `skills/`: OneScience / OneSkills skill packages
- `docs/`: User guides, open-source release documentation, and contribution notes
- `evaluation/`: Skill, code generation, and routing evaluation assets
- `qa/`: Real-world agent evaluation, runtime assets, and quality check tools

Version information:

- Root `VERSION`: Current repository release version
- `skills/VERSION`: Skill package version
- `RELEASE_NOTES.md`: Release notes

## Architecture

The current primary entry point is `onescience-orchestrator`. When a user says "Use OneScience / OneSkills" and raises complex research tasks such as paper reproduction, data integration, model development, runtime verification, or remote installation, the orchestrator creates or updates a Task State and enters a loop of resource retrieval, expert planning, execution dispatch, and feedback.

```text
User Research Goal
  -> onescience-orchestrator
       -> type=resource: Recall resource summaries and planning knowledge
       -> type=expert: Generate domain-specific or task-specific planner proposals
       -> Global Plan: Merge plans, bind resources, select next step
       -> type=executor: Coding, paper reproduction, runtime, installation, analysis, inference, etc.
       -> Task State: Record artifacts / observations, drive next planning round or completion
```

![OneSkills Architecture](OneSkills_Architecture.png)

### Layer 1: Orchestrator

- Skill: `onescience-orchestrator`
- Responsibilities: Initialize project-level `onescience.json`, maintain Task State, invoke resource skills, recognize intent, recall experts, merge Global Plan, dispatch executors step by step
- Boundaries: Does not carry domain-specific knowledge; does not hardcode professional workflows such as paper reproduction, model training, bioinformatics analysis, or CFD simulation

### Layer 2: Resource

- Skill: `onescience-primitives`
- Responsibilities: Recall primitive resources from `skills/onescience-primitives/assets/`
- Coverage: `bio`, `cfd`, `climate`, `matchem`
- Common resources: models, components, datapipes, applications, workflow-planning, contracts
- Constraint: Callers may only consume `matched_resources[*].content` returned by the resource skill; they may not bypass the resource contract by directly reading assets

### Layer 3: Expert

- `onescience-research-workflow`: Research workflow planning expert, covering task families such as meteorology/climate, bioinformatics/proteins, materials/chemistry, and CFD/fluids
- `onescience-data-profile`: Data processing planning expert, producing data processing plans, data contracts, processing steps, and risk notes

Experts are responsible only for planning. They do not write code directly, submit jobs, or modify environments.

### Layer 4: Executor

The current execution skills are grouped into four categories:

**Coding & Reproduction**
- `onescience-coder`: Step-by-step coding, minimal smoke testing, or static requirement consistency checking
- `onescience-paper-repro`: Paper material acquisition, structured information extraction, reproduction specification and coding task description generation
- `onescience-dataset-builder`: Dataset build wrapper generation, dataset validation, quality checking, and metadata generation

**Runtime & Environment**
- `onescience-runsite`: Runtime site configuration parsing, validation, saving, and reuse; completing the runtime site configuration in `onescience.json`
- `onescience-runtime`: Unified runtime entry point, responsible for discover → preflight → execute → diagnose
- `onescience-installer`: Unified installation/repair entry point, responsible for discover → precheck → install → verify
- `onescience-cli`: Dispatching `onescience` commands in remote SSH / SLURM environments

**Model & Inference**
- `onescience-infer`: Scientific model inference workflow execution, covering HuggingFace / local checkpoints / project-native runners; supporting meteorology, bioinformatics, materials, fluids, and general research models
- `onescience-parallel`: Pipeline Parallel (PP) / Tensor Parallel (TP) adaptation of PyTorch models

**Platform & Analysis**
- `scnet-chat`: Natural language management of SCNet supercomputing platform jobs, files, accounts, regions, and queues
- `onescience-data-analyzer`: Data analysis, visualization, and report output; automatically matches visualization specifications by domain

## Runtime Model

`onescience-runtime` is the sole public runtime entry point. It accepts a script path or command, identifies the execution mode, completes pre-run checks, job submission, log synchronization, and basic diagnostics.

The runtime phases are fixed as:

```text
discover -> preflight -> execute -> diagnose
```

Supported execution modes:

- `local`: Direct execution in the current environment
- `local_slurm`: Current shell is already on a login node with direct SLURM access
- `remote_slurm`: Access a remote SLURM cluster via SSH
- `remote_direct`: Cloud platform direct connection scenarios, currently used primarily for SCNet routing

Stable runtime backends:

- `slurm_dcu`
- `slurm_gpu`
- `slurm_gpu_multinode_torchrun`
- `slurm_cpu`
- `local_direct_generic`

Stable runtime profiles:

- `remote_slurm_dcu`
- `remote_slurm_gpu`
- `remote_slurm_gpu_multinode_torchrun`
- `remote_slurm_cpu`
- `local_slurm_dcu`
- `local_slurm_gpu`
- `local_direct_python`
- `remote_direct_scnet_mcp`

Public remote channels:

- `ssh_slurm`: `remote_slurm + ssh`
- `scnet_mcp`: `remote_direct + cloud_api`; delegates to `scnet-chat` when SCNet job, file, account, region, queue, or cluster requirements are matched

## Installer Model

`onescience-installer` is the sole public installation/repair entry point. It is responsible for advancing the target environment to a state where it can be handed back to `onescience-runtime` for continued runtime verification.

The installation phases are fixed as:

```text
discover -> precheck -> install -> verify
```

Supported installation intents:

- Fresh install: Create or prepare a OneScience workspace and dependency environment
- Existing environment augmentation: Install domain-specific dependencies into an existing OneScience environment

Stable install profiles:

- `dcu_remote_install_profile`
- `gpu_remote_install_profile`
- `dcu_local_install_profile`
- `gpu_local_install_profile`

Successful installation does not guarantee successful runtime. Only after `verify` passes should the next step be handed to `onescience-runtime`.

## Supported Requests

Typical requests supported by the current architecture:

- "Use OneScience / OneSkills to help me plan this research task"
- "Help me reproduce this paper and generate follow-up coding tasks"
- "Access ERA5 / bioinformatics / materials / CFD data resources and generate processing pipelines"
- "Modify models, complete DataPipes, or implement components based on existing resources"
- "Generate dataset build scripts and validate dataset quality"
- "Install or repair OneScience in a remote GPU / DCU / CPU SLURM environment"
- "Submit this training / inference / data processing script to remote and sync logs"
- "Diagnose whether a run failure is an environment, submission, log, or business script issue"
- "Query jobs, submit tasks, download logs, or manage files in SCNet"
- "Adapt an existing PyTorch model to support PP / TP parallelism"
- "Configure a OneScience runtime site (local / remote SSH / SCNet), completing runtime environment information"

## Installation

### Claude Code

Install via the Claude Code plugin marketplace (recommended):

```text
/plugin marketplace add https://github.com/onescience-ai/oneskills
/plugin install oneskills@oneskills
```

For local development and debugging, clone the repository and use the repository root as the marketplace:

```bash
git clone https://github.com/onescience-ai/oneskills.git
```

```text
/plugin marketplace add ./oneskills
/plugin install oneskills@oneskills
```

### Codex

Install skills via the Codex marketplace (recommended):

```bash
npx codex-marketplace add https://github.com/onescience-ai/oneskills --skills
```

### OpenCode

Follow the instructions in [.opencode/INSTALL.md](.opencode/INSTALL.md) to check out and install from the current repository.

### Trae

Install via the OneScience Copilot VSIX plugin package. In the Trae extension manager, select "Install from VSIX" and choose `onescience-copilot-x.x.x.vsix`.

## Custom Skills

To extend custom skills, it is recommended to first read:

- [`docs/user-guides/extend_domain_experience.md`](docs/user-guides/extend_domain_experience.md)
- [`docs/open-source/custom_skill_contribution.md`](docs/open-source/custom_skill_contribution.md)

Recommended extension order:

1. Prioritize supplementing `onescience-primitives` resource assets so that existing orchestrator / expert / executor skills can recall them.
2. When a task requires complex planning and will be reused, add a new `type=expert` skill.
3. When a capability has stable inputs/outputs, can execute independently, and can return artifacts / observations, add a new `type=executor` skill.
4. Avoid hardcoding domain workflows into `onescience-orchestrator`.

## Optional Integrations

- `.claude-plugin/`: Claude Code plugin metadata and marketplace example
- `.codex-plugin/`: Codex marketplace plugin metadata
- `.opencode/INSTALL.md`: OpenCode installation instructions

When testing locally with Claude Code, add the repository root via `/plugin marketplace add ./oneskills`, not `./oneskills/.claude-plugin`. This ensures that `source: "./"` in the marketplace points to the repository root and installs the full `skills/` directory.

## Project Governance

- `LICENSE`
- `CONTRIBUTING_EN.md`
- `SECURITY_EN.md`
