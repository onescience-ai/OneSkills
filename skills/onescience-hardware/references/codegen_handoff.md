# Codegen Handoff

本文件定义 `onescience-hardware -> onescience-coder` 的最小交接面。

目标是让 `onescience-coder` 不直接处理硬件探测逻辑，只消费一份稳定、精简的“代码生成交接摘要”。

如需查看与完整硬件画像配套的标准输出示例，可参考：

- `../assets/examples/slurm_dcu_output.json`
- `../assets/examples/slurm_gpu_output.json`
- `../assets/examples/slurm_cpu_output.json`

## 为什么需要这层抽象

`onescience-hardware` 负责识别：

- Host
- 平台类型
- 队列 / 分区
- module / conda 约束
- 路径约定

这些信息很多都属于“环境事实”，不应该让 `onescience-coder` 直接参与探测、判断和选择。

`onescience-coder` 真正关心的，是这些环境事实对代码实现有什么影响。

## 交接格式

建议把交接摘要整理成下面几类信息。

### 1. CPU 与主加速卡摘要

- `cpu_arch`: `x86_64` / `aarch64`
- `accelerator_kind`: `dcu` / `gpu` / `cpu`
- `accelerator_vendor`: `amd` / `nvidia` / `none`
- `accelerator_count_per_node`

这里的 `accelerator_kind` 用于概括“代码主要跑在什么设备上”，不是替代完整硬件画像中的 `cpu` 与 `accelerators[]`。

### 2. 运行与分布式模式

- `distributed_mode`: `single` / `multi_accelerator` / `multi_node`
- `runtime_mode`: `slurm` / `direct_remote`
- `launch_mode`: `python` / `torchrun` / `srun`
- `distributed_backend`: `rccl` / `nccl` / `gloo` / `none`

### 3. 代码必须适配的约束

- `needs_distributed_entry`
- `needs_device_guard`
- `needs_path_env`
- `needs_cluster_friendly_io`
- `needs_cpu_thread_tuning`
- `needs_numa_awareness`

这些字段回答的是“代码里要不要处理这件事”，而不是“远程环境怎么探测出来的”。

### 4. 运行期路径约定

- `dataset_dir`
- `models_dir`
- `work_dir`
- `device_visibility_env`

如果这些路径只在运行脚本里使用，也可以只传“是否依赖路径环境变量”，不必把全部远端细节塞给 `coder`。

### 5. 备注信息

- `notes_for_codegen`

例如：

- “入口脚本需要兼容 DCU 环境变量”
- “入口脚本需要兼容 CUDA_VISIBLE_DEVICES”
- “不要把数据集路径写死为本地绝对路径”
- “训练入口需保留分布式参数占位”
- “CPU dataloader 线程数不要硬编码”

## `onescience-coder` 应该怎么使用

`onescience-coder` 只需要做这几件事：

1. 读取交接摘要
2. 判断代码入口是否需要设备适配
3. 判断脚本是否需要分布式或环境变量占位
4. 在实现中保留与运行层兼容的接口

不要在 `coder` 中重新：

- 解析 SSH 配置
- 选择 Host
- 判断队列
- 探测 module / conda

## `onescience-hardware` 应该怎么输出

如果信息很多，优先输出对代码真正有影响的部分，而不是完整硬件清单。

推荐优先级：

1. CPU 架构
2. 主加速卡类型与厂商
3. 运行模式与启动模式
4. 是否分布式
5. 是否依赖环境变量路径
6. 入口脚本必须保留的适配点

## 示例

```yaml
codegen_handoff:
  cpu_arch: x86_64
  accelerator_kind: dcu
  accelerator_vendor: amd
  accelerator_count_per_node: 4
  distributed_mode: single
  runtime_mode: slurm
  launch_mode: python
  distributed_backend: rccl
  needs_distributed_entry: false
  needs_device_guard: true
  needs_path_env: true
  needs_cluster_friendly_io: true
  needs_cpu_thread_tuning: true
  needs_numa_awareness: false
  dataset_dir: /public/share/.../onedatasets
  models_dir: /public/share/.../onemodels
  work_dir: /home/user/project
  device_visibility_env: HIP_VISIBLE_DEVICES
  notes_for_codegen:
    - 不要写死本地数据路径
    - 入口脚本需兼容 DCU 环境
    - dataloader worker 数量不要硬编码
```
