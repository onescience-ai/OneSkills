# OneScience Runsite 技能优化方案

## Agent 阅读指引

在以下情况读取本文件:

- 需要理解 `onescience.json` 为什么必须按 `runsite.example.json` 生成。
- 需要确认每个字段来自用户输入、profile、硬件检测还是动态计算。
- 需要实现或调整 `scripts/runsite_config.py generate`。
- 需要设计验证用例或排查配置生成结果不符合预期的问题。

阅读顺序:

1. 先看"字段来源映射表"。
2. 再看"配置生成流程重构"。
3. 实现脚本时读取 "Profile 匹配规则"、"Mode 和 Backend ID 确定规则"、"Profile Ref 确定规则"。
4. 验证时读取"配置示例"和"测试计划"。

## 目录

- [1. 问题分析](#1-问题分析)
- [2. 优化方案](#2-优化方案)
- [3. 实施步骤](#3-实施步骤)
- [4. 配置示例](#4-配置示例)
- [5. 关键约束](#5-关键约束)
- [6. 测试计划](#6-测试计划)
- [7. 后续改进](#7-后续改进)

## 1. 问题分析

### 1.1 当前问题

当前生成的 `onescience.json` 格式与 `runsite.example.json` 不匹配，主要问题：

1. **生成逻辑过于简单**：`runsite_config.py` 的 `cmd_generate` 函数直接复制模板，未根据实际情况动态填充
2. **配置模板不完整**：`runsite_profiles/*.json` 仅包含最少字段，缺少完整结构
3. **缺少字段映射逻辑**：
   - `run_site` 字段应来自 `runsite_profiles` 模板
   - `cluster` 字段应来自 `cluster_profiles` 模板
   - `env_vars` 字段应来自 `env_vars/config.json`
   - `target` 和 `environment` 字段应来自 `hardware_profiles` 匹配
   - `mode`、`backend_id`、`runtime_profile_ref`、`install_profile_ref` 应根据运行方式和硬件类型动态确定

### 1.2 期望行为

生成的 `onescience.json` 应该：

1. **顶层字段固定**：`runtime` 对象包含固定的子字段结构
2. **`mode` 和 `backend_id` 动态确定**：根据执行通道和硬件类型
   - `mode`: `"local"` | `"slurm"` | `"direct"`
   - `backend_id`: `"local_dcu"` | `"local_gpu"` | `"slurm_dcu"` | `"slurm_gpu"` 等
3. **`run_site` 字段匹配模板**：从 `runsite_profiles` 中的模板获取字段
4. **`cluster` 字段匹配模板**：从 `cluster_profiles/slurm.json` 获取，并填充用户提供的值
5. **`env_vars` 字段来自配置**：从 `env_vars/config.json` 读取
6. **硬件相关字段来自匹配**：
   - 根据硬件检测结果（DCU/GPU/CPU）
   - 匹配 `hardware_profiles/dcu_hardware_profiles.json` 或 `gpu_hardware_profiles.json`
   - 提取 `cpu.vendor`、`accelerators[0].vendor` 等字段
7. **运行时引用字段来自 runtime 定义**：
   - `scheduler_type`: 从 hardware_profile 中的 `scheduler_type` 获取
   - `platform_type`: 从 hardware_profile 中的 `platform_type` 获取
   - `runtime_profile_ref`: 根据执行模式和硬件类型组合（如 `remote_slurm_dcu`）
   - `install_profile_ref`: 根据硬件类型和接入方式组合（如 `dcu_remote_install_profile`）

## 2. 优化方案

### 2.1 配置生成流程重构

**新的生成流程**：

```
用户输入
  ↓
确定执行通道 (execution_channel)
  ↓
检测硬件类型 (hardware_detection)
  ↓
匹配 hardware_profile
  ↓
加载配置模板
  ├─ runsite_profile (run_site字段)
  ├─ cluster_profile (cluster字段，如使用Slurm)
  ├─ env_vars/config.json (env_vars字段)
  └─ hardware_profile (target/environment/resources字段)
  ↓
确定 mode 和 backend_id
  ↓
确定 runtime_profile_ref 和 install_profile_ref
  ↓
组装最终配置
  ↓
保存到 onescience.json
```

### 2.2 字段来源映射表

| 字段路径 | 来源 | 说明 |
|---------|------|------|
| `runtime.mode` | 动态计算 | 根据 execution_channel 确定：`local_direct`→`local`, `local_slurm`→`slurm`, `ssh_slurm`→`slurm` |
| `runtime.backend_id` | 动态计算 | 格式：`{mode}_{hardware}`，如 `slurm_dcu`, `local_gpu` |
| `runtime.execution_profile.execution_mode` | CHANNELS映射 | 从 `runsite_config.py` 的 CHANNELS 获取 |
| `runtime.execution_profile.access_mode` | CHANNELS映射 | 从 `runsite_config.py` 的 CHANNELS 获取 |
| `runtime.execution_profile.runtime_profile_ref` | 动态计算 | 格式：`{execution_mode}_{hardware}`，如 `remote_slurm_dcu` |
| `runtime.execution_profile.install_profile_ref` | 动态计算 | 格式：`{hardware}_{access_mode}_install_profile`，如 `dcu_remote_install_profile` |
| `runtime.run_site.*` | runsite_profiles模板 | 完全来自匹配的 runsite_profile 模板 |
| `runtime.target.scheduler_type` | hardware_profile | 从匹配的 hardware_profile 中的 `scheduler_type` 获取 |
| `runtime.target.platform_type` | hardware_profile | 从匹配的 hardware_profile 中的 `platform_type` 获取 |
| `runtime.target.cpu_arch` | 硬件检测 | 从 `detect_hardware()` 获取 |
| `runtime.target.cpu_vendor` | hardware_profile | 从匹配的 hardware_profile 的 `cpu.vendor` 获取 |
| `runtime.target.accelerator_kind` | 硬件检测 | 从 `detect_hardware()` 获取 |
| `runtime.target.accelerator_vendor` | 硬件检测 | 从 `detect_hardware()` 获取 |
| `runtime.target.node_scope` | 用户输入/默认 | Slurm nodes>1 时为 `multi_node`，否则 `single_node` |
| `runtime.environment.cpu.*` | hardware_profile | 从 hardware_profile 的 `cpu` 对象获取 |
| `runtime.environment.accelerator_defaults.*` | hardware_profile | 从 hardware_profile 的 `accelerators[0]` 获取并转换 |
| `runtime.cluster.*` | cluster_profile + 用户输入 | 模板来自 cluster_profiles/slurm.json，值来自用户输入 |
| `runtime.modules` | 用户输入/hardware_profile | 优先用户输入，回退到 hardware_profile 的 `software.modules` |
| `runtime.resources.*` | hardware_profile + 计算 | 从 hardware_profile 提取或根据 cluster 配置计算 |
| `runtime.env_vars.*` | env_vars/config.json | 完全来自 env_vars/config.json |

### 2.3 硬件 Profile 匹配规则

**匹配逻辑**：

```python
def match_hardware_profile(hardware_type: dict, use_slurm: bool, node_count: int) -> dict:
    """
    根据硬件类型和配置匹配 hardware_profile

    Args:
        hardware_type: detect_hardware() 返回的结果
        use_slurm: 是否使用 Slurm
        node_count: 节点数量

    Returns:
        匹配的 hardware_profile
    """
    accelerator_kind = hardware_type["accelerator_kind"]

    # 确定文件路径
    if accelerator_kind == "dcu":
        profile_file = "hardware_profiles/dcu_hardware_profiles.json"
    elif accelerator_kind == "gpu":
        profile_file = "hardware_profiles/gpu_hardware_profiles.json"
    else:
        # CPU 场景暂不支持 hardware_profile
        return None

    # 加载 profiles
    profiles = load_json(profile_file)["profiles"]

    # 匹配规则
    for profile in profiles:
        # 必须支持 Slurm（如果需要）
        if use_slurm and not profile.get("capabilities", {}).get("supports_sbatch"):
            continue

        # 匹配节点范围
        default_scope = profile.get("capabilities", {}).get("default_node_scope", "single_node")
        if node_count > 1 and default_scope != "multi_node":
            continue
        if node_count == 1 and default_scope == "multi_node":
            # 允许 multi_node profile 用于 single_node，但优先 single_node profile
            pass

        # 找到匹配
        return profile

    # 如果没有精确匹配，返回第一个 profile 作为默认
    return profiles[0] if profiles else None
```

### 2.4 Mode 和 Backend ID 确定规则

```python
def determine_mode_and_backend(execution_channel: str, hardware_kind: str) -> tuple[str, str]:
    """
    根据执行通道和硬件类型确定 mode 和 backend_id

    Returns:
        (mode, backend_id)
    """
    # 确定 mode
    if execution_channel in ["local_direct"]:
        mode = "local"
    elif execution_channel in ["local_slurm", "ssh_slurm", "scnet_slurm"]:
        mode = "slurm"
    elif execution_channel in ["ssh_direct", "scnet_direct"]:
        mode = "direct"
    else:
        mode = "local"  # 默认

    # 确定 backend_id
    backend_id = f"{mode}_{hardware_kind}"

    return mode, backend_id
```

### 2.5 Runtime Profile Ref 确定规则

```python
def determine_runtime_profile_ref(execution_mode: str, hardware_kind: str) -> str:
    """
    根据执行模式和硬件类型确定 runtime_profile_ref

    格式：{execution_mode}_{hardware_kind}
    """
    # execution_mode: local, local_slurm, remote_slurm, remote_direct, remote
    # hardware_kind: dcu, gpu, cpu

    return f"{execution_mode}_{hardware_kind}"
```

### 2.6 Install Profile Ref 确定规则

```python
def determine_install_profile_ref(hardware_kind: str, access_mode: str) -> str:
    """
    根据硬件类型和接入方式确定 install_profile_ref

    格式：{hardware_kind}_{access_location}_install_profile
    其中 access_location 由 access_mode 推导：
    - local → local
    - ssh/scnet → remote
    """
    if access_mode == "local":
        location = "local"
    else:
        location = "remote"

    return f"{hardware_kind}_{location}_install_profile"
```

## 3. 实施步骤

### 3.1 增强 runsite_config.py

需要添加以下函数：

1. `load_json(file_path)`: 加载 JSON 文件
2. `match_hardware_profile(hardware_type, use_slurm, node_count)`: 匹配硬件配置
3. `determine_mode_and_backend(execution_channel, hardware_kind)`: 确定 mode 和 backend_id
4. `determine_runtime_profile_ref(execution_mode, hardware_kind)`: 确定 runtime_profile_ref
5. `determine_install_profile_ref(hardware_kind, access_mode)`: 确定 install_profile_ref
6. `build_config(...)`: 主配置构建函数

### 3.2 重构 cmd_generate 函数

新的 `cmd_generate` 应该：

1. 接收参数：
   - `--execution-channel`: 执行通道
   - `--run-site-data`: run_site 数据（JSON字符串）
   - `--cluster-data`: cluster 数据（JSON字符串，可选）
   - `--modules`: 模块列表（可选）
2. 执行流程：
   - 检测硬件
   - 确定是否使用 Slurm
   - 匹配 hardware_profile
   - 加载各种配置源
   - 组装最终配置
   - 保存

### 3.3 更新 SKILL.md 文档

更新技能文档，明确说明：

1. 配置生成的详细流程
2. 各字段的来源映射
3. 调用 `cmd_generate` 时需要传递的参数
4. 示例命令

## 4. 配置示例

### 4.1 DCU + Slurm + SSH 远程

```json
{
  "runtime": {
    "execution_profile": {
      "run_site": "remote",
      "execution_mode": "slurm",
      "access_mode": "ssh"
    },
    "ssh": {
      "host": "dzeshell.hpccube.com",
      "hostname": "dzeshell.hpccube.com",
      "port": 22,
      "user": "test",
      "strict_host_key_checking": "no",
      "password_authentication": "no",
      "identity_file": "",
      "work_dir": "~/onescience-work"
    },
    "target": {
      "scheduler_type": "slurm",
      "platform_type": "cluster",
      "cpu_arch": "x86_64",
      "cpu_vendor": "amd",
      "accelerator_kind": "dcu",
      "accelerator_vendor": "amd",
      "node_scope": "single_node"
    },
    "environment": {
      "cpu": {
        "arch": "x86_64",
        "vendor": "amd"
      },
      "accelerator_defaults": {
        "kind": "dcu",
        "vendor": "amd",
        "visibility_env": "HIP_VISIBLE_DEVICES",
        "distributed_backend": "rccl",
        "launch_mode": "python",
        "distributed_mode": "single"
      }
    },
    "cluster": {
      "partition": "hpctest01",
      "nodes": 1,
      "gpus_per_node": 1,
      "cpus_per_task": 8,
      "memory": "64GB",
      "time_limit": "02:00:00",
      "gpu_type": "dcu",
      "ntasks_per_node": 1
    },
    "modules": [
      "sghpc-mpi-gcc/26.3",
      "sghpcdas/25.6"
    ],
    "resources": {
      "gpu_type": "dcu",
      "cpu_memory_ratio": 8,
      "disk_space": "100GB"
    },
    "env_vars": {
      "ONESCIENCE_DATASETS_DIR": "/public/share/sugonhpcapp01/onestore/onedatasets/",
      "ONESCIENCE_MODELS_DIR": "/public/share/sugonhpcapp01/onestore/onemodels/"
    }
  }
}
```

### 4.1 DCU + Slurm + scnet 远程

```json
{
  "runtime": {
    "execution_profile": {
      "run_site": "remote",
      "execution_mode": "slurm",
      "access_mode": "scnet"
    },
    "ssh": {
      "host": "dzeshell.hpccube.com",
      "hostname": "dzeshell.hpccube.com",
      "port": 22,
      "user": "test",
      "strict_host_key_checking": "no",
      "password_authentication": "no",
      "identity_file": "",
      "work_dir": "~/onescience-work"
    },
    "scnet": {
      "SCNET_ACCESS_KEY": "<SCNET_ACCESS_KEY>",
      "SCNET_SECRET_KEY": "<SCNET_SECRET_KEY>",
      "SCNET_USER": "alice",
      "region": "核心节点",
      "remote_work_dir": "~/onescience-work"
    },
    "scnet": {
      "SCNET_ACCESS_KEY": "cb0a003",
      "SCNET_SECRET_KEY": "4ea415",
      "SCNET_USER": "test",
      "region": "核心节点",
      "work_dir": "test"
    },
    "target": {
      "scheduler_type": "slurm",
      "platform_type": "cluster",
      "cpu_arch": "x86_64",
      "cpu_vendor": "amd",
      "accelerator_kind": "dcu",
      "accelerator_vendor": "amd",
      "node_scope": "single_node"
    },
    "environment": {
      "cpu": {
        "arch": "x86_64",
        "vendor": "amd"
      },
      "accelerator_defaults": {
        "kind": "dcu",
        "vendor": "amd",
        "visibility_env": "HIP_VISIBLE_DEVICES",
        "distributed_backend": "rccl",
        "launch_mode": "python",
        "distributed_mode": "single"
      }
    },
    "cluster": {
      "partition": "hpctest01",
      "nodes": 1,
      "gpus_per_node": 1,
      "cpus_per_task": 8,
      "memory": "64GB",
      "time_limit": "02:00:00",
      "gpu_type": "dcu",
      "ntasks_per_node": 1
    },
    "modules": [
      "sghpc-mpi-gcc/26.3",
      "sghpcdas/25.6"
    ],
    "resources": {
      "gpu_type": "dcu",
      "cpu_memory_ratio": 8,
      "disk_space": "100GB"
    },
    "env_vars": {
      "ONESCIENCE_DATASETS_DIR": "/public/share/sugonhpcapp01/onestore/onedatasets/",
      "ONESCIENCE_MODELS_DIR": "/public/share/sugonhpcapp01/onestore/onemodels/"
    }
  }
}
```

### 4.3 GPU + 本地直接运行

```json
{
  "runtime": {
    "mode": "local",
    "backend_id": "local_gpu",
    "execution_profile": {
      "execution_mode": "local",
      "access_mode": "local",
      "runtime_profile_ref": "local_gpu",
      "install_profile_ref": "gpu_local_install_profile"
    },
    "local": {},
    "target": {
      "scheduler_type": null,
      "platform_type": "workstation",
      "cpu_arch": "x86_64",
      "cpu_vendor": "intel",
      "accelerator_kind": "gpu",
      "accelerator_vendor": "nvidia",
      "node_scope": "single_node"
    },
    "environment": {
      "cpu": {
        "arch": "x86_64",
        "vendor": "intel"
      },
      "accelerator_defaults": {
        "kind": "gpu",
        "vendor": "nvidia",
        "visibility_env": "CUDA_VISIBLE_DEVICES",
        "distributed_backend": "nccl",
        "launch_mode": "python",
        "distributed_mode": "single"
      }
    },
    "cluster": null,
    "modules": [],
    "resources": {
      "gpu_type": "gpu",
      "cpu_memory_ratio": 8,
      "disk_space": "100GB"
    },
    "env_vars": {
      "ONESCIENCE_DATASETS_DIR": "/public/share/sugonhpcapp01/onestore/onedatasets/",
      "ONESCIENCE_MODELS_DIR": "/public/share/sugonhpcapp01/onestore/onemodels/"
    }
  }
}
```

## 5. 关键约束

1. **不修改已存在的 onescience.json**：生成功能仅在文件不存在时使用
2. **模板优先级**：hardware_profile > cluster_profile > runsite_profile > 默认值
3. **用户输入优先**：用户明确提供的值优先于模板值
4. **向后兼容**：保持与现有 onescience-runtime 技能的兼容性
5. **验证必填字段**：生成前验证所有必需数据已提供

## 6. 测试计划

### 6.1 单元测试

- 测试 `match_hardware_profile()` 的各种匹配场景
- 测试 `determine_mode_and_backend()` 的映射逻辑
- 测试 `determine_runtime_profile_ref()` 和 `determine_install_profile_ref()` 的命名规则

### 6.2 集成测试

- 测试完整的配置生成流程
- 测试生成的配置能被 onescience-runtime 正确解析
- 测试各种组合：local/remote, dcu/gpu, slurm/direct

### 6.3 验证清单

- [ ] 生成的 onescience.json 结构与 runsite.example.json 一致
- [ ] run_site 字段完全来自 runsite_profile 模板
- [ ] cluster 字段完全来自 cluster_profile 模板（当使用 Slurm 时）
- [ ] env_vars 字段完全来自 env_vars/config.json
- [ ] target 和 environment 字段正确反映硬件检测和 hardware_profile
- [ ] mode 和 backend_id 根据执行通道和硬件正确确定
- [ ] runtime_profile_ref 和 install_profile_ref 命名符合规范
- [ ] scheduler_type 和 platform_type 来自 hardware_profile

## 7. 后续改进

1. **Profile 版本管理**：为 hardware_profiles 添加版本标识
2. **配置验证**：添加生成后的配置验证功能
3. **智能推荐**：根据硬件和任务类型推荐最优配置
4. **配置导出导入**：支持配置的导出和跨项目导入
