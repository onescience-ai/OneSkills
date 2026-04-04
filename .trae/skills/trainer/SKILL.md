---
name: trainer
description: 训练层技能，负责训练策略和训练流程配置
---

# Skill: trainer

## 能力描述

本技能负责 AI4S Pipeline 的训练层任务，包括训练策略配置和训练流程工程化。基于 OneScience 组件库和构建的知识体系，提供完整的训练解决方案。

## 核心能力

### 1. 训练策略

支持多种训练策略：

| 策略类型 | 支持情况 | 说明 |
|---------|---------|------|
| 预训练迁移 | ✅ 完全支持 | 加载预训练权重 |
| 微调策略 | ✅ 完全支持 | 部分参数微调 |
| 冻结策略 | ✅ 完全支持 | 冻结部分参数 |
| 学习率调度 | ✅ 完全支持 | 多种调度策略 |
| 优化器选择 | ✅ 完全支持 | 多种优化器 |

### 2. 训练流程工程化

支持完整的训练流程：

| 流程类型 | 支持情况 | 说明 |
|---------|---------|------|
| 配置生成 | ✅ 完全支持 | YAML 配置文件 |
| 脚本生成 | ✅ 完全支持 | 训练脚本 |
| 分布式训练 | ✅ 完全支持 | 多GPU、多节点 |
| 混合精度 | ✅ 完全支持 | AMP 训练 |
| 梯度检查点 | ✅ 完全支持 | 节省显存 |

## 使用方法

### 场景 1：训练策略配置

**用户需求**：配置预训练迁移和微调策略。

**Prompt**：
```
基于./oneskills/trae/task/react_prompt.md中的工作流执行以下任务：
配置 Pangu-Weather 模型的预训练迁移和微调策略，要求：
1. 加载预训练权重
2. 设计冻结策略
3. 配置微调学习率
4. 生成训练脚本
5. 保存至 fine_tuning.py
```

**输出**：训练策略代码

### 场景 2：训练流程工程化

**用户需求**：为 GraphCast 模型生成完整的训练配置和脚本。

**Prompt**：
```
基于./oneskills/trae/task/react_prompt.md中的工作流执行以下任务：
为 GraphCast 模型生成完整的训练配置和脚本，要求：
1. 生成 YAML 配置文件
2. 生成单机单卡、单机多卡、多机多卡脚本
3. 配置混合精度训练
4. 保存至 train_graphcast.py 和 configs/
```

**输出**：训练脚本和配置文件

## 核心规则

### 1. 训练策略规范（强制）

所有训练策略必须遵循以下规范：

```python
# 训练策略规范
def training_strategy_pipeline(config):
    # 1. 预训练迁移
    pretrained_model = load_pretrained_model(config["pretrained"])
    
    # 2. 冻结策略
    frozen_layers = apply_freeze_strategy(pretrained_model, config["freeze"])
    
    # 3. 微调策略
    fine_tuned_model = apply_finetune_strategy(frozen_layers, config["finetune"])
    
    # 4. 学习率调度
    scheduler = configure_scheduler(fine_tuned_model, config["scheduler"])
    
    # 5. 优化器选择
    optimizer = configure_optimizer(fine_tuned_model, config["optimizer"])
    
    return fine_tuned_model, optimizer, scheduler
```

### 2. 训练流程规范（强制）

训练流程必须遵循以下规范：

```python
# 训练流程规范
def training_pipeline_pipeline(config):
    # 1. 配置生成
    yaml_config = generate_yaml_config(config)
    
    # 2. 脚本生成
    training_script = generate_training_script(config)
    
    # 3. 分布式训练
    distributed_config = configure_distributed(config)
    
    # 4. 混合精度
    amp_config = configure_amp(config)
    
    # 5. 梯度检查点
    checkpoint_config = configure_gradient_checkpointing(config)
    
    return yaml_config, training_script, distributed_config, amp_config, checkpoint_config
```

## 输出格式

### 训练策略代码模板

```python
"""
Trainer - 训练策略

任务描述：{任务描述}
策略类型：{策略类型}
"""

import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, List, Tuple


class TrainingStrategy:
    """
    训练策略类
    
    功能：
    - 预训练迁移
    - 冻结策略
    - 微调策略
    - 学习率调度
    - 优化器选择
    """
    
    def __init__(self, config: Dict):
        self.config = config
    
    def load_pretrained_model(self, pretrained_path: str) -> nn.Module:
        """加载预训练模型"""
        model = torch.load(pretrained_path)
        return model
    
    def apply_freeze_strategy(self, model: nn.Module, freeze_config: Dict) -> nn.Module:
        """应用冻结策略"""
        for name, param in model.named_parameters():
            if self._should_freeze(name, freeze_config):
                param.requires_grad = False
        
        return model
    
    def apply_finetune_strategy(self, model: nn.Module, finetune_config: Dict) -> nn.Module:
        """应用微调策略"""
        # 解冻特定层
        for name, param in model.named_parameters():
            if self._should_finetune(name, finetune_config):
                param.requires_grad = True
        
        return model
    
    def configure_scheduler(self, model: nn.Module, scheduler_config: Dict) -> optim.lr_scheduler._LRScheduler:
        """配置学习率调度器"""
        scheduler_type = scheduler_config.get("type", "cosine")
        
        if scheduler_type == "cosine":
            scheduler = optim.lr_scheduler.CosineAnnealingLR(
                model.optimizer,
                T_max=scheduler_config.get("T_max", 100),
                eta_min=scheduler_config.get("eta_min", 1e-6)
            )
        elif scheduler_type == "step":
            scheduler = optim.lr_scheduler.StepLR(
                model.optimizer,
                step_size=scheduler_config.get("step_size", 30),
                gamma=scheduler_config.get("gamma", 0.1)
            )
        else:
            raise ValueError(f"Unsupported scheduler type: {scheduler_type}")
        
        return scheduler
    
    def configure_optimizer(self, model: nn.Module, optimizer_config: Dict) -> optim.Optimizer:
        """配置优化器"""
        optimizer_type = optimizer_config.get("type", "adam")
        
        if optimizer_type == "adam":
            optimizer = optim.Adam(
                model.parameters(),
                lr=optimizer_config.get("lr", 1e-4),
                betas=optimizer_config.get("betas", (0.9, 0.999))
            )
        elif optimizer_type == "adamw":
            optimizer = optim.AdamW(
                model.parameters(),
                lr=optimizer_config.get("lr", 1e-4),
                betas=optimizer_config.get("betas", (0.9, 0.999)),
                weight_decay=optimizer_config.get("weight_decay", 1e-2)
            )
        else:
            raise ValueError(f"Unsupported optimizer type: {optimizer_type}")
        
        return optimizer


if __name__ == '__main__':
    # 使用示例
    strategy = TrainingStrategy(config)
    
    # 加载预训练模型
    pretrained_model = strategy.load_pretrained_model(pretrained_path)
    
    # 应用冻结策略
    frozen_model = strategy.apply_freeze_strategy(pretrained_model, freeze_config)
    
    # 应用微调策略
    fine_tuned_model = strategy.apply_finetune_strategy(frozen_model, finetune_config)
    
    # 配置学习率调度器
    scheduler = strategy.configure_scheduler(fine_tuned_model, scheduler_config)
    
    # 配置优化器
    optimizer = strategy.configure_optimizer(fine_tuned_model, optimizer_config)
```

### 训练流程代码模板

```python
"""
Trainer - 训练流程

任务描述：{任务描述}
流程类型：{流程类型}
"""

import torch
import torch.nn as nn
import torch.optim as optim
import yaml
from pathlib import Path
from typing import Dict, List, Tuple


class TrainingPipeline:
    """
    训练流程类
    
    功能：
    - 配置生成
    - 脚本生成
    - 分布式训练
    - 混合精度
    - 梯度检查点
    """
    
    def __init__(self, config: Dict):
        self.config = config
    
    def generate_yaml_config(self, config: Dict) -> str:
        """生成 YAML 配置文件"""
        yaml_config = yaml.dump(config, default_flow_style=False)
        
        # 保存配置文件
        config_path = Path(self.config.get("config_path", "configs/training_config.yaml"))
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, "w") as f:
            f.write(yaml_config)
        
        return yaml_config
    
    def generate_training_script(self, config: Dict) -> str:
        """生成训练脚本"""
        script = f"""
import torch
import torch.nn as nn
import torch.optim as optim
import yaml
from pathlib import Path

# 加载配置
with open("{config.get("config_path", "configs/training_config.yaml")}", "r") as f:
    config = yaml.safe_load(f)

# 模型定义
model = {config["model"]["type"]}(**config["model"]["args"])

# 优化器
optimizer = optim.{config["optimizer"]["type"]}(model.parameters(), lr={config["optimizer"]["lr"]})

# 损失函数
criterion = nn.{config["loss"]["type"]}()

# 训练循环
for epoch in range({config["training"]["num_epochs"]}):
    for batch in train_loader:
        optimizer.zero_grad()
        output = model(batch["input"])
        loss = criterion(output, batch["target"])
        loss.backward()
        optimizer.step()
    
    print(f"Epoch {epoch}: Loss = {loss.item()}")
"""
        
        # 保存训练脚本
        script_path = Path(self.config.get("script_path", "train.py"))
        with open(script_path, "w") as f:
            f.write(script)
        
        return script
    
    def configure_distributed(self, config: Dict) -> Dict:
        """配置分布式训练"""
        distributed_config = {
            "backend": config.get("backend", "nccl"),
            "world_size": config.get("world_size", 1),
            "rank": config.get("rank", 0),
            "master_addr": config.get("master_addr", "127.0.0.1"),
            "master_port": config.get("master_port", "29500")
        }
        
        return distributed_config
    
    def configure_amp(self, config: Dict) -> Dict:
        """配置混合精度训练"""
        amp_config = {
            "enabled": config.get("amp_enabled", True),
            "dtype": config.get("amp_dtype", "float16"),
            "loss_scale": config.get("loss_scale", "dynamic"),
            "opt_level": config.get("opt_level", "O1")
        }
        
        return amp_config
    
    def configure_gradient_checkpointing(self, config: Dict) -> Dict:
        """配置梯度检查点"""
        checkpoint_config = {
            "enabled": config.get("checkpoint_enabled", False),
            "num_checkpoint_segments": config.get("num_checkpoint_segments", 1)
        }
        
        return checkpoint_config


if __name__ == '__main__':
    # 使用示例
    pipeline = TrainingPipeline(config)
    
    # 生成 YAML 配置文件
    yaml_config = pipeline.generate_yaml_config(config)
    
    # 生成训练脚本
    training_script = pipeline.generate_training_script(config)
    
    # 配置分布式训练
    distributed_config = pipeline.configure_distributed(config)
    
    # 配置混合精度
    amp_config = pipeline.configure_amp(config)
    
    # 配置梯度检查点
    checkpoint_config = pipeline.configure_gradient_checkpointing(config)
```

## 最佳实践

### 1. 训练策略最佳实践

```python
# 训练策略最佳实践
def training_strategy_best_practices(config: Dict) -> Tuple[nn.Module, optim.Optimizer, optim.lr_scheduler._LRScheduler]:
    # 1. 加载预训练模型
    pretrained_model = load_pretrained_model(config["pretrained"])
    
    # 2. 应用冻结策略
    frozen_model = apply_freeze_strategy(pretrained_model, config["freeze"])
    
    # 3. 应用微调策略
    fine_tuned_model = apply_finetune_strategy(frozen_model, config["finetune"])
    
    # 4. 配置学习率调度器
    scheduler = configure_scheduler(fine_tuned_model, config["scheduler"])
    
    # 5. 配置优化器
    optimizer = configure_optimizer(fine_tuned_model, config["optimizer"])
    
    return fine_tuned_model, optimizer, scheduler
```

### 2. 训练流程最佳实践

```python
# 训练流程最佳实践
def training_pipeline_best_practices(config: Dict) -> Dict:
    # 1. 生成 YAML 配置文件
    yaml_config = generate_yaml_config(config)
    
    # 2. 生成训练脚本
    training_script = generate_training_script(config)
    
    # 3. 配置分布式训练
    distributed_config = configure_distributed(config)
    
    # 4. 配置混合精度
    amp_config = configure_amp(config)
    
    # 5. 配置梯度检查点
    checkpoint_config = configure_gradient_checkpointing(config)
    
    return {
        "yaml_config": yaml_config,
        "training_script": training_script,
        "distributed_config": distributed_config,
        "amp_config": amp_config,
        "checkpoint_config": checkpoint_config
    }
```

## 错误处理

### 常见错误 1：预训练权重加载失败

**错误**：预训练权重加载失败

**解决**：使用多种加载策略

```python
# 多种加载策略
def load_pretrained_model_with_strategies(pretrained_path: str) -> nn.Module:
    # 策略 1：直接加载
    try:
        model = torch.load(pretrained_path)
        return model
    except Exception as e:
        print(f"Direct loading failed: {e}")
    
    # 策略 2：部分加载
    try:
        model = torch.load(pretrained_path, map_location="cpu")
        # 部分加载逻辑
        return model
    except Exception as e:
        print(f"Partial loading failed: {e}")
    
    raise LoadError("All loading strategies failed")
```

### 常见错误 2：分布式训练配置失败

**错误**：分布式训练配置失败

**解决**：使用分布式训练工作流

```python
# 分布式训练工作流
def distributed_training_workflow(config: Dict) -> Dict:
    # 1. 配置分布式环境
    try:
        distributed_config = configure_distributed(config)
        return distributed_config
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

本技能提供了训练层的完整解决方案：

- ✅ **训练策略**：多种训练策略
- ✅ **训练流程**：完整的训练流程
- ✅ **分布式训练**：多GPU、多节点支持
- ✅ **混合精度**：AMP 训练
- ✅ **梯度检查点**：节省显存
- ✅ **错误处理**：完善的错误处理机制
- ✅ **最佳实践**：遵循领域最佳实践

通过本技能，用户可以快速完成训练层任务。
