# 本地运行站点工作流

用于创建本地运行配置。进入本工作流的前提是根目录不存在 `onescience.json`，且用户选择本地运行。

## 1. 第一问

若还没有问过，先问：

```text
你这次是本地运行还是远程运行？
```

用户选择“本地”后继续。不要询问 SSH 或 SCnet 字段。

## 2. 工作目录

读取 `assets/runsite_profiles/local.json`。若 `local.work_dir` 为空，询问：

```text
请提供本地工作目录；直接回车则使用当前项目目录。
```

当前项目目录可作为默认值。

## 3. Slurm

检测本地是否存在 Slurm：

```bash
python skills/onescience-runsite/scripts/runsite_config.py detect-local-slurm
```

若检测到 Slurm，询问：

```text
检测到本地有 Slurm，是否使用 Slurm 提交任务？
```

- 是：`execution_mode=slurm`，读取 `assets/cluster_profliles/slurm.json` 并补问空字段。补问时必须列出每个 Slurm 字段名、含义、默认值或是否可留空；不要只说“请提供 cluster 信息”。`gpu_type` 使用后续检测或用户确认的 `accelerator_kind`，用户直接回车时填入该值。
- 否：`execution_mode=null`，`runtime.cluster=null`。

无论是否使用 Slurm，`run_site=local` 且 `access_mode=""`。

本地 Slurm 一次性补问时必须列出：

```text
请按下面字段提供 Slurm 集群资源信息：
- partition：Slurm 分区名称，例如 gpu、compute、hpctest01；无默认值
- nodes：节点数量；直接回车使用 1
- gpus_per_node：每个节点需要的 GPU/DCU 数量；直接回车使用 1
- cpus_per_task：每个任务需要的 CPU 核心数；直接回车使用 8
- memory：内存大小，例如 64GB；直接回车使用 64GB
- time_limit：作业时间限制 HH:MM:SS；直接回车使用 02:00:00
- gpu_type：Slurm 加速器类型；直接回车使用后续检测或用户确认的 dcu/gpu
- ntasks_per_node：每节点任务数；直接回车使用 1
```

## 4. 硬件

```bash
python skills/onescience-runsite/scripts/runsite_config.py detect-hardware
```

检测本地运行平台的加速器类型。若输出 `hardware_detected=true` 且 `accelerator_kind` 为 `dcu` 或 `gpu`，后续 `generate` 必须传入对应的 `--accelerator-kind`。

若输出 `hardware_detected=false`，不要生成配置，必须询问用户：

```text
未能自动检测到本地运行平台加速器类型，请确认是 dcu 还是 gpu。
```

用户确认后，使用确认值作为 `--accelerator-kind`。脚本会从 `assets/hardware_profiles/{dcu|gpu}_hardware_profiles.json` 匹配 profile，并把 `software.modules` 写入 `onescience.json.runtime.modules`。不要手写 modules，除非用户明确覆盖。

## 5. 生成

本地直接运行：

```bash
python skills/onescience-runsite/scripts/runsite_config.py --config-path ./onescience.json generate \
  --run-site local \
  --execution-mode none \
  --accelerator-kind dcu
```

本地 Slurm：

```bash
python skills/onescience-runsite/scripts/runsite_config.py --config-path ./onescience.json generate \
  --run-site local \
  --execution-mode slurm \
  --accelerator-kind dcu \
  --cluster-data '{"partition":"hpctest01","nodes":1,"gpus_per_node":1,"cpus_per_task":8,"memory":"64GB","time_limit":"02:00:00","gpu_type":"dcu","ntasks_per_node":1}'
```

不要传 `--access-mode`；脚本会为本地配置写入空字符串。

生成完成后，按调用上下文回传：若由某个技能调用，交回该技能继续原任务；若没有明确调用方，交回 `onescience-orchestrator` 重新规划。
