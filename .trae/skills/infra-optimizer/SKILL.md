---
name: infra-optimizer
description: 系统层技能，负责系统优化、并行策略和平台适配
---

# Skill: infra-optimizer

## 能力描述

本技能负责 AI4S Pipeline 的系统层任务，包括系统优化、并行策略和平台适配。基于 OneScience 组件库和构建的知识体系，提供完整的系统优化解决方案。

## 核心能力

### 1. 系统优化

支持多种系统优化方式：

| 优化类型 | 支持情况 | 说明 |
|---------|---------|------|
| AMP 混合精度 | ✅ 完全支持 | 自动混合精度 |
| 显存优化 | ✅ 完全支持 | 显存使用优化 |
| 计算优化 | ✅ 完全支持 | 计算效率优化 |
| 数据加载优化 | ✅ 完全支持 | 数据加载加速 |

### 2. 并行策略

支持多种并行策略：

| 并行类型 | 支持情况 | 说明 |
|---------|---------|------|
| 数据并行 | ✅ 完全支持 | DataParallel |
| 模型并行 | ✅ 完全支持 | ModelParallel |
| 分布式训练 | ✅ 完全支持 | DDP、DeepSpeed |
| 梯度累积 | ✅ 完全支持 | 梯度累积优化 |

### 3. 平台适配

支持多种平台适配：

| 平台类型 | 支持情况 | 说明 |
|---------|---------|------|
| GPU 平台 | ✅ 完全支持 | CUDA 优化 |
| CPU 平台 | ✅ 完全支持 | CPU 优化 |
| TPU 平台 | ✅ 完全支持 | TPU 适配 |
| 多框架 | ✅ 完全支持 | PyTorch/TensorFlow |

## 使用方法

### 场景 1：系统优化

**用户需求**：优化 Pangu-Weather 模型的显存使用和计算效率。

**Prompt**：
```
基于./oneskills/trae/task/react_prompt.md中的工作流执行以下任务：
优化 Pangu-Weather 模型的显存使用和计算效率，要求：
1. 启用混合精度训练（AMP）
2. 启用梯度检查点
3. 优化数据加载
4. 生成优化代码
5. 保存至 optimized_model.py
```

**输出**：优化后的模型代码

### 场景 2：并行策略

**用户需求**：为 GraphCast 模型配置多GPU并行训练。

**Prompt**：
```
基于./oneskills/trae/task/react_prompt.md中的工作流执行以下任务：
为 GraphCast 模型配置多GPU并行训练，要求：
1. 配置数据并行
2. 配置分布式训练
3. 生成并行训练脚本
4. 保存至 distributed_training.py
```

**输出**：并行训练代码

### 场景 3：平台适配

**用户需求**：适配 Pangu-Weather 模型到不同硬件平台。

**Prompt**：
```
基于./oneskills/trae/task/react_prompt.md中的工作流执行以下任务：
适配 Pangu-Weather 模型到不同硬件平台，要求：
1. GPU 平台优化
2. CPU 平台支持
3. TPU 平台适配
4. 生成平台适配代码
5. 保存至 platform_adaptation.py
```

**输出**：平台适配代码

## 核心规则

### 1. 系统优化规范（强制）

所有系统优化必须遵循以下规范：

```python
# 系统优化规范
def system_optimization_pipeline(config):
    # 1. AMP 混合精度
    amp_config = configure_amp(config)
    
    # 2. 显存优化
    memory_config = configure_memory(config)
    
    # 3. 计算优化
    compute_config = configure_compute(config)
    
    # 4. 数据加载优化
    dataloader_config = configure_dataloader(config)
    
    return amp_config, memory_config, compute_config, dataloader_config
```

### 2. 并行策略规范（强制）

并行策略必须遵循以下规范：

```python
# 并行策略规范
def parallel_strategy_pipeline(config):
    # 1. 数据并行
    dp_config = configure_data_parallel(config)
    
    # 2. 模型并行
    mp_config = configure_model_parallel(config)
    
    # 3. 分布式训练
    dist_config = configure_distributed(config)
    
    # 4. 梯度累积
    grad_accum_config = configure_gradient_accumulation(config)
    
    return dp_config, mp_config, dist_config, grad_accum_config
```

### 3. 平台适配规范（强制）

平台适配必须遵循以下规范：

```python
# 平台适配规范
def platform_adaptation_pipeline(config):
    # 1. GPU 平台适配
    gpu_config = configure_gpu(config)
    
    # 2. CPU 平台适配
    cpu_config = configure_cpu(config)
    
    # 3. TPU 平台适配
    tpu_config = configure_tpu(config)
    
    # 4. 多框架适配
    framework_config = configure_framework(config)
    
    return gpu_config, cpu_config, tpu_config, framework_config
```

## 输出格式

### 系统优化代码模板

```python
"""
Infra Optimizer - 系统优化

任务描述：{任务描述}
优化类型：{优化类型}
"""

import torch
import torch.nn as nn
import torch.cuda.amp as amp
from typing import Dict, List, Tuple


class SystemOptimizer:
    """
    系统优化类
    
    功能：
    - AMP 混合精度
    - 显存优化
    - 计算优化
    - 数据加载优化
    """
    
    def __init__(self, config: Dict):
        self.config = config
    
    def configure_amp(self, config: Dict) -> Dict:
        """配置 AMP 混合精度"""
        amp_config = {
            "enabled": config.get("amp_enabled", True),
            "dtype": config.get("amp_dtype", "float16"),
            "loss_scale": config.get("loss_scale", "dynamic"),
            "opt_level": config.get("opt_level", "O1")
        }
        
        return amp_config
    
    def configure_memory(self, config: Dict) -> Dict:
        """配置显存优化"""
        memory_config = {
            "gradient_checkpointing": config.get("gradient_checkpointing", False),
            "num_checkpoint_segments": config.get("num_checkpoint_segments", 1),
            "memory_format": config.get("memory_format", "contiguous_format"),
            "pin_memory": config.get("pin_memory", True)
        }
        
        return memory_config
    
    def configure_compute(self, config: Dict) -> Dict:
        """配置计算优化"""
        compute_config = {
            "torch_compile": config.get("torch_compile", False),
            "fused_ops": config.get("fused_ops", True),
            "memory_efficient_ops": config.get("memory_efficient_ops", True),
            "num_threads": config.get("num_threads", 1)
        }
        
        return compute_config
    
    def configure_dataloader(self, config: Dict) -> Dict:
        """配置数据加载优化"""
        dataloader_config = {
            "num_workers": config.get("num_workers", 4),
            "pin_memory": config.get("pin_memory", True),
            "persistent_workers": config.get("persistent_workers", True),
            "prefetch_factor": config.get("prefetch_factor", 2)
        }
        
        return dataloader_config


if __name__ == '__main__':
    # 使用示例
    optimizer = SystemOptimizer(config)
    
    # 配置 AMP 混合精度
    amp_config = optimizer.configure_amp(config)
    
    # 配置显存优化
    memory_config = optimizer.configure_memory(config)
    
    # 配置计算优化
    compute_config = optimizer.configure_compute(config)
    
    # 配置数据加载优化
    dataloader_config = optimizer.configure_dataloader(config)
```

### 并行训练代码模板

```python
"""
Infra Optimizer - 并行训练

任务描述：{任务描述}
并行类型：{并行类型}
"""

import torch
import torch.nn as nn
import torch.distributed as dist
import torch.multiprocessing as mp
from typing import Dict, List, Tuple


class ParallelTrainer:
    """
    并行训练类
    
    功能：
    - 数据并行
    - 模型并行
    - 分布式训练
    - 梯度累积
    """
    
    def __init__(self, config: Dict):
        self.config = config
    
    def configure_data_parallel(self, config: Dict) -> Dict:
        """配置数据并行"""
        dp_config = {
            "use_dataparallel": config.get("use_dataparallel", False),
            "device_ids": config.get("device_ids", None),
            "output_device": config.get("output_device", None)
        }
        
        return dp_config
    
    def configure_model_parallel(self, config: Dict) -> Dict:
        """配置模型并行"""
        mp_config = {
            "use_modelparallel": config.get("use_modelparallel", False),
            "parallel_segments": config.get("parallel_segments", 2)
        }
        
        return mp_config
    
    def configure_distributed(self, config: Dict) -> Dict:
        """配置分布式训练"""
        dist_config = {
            "backend": config.get("backend", "nccl"),
            "world_size": config.get("world_size", 1),
            "rank": config.get("rank", 0),
            "master_addr": config.get("master_addr", "127.0.0.1"),
            "master_port": config.get("master_port", "29500")
        }
        
        return dist_config
    
    def configure_gradient_accumulation(self, config: Dict) -> Dict:
        """配置梯度累积"""
        grad_accum_config = {
            "enabled": config.get("gradient_accumulation", False),
            "accum_steps": config.get("accum_steps", 1)
        }
        
        return grad_accum_config


if __name__ == '__main__':
    # 使用示例
    trainer = ParallelTrainer(config)
    
    # 配置数据并行
    dp_config = trainer.configure_data_parallel(config)
    
    # 配置模型并行
    mp_config = trainer.configure_model_parallel(config)
    
    # 配置分布式训练
    dist_config = trainer.configure_distributed(config)
    
    # 配置梯度累积
    grad_accum_config = trainer.configure_gradient_accumulation(config)
```

### 平台适配代码模板

```python
"""
Infra Optimizer - 平台适配

任务描述：{任务描述}
平台类型：{平台类型}
"""

import torch
import torch.nn as nn
from typing import Dict, List, Tuple


class PlatformAdapter:
    """
    平台适配类
    
    功能：
    - GPU 平台适配
    - CPU 平台适配
    - TPU 平台适配
    - 多框架适配
    """
    
    def __init__(self, config: Dict):
        self.config = config
    
    def configure_gpu(self, config: Dict) -> Dict:
        """配置 GPU 平台"""
        gpu_config = {
            "use_cuda": config.get("use_cuda", True),
            "device_ids": config.get("device_ids", None),
            "mixed_precision": config.get("mixed_precision", False),
            "cudnn_benchmark": config.get("cudnn_benchmark", True)
        }
        
        return gpu_config
    
    def configure_cpu(self, config: Dict) -> Dict:
        """配置 CPU 平台"""
        cpu_config = {
            "use_cpu": config.get("use_cpu", True),
            "num_threads": config.get("num_threads", 1),
            "memory_format": config.get("memory_format", "contiguous_format")
        }
        
        return cpu_config
    
    def configure_tpu(self, config: Dict) -> Dict:
        """配置 TPU 平台"""
        tpu_config = {
            "use_tpu": config.get("use_tpu", False),
            "tpu_name": config.get("tpu_name", None),
            "mixed_precision": config.get("mixed_precision", False)
        }
        
        return tpu_config
    
    def configure_framework(self, config: Dict) -> Dict:
        """配置多框架适配"""
        framework_config = {
            "framework": config.get("framework", "pytorch"),
            "convert_to_onnx": config.get("convert_to_onnx", False),
            "convert_to_torchscript": config.get("convert_to_torchscript", False)
        }
        
        return framework_config


if __name__ == '__main__':
    # 使用示例
    adapter = PlatformAdapter(config)
    
    # 配置 GPU 平台
    gpu_config = adapter.configure_gpu(config)
    
    # 配置 CPU 平台
    cpu_config = adapter.configure_cpu(config)
    
    # 配置 TPU 平台
    tpu_config = adapter.configure_tpu(config)
    
    # 配置多框架适配
    framework_config = adapter.configure_framework(config)
```

## 最佳实践

### 1. 系统优化最佳实践

```python
# 系统优化最佳实践
def system_optimization_best_practices(config: Dict) -> Dict:
    # 1. 配置 AMP 混合精度
    amp_config = configure_amp(config)
    
    # 2. 配置显存优化
    memory_config = configure_memory(config)
    
    # 3. 配置计算优化
    compute_config = configure_compute(config)
    
    # 4. 配置数据加载优化
    dataloader_config = configure_dataloader(config)
    
    return {
        "amp_config": amp_config,
        "memory_config": memory_config,
        "compute_config": compute_config,
        "dataloader_config": dataloader_config
    }
```

### 2. 并行策略最佳实践

```python
# 并行策略最佳实践
def parallel_strategy_best_practices(config: Dict) -> Dict:
    # 1. 配置数据并行
    dp_config = configure_data_parallel(config)
    
    # 2. 配置模型并行
    mp_config = configure_model_parallel(config)
    
    # 3. 配置分布式训练
    dist_config = configure_distributed(config)
    
    # 4. 配置梯度累积
    grad_accum_config = configure_gradient_accumulation(config)
    
    return {
        "dp_config": dp_config,
        "mp_config": mp_config,
        "dist_config": dist_config,
        "grad_accum_config": grad_accum_config
    }
```

### 3. 平台适配最佳实践

```python
# 平台适配最佳实践
def platform_adaptation_best_practices(config: Dict) -> Dict:
    # 1. 配置 GPU 平台
    gpu_config = configure_gpu(config)
    
    # 2. 配置 CPU 平台
    cpu_config = configure_cpu(config)
    
    # 3. 配置 TPU 平台
    tpu_config = configure_tpu(config)
    
    # 4. 配置多框架适配
    framework_config = configure_framework(config)
    
    return {
        "gpu_config": gpu_config,
        "cpu_config": cpu_config,
        "tpu_config": tpu_config,
        "framework_config": framework_config
    }
```

## 错误处理

### 常见错误 1：AMP 配置失败

**错误**：AMP 配置失败

**解决**：使用多种 AMP 策略

```python
# 多种 AMP 策略
def configure_amp_with_strategies(config: Dict) -> Dict:
    # 策略 1：标准 AMP
    try:
        amp_config = {
            "enabled": True,
            "dtype": "float16",
            "loss_scale": "dynamic",
            "opt_level": "O1"
        }
        return amp_config
    except Exception as e:
        print(f"Standard AMP failed: {e}")
    
    # 策略 2：纯 FP32
    try:
        amp_config = {
            "enabled": False,
            "dtype": "float32"
        }
        return amp_config
    except Exception as e:
        print(f"Pure FP32 failed: {e}")
    
    raise AMPError("All AMP strategies failed")
```

### 常见错误 2：分布式训练配置失败

**错误**：分布式训练配置失败

**解决**：使用分布式训练工作流

```python
# 分布式训练工作流
def distributed_training_workflow(config: Dict) -> Dict:
    # 1. 配置分布式环境
    try:
        dist_config = configure_distributed(config)
        return dist_config
    except Exception as e:
        print(f"Distributed configuration failed: {e}")
    
    # 2. 回退到单机训练
    try:
        single_machine_config = configure_single_machine(config)
        return single_machine_config
    except Exception as e:
        print(f"Single machine configuration failed: {e}")
    
    raise DistributedError("All distributed configuration strategies failed")
```

## 总结

本技能提供了系统层的完整解决方案：

- ✅ **系统优化**：多种优化方式
- ✅ **并行策略**：多种并行策略
- ✅ **平台适配**：多种平台支持
- ✅ **错误处理**：完善的错误处理机制
- ✅ **最佳实践**：遵循领域最佳实践

通过本技能，用户可以快速完成系统层任务。
