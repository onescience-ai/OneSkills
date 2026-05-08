# Hardware Profile

本文件用于定义 `onescience-hardware` 输出的“完整硬件画像”结构，以及它与“代码生成交接摘要”的关系。

## 完整硬件画像

完整硬件画像主要给 `onescience-runtime` / `onescience-installer` 使用。它回答的是“远程环境事实是什么”，而不是“代码该怎么写”。

如需查看仓库内的标准输出示例，可参考：

- `../assets/examples/slurm_dcu_output.json`
- `../assets/examples/slurm_gpu_output.json`
- `../assets/examples/slurm_cpu_output.json`

完整硬件画像应能描述：

- CPU 架构、型号与拓扑
- 主加速卡类型、厂商与数量
- CPU 与加速卡的组合关系
- 运行所需的 module、conda、路径与调度约束
- 驱动栈与基础执行能力的 readiness

建议使用结构化块输出：

```yaml
hardware_profile:
  schema_version: v1
  host: login-kunshan
  scheduler_type: slurm
  platform_type: cluster
  partition: hpctest01

  cpu:
    arch: x86_64
    vendor: amd
    model: EPYC-xxx
    sockets: 2
    cores_per_socket: 32
    threads_per_core: 2
    numa_nodes: 4

  accelerators:
    - kind: dcu
      vendor: amd
      model: instinct-xxx
      count_per_node: 4
      memory_gb: 32
      interconnect: infinity-fabric
      visibility_env: HIP_VISIBLE_DEVICES
      distributed_backend: rccl

  memory:
    system_gb: 512

  storage:
    dataset_dir: /public/share/.../onedatasets
    models_dir: /public/share/.../onemodels
    work_dir: /home/user/project
    log_dir: /home/user/project/logs
    local_scratch_dir: /tmp

  software:
    modules:
      - sghpc-mpi-gcc/26.3
      - sghpcdas/25.6
    driver_stack:
      accelerator_runtime_family: rocm
      driver_version: "6.0"
      user_space_version: "25.6"
      delivery_mode: module
      driver_ready: true
      user_space_ready: true
      owner: platform_admin
      capability_readiness:
        compiler_ready: true
        torch_ready: true
        distributed_runtime_ready: true
        verification_commands:
          - hipcc --version
          - python -c 'import torch; print(torch.__version__)'
    conda_env: onescience311
    shell_init: source ~/.bashrc

  capabilities:
    supports_sbatch: true
    launch_mode: python
    supports_torchrun: false
    needs_rocm_env: true
    needs_cuda_env: false
```

### 必填字段

无论具体环境是什么，至少应输出：

- `schema_version`
- `host`
- `scheduler_type`
- `platform_type`
- `cpu.arch`
- `cpu.vendor`
- `partition` 或等价调度目标
- `storage.dataset_dir`
- `storage.models_dir`
- `storage.work_dir`
- `software.modules`
- `software.driver_stack.*`
- `software.conda_env`
- `capabilities.supports_sbatch`
- `capabilities.launch_mode`

### 加速卡字段

如果目标环境带加速卡，`accelerators` 至少应包含：

- `kind`: `dcu` / `gpu`
- `vendor`: `amd` / `nvidia`
- `count_per_node`
- `visibility_env`
- `distributed_backend`

如果目标环境是纯 CPU，使用：

```yaml
accelerators: []
```

不要伪造“虚拟 GPU/DCU”占位。

### 驱动与用户态 runtime 字段

`onescience-installer` 不应负责系统级驱动安装，但必须知道驱动栈是否已经就绪。因此完整硬件画像应显式提供：

- `software.driver_stack.accelerator_runtime_family`: `rocm` / `cuda` / `none`
- `software.driver_stack.driver_version`
- `software.driver_stack.user_space_version`
- `software.driver_stack.delivery_mode`: `module` / `system`
- `software.driver_stack.driver_ready`
- `software.driver_stack.user_space_ready`
- `software.driver_stack.owner`
- `software.driver_stack.capability_readiness.compiler_ready`
- `software.driver_stack.capability_readiness.torch_ready`
- `software.driver_stack.capability_readiness.distributed_runtime_ready`
- `software.driver_stack.capability_readiness.verification_commands`

这组字段的语义是：

- `hardware` 负责识别驱动栈事实
- `installer` 负责消费这些事实做 precheck
- 系统级驱动安装与内核模块管理不属于 `installer` 的职责

其中 `capability_readiness` 用于表达“驱动栈已就绪之后，平台是否还具备继续安装和验证所需的基础执行能力”。

### 为什么必须显式描述 CPU

真实远程环境经常是“CPU + accelerator”的组合，而不是单一 `device_type`。CPU 信息会直接影响：

- dataloader worker 数量
- `OMP_NUM_THREADS` 等线程设置
- NUMA / socket 亲和性
- 是否依赖某类指令集或编译环境
- 运行脚本中的资源申请方式

因此 CPU 不应只是 `runtime.cluster.cpus_per_task` 这样的附属字段，而应是完整硬件画像的一部分。

## 代码生成交接摘要

代码生成交接摘要只给 `onescience-coder` 使用。它回答的是“代码应该如何适配”。

核心原则：

- 完整硬件画像回答“远程环境事实是什么”
- 代码生成交接摘要回答“代码应该如何适配”

建议至少从完整硬件画像中提炼出：

- CPU 架构信息
- 主加速卡类型与厂商
- 分布式后端
- 启动模式
- 路径环境依赖

完整字段定义见 `./codegen_handoff.md`。

## 输出建议

至少给出：

1. 使用的 Host
2. 调度后端与平台类型
3. CPU 拓扑摘要
4. 加速卡拓扑摘要
5. 关键运行约束：队列、module、conda、路径、设备可见性变量
6. 对代码生成的影响
7. 对后续 `onescience-runtime` / `onescience-installer` 的影响

## 轻量探测建议

如有必要，可执行轻量只读探测，确认：

- 平台类型
- 队列或分区名称
- CPU 架构、厂商与 NUMA 信息
- 加速卡类型、厂商与数量
- module 与 conda 可用性
- 常用数据、模型和工作目录约定

优先使用低风险、只读命令，不要把上传文件、提交作业、运行脚本当作本 skill 的默认职责。
