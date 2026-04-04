---
name: debugger
description: 诊断层技能，负责模型诊断、调试和性能分析
---

# Skill: debugger

## 能力描述

本技能负责 AI4S Pipeline 的诊断层任务，包括模型诊断、调试和性能分析。基于 OneScience 组件库和构建的知识体系，提供完整的诊断和调试解决方案。

## 核心能力

### 1. 模型诊断

支持多种模型诊断方式：

| 诊断类型 | 支持情况 | 说明 |
|---------|---------|------|
| 梯度爆炸/消失 | ✅ 完全支持 | 梯度监控 |
| NaN/Inf 检测 | ✅ 完全支持 | 数值异常检测 |
| 不收敛检测 | ✅ 完全支持 | 训练曲线分析 |
| 内存泄漏检测 | ✅ 完全支持 | 内存监控 |

### 2. 训练调试

支持多种训练调试方式：

| 调试类型 | 支持情况 | 说明 |
|---------|---------|------|
| 前向传播调试 | ✅ 完全支持 | 前向传播监控 |
| 反向传播调试 | ✅ 完全支持 | 反向传播监控 |
| 损失函数调试 | ✅ 完全支持 | 损失监控 |
| 梯度调试 | ✅ 完全支持 | 梯度监控 |

### 3. 性能分析

支持多种性能分析方式：

| 分析类型 | 支持情况 | 说明 |
|---------|---------|------|
| 计算性能分析 | ✅ 完全支持 | FLOPS、时间分析 |
| 内存性能分析 | ✅ 完全支持 | 显存、内存分析 |
| 数据加载性能分析 | ✅ 完全支持 | DataLoader 性能 |
| I/O 性能分析 | ✅ 完全支持 | 数据读取性能 |

## 使用方法

### 场景 1：模型诊断

**用户需求**：诊断 GraphCast 模型训练异常。

**Prompt**：
```
基于./oneskills/trae/task/react_prompt.md中的工作流执行以下任务：
诊断 GraphCast 模型训练异常，要求：
1. 检测梯度爆炸/消失
2. 检测数值异常（NaN/Inf）
3. 分析训练曲线
4. 提供调试建议
5. 保存至 model_diagnosis.py
```

**输出**：诊断工具和调试报告

### 场景 2：训练调试

**用户需求**：调试 Pangu-Weather 模型训练过程。

**Prompt**：
```
基于./oneskills/trae/task/react_prompt.md中的工作流执行以下任务：
调试 Pangu-Weather 模型训练过程，要求：
1. 监控前向传播
2. 监控反向传播
3. 监控损失函数
4. 监控梯度
5. 保存至 training_debug.py
```

**输出**：调试工具和报告

### 场景 3：性能分析

**用户需求**：分析 Pangu-Weather 模型的性能瓶颈。

**Prompt**：
```
基于./oneskills/trae/task/react_prompt.md中的工作流执行以下任务：
分析 Pangu-Weather 模型的性能瓶颈，要求：
1. 分析计算性能
2. 分析内存性能
3. 分析数据加载性能
4. 分析 I/O 性能
5. 提供优化建议
6. 保存至 performance_analysis.py
```

**输出**：性能分析报告和优化建议

## 核心规则

### 1. 模型诊断规范（强制）

所有模型诊断必须遵循以下规范：

```python
# 模型诊断规范
def model_diagnosis_pipeline(model, data_loader, config):
    # 1. 梯度诊断
    gradient_diagnosis = diagnose_gradients(model)
    
    # 2. 数值异常检测
    numerical_diagnosis = diagnose_numerical_issues(model, data_loader)
    
    # 3. 训练曲线分析
    training_diagnosis = diagnose_training_curves(model, data_loader)
    
    # 4. 内存泄漏检测
    memory_diagnosis = diagnose_memory_leaks(model)
    
    return gradient_diagnosis, numerical_diagnosis, training_diagnosis, memory_diagnosis
```

### 2. 训练调试规范（强制）

训练调试必须遵循以下规范：

```python
# 训练调试规范
def training_debugging_pipeline(model, data_loader, config):
    # 1. 前向传播调试
    forward_debug = debug_forward(model, data_loader)
    
    # 2. 反向传播调试
    backward_debug = debug_backward(model, data_loader)
    
    # 3. 损失函数调试
    loss_debug = debug_loss(model, data_loader)
    
    # 4. 梯度调试
    gradient_debug = debug_gradients(model, data_loader)
    
    return forward_debug, backward_debug, loss_debug, gradient_debug
```

### 3. 性能分析规范（强制）

性能分析必须遵循以下规范：

```python
# 性能分析规范
def performance_analysis_pipeline(model, data_loader, config):
    # 1. 计算性能分析
    compute_analysis = analyze_compute_performance(model)
    
    # 2. 内存性能分析
    memory_analysis = analyze_memory_performance(model)
    
    # 3. 数据加载性能分析
    dataloader_analysis = analyze_dataloader_performance(data_loader)
    
    # 4. I/O 性能分析
    io_analysis = analyze_io_performance(data_loader)
    
    return compute_analysis, memory_analysis, dataloader_analysis, io_analysis
```

## 输出格式

### 模型诊断代码模板

```python
"""
Debugger - 模型诊断

任务描述：{任务描述}
诊断类型：{诊断类型}
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Tuple
import logging


class ModelDebugger:
    """
    模型诊断类
    
    功能：
    - 梯度诊断
    - 数值异常检测
    - 训练曲线分析
    - 内存泄漏检测
    """
    
    def __init__(self, model: nn.Module, config: Dict):
        self.model = model
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def diagnose_gradients(self, model: nn.Module) -> Dict:
        """诊断梯度"""
        gradient_info = {
            "grad_norms": {},
            "grad_mean": {},
            "grad_std": {},
            "grad_min": {},
            "grad_max": {},
            "has_nan": False,
            "has_inf": False
        }
        
        for name, param in model.named_parameters():
            if param.grad is not None:
                grad = param.grad.data
                
                gradient_info["grad_norms"][name] = grad.norm().item()
                gradient_info["grad_mean"][name] = grad.mean().item()
                gradient_info["grad_std"][name] = grad.std().item()
                gradient_info["grad_min"][name] = grad.min().item()
                gradient_info["grad_max"][name] = grad.max().item()
                
                if torch.isnan(grad).any():
                    gradient_info["has_nan"] = True
                    self.logger.warning(f"NaN detected in gradient: {name}")
                
                if torch.isinf(grad).any():
                    gradient_info["has_inf"] = True
                    self.logger.warning(f"Inf detected in gradient: {name}")
        
        return gradient_info
    
    def diagnose_numerical_issues(self, model: nn.Module, data_loader) -> Dict:
        """诊断数值异常"""
        numerical_info = {
            "has_nan_input": False,
            "has_inf_input": False,
            "has_nan_output": False,
            "has_inf_output": False,
            "nan_count": 0,
            "inf_count": 0
        }
        
        for batch in data_loader:
            input_data = batch["input"]
            
            if torch.isnan(input_data).any():
                numerical_info["has_nan_input"] = True
                numerical_info["nan_count"] += torch.isnan(input_data).sum().item()
            
            if torch.isinf(input_data).any():
                numerical_info["has_inf_input"] = True
                numerical_info["inf_count"] += torch.isinf(input_data).sum().item()
            
            with torch.no_grad():
                output = model(input_data)
                
                if torch.isnan(output).any():
                    numerical_info["has_nan_output"] = True
                
                if torch.isinf(output).any():
                    numerical_info["has_inf_output"] = True
        
        return numerical_info
    
    def diagnose_training_curves(self, model: nn.Module, data_loader) -> Dict:
        """诊断训练曲线"""
        training_info = {
            "loss_history": [],
            "learning_rate_history": [],
            "has_converged": False,
            "convergence_rate": 0.0
        }
        
        # 记录训练曲线
        for epoch in range(self.config.get("num_epochs", 10)):
            epoch_loss = 0.0
            num_batches = 0
            
            for batch in data_loader:
                input_data = batch["input"]
                target = batch["target"]
                
                with torch.no_grad():
                    output = model(input_data)
                    loss = nn.MSELoss()(output, target)
                
                epoch_loss += loss.item()
                num_batches += 1
            
            avg_loss = epoch_loss / num_batches
            training_info["loss_history"].append(avg_loss)
        
        # 分析收敛情况
        if len(training_info["loss_history"]) > 1:
            last_loss = training_info["loss_history"][-1]
            first_loss = training_info["loss_history"][0]
            
            if last_loss < first_loss * 0.9:
                training_info["has_converged"] = True
                training_info["convergence_rate"] = (first_loss - last_loss) / first_loss
        
        return training_info
    
    def diagnose_memory_leaks(self, model: nn.Module) -> Dict:
        """诊断内存泄漏"""
        memory_info = {
            "initial_memory": torch.cuda.memory_allocated(),
            "current_memory": 0,
            "memory_growth_rate": 0.0,
            "has_memory_leak": False
        }
        
        # 记录内存使用
        for epoch in range(self.config.get("num_epochs", 10)):
            torch.cuda.reset_peak_memory_stats()
            
            for batch in data_loader:
                input_data = batch["input"]
                
                with torch.no_grad():
                    output = model(input_data)
            
            memory_info["current_memory"] = torch.cuda.memory_allocated()
        
        # 分析内存增长
        if memory_info["current_memory"] > memory_info["initial_memory"] * 1.1:
            memory_info["has_memory_leak"] = True
            memory_info["memory_growth_rate"] = (memory_info["current_memory"] - memory_info["initial_memory"]) / memory_info["initial_memory"]
        
        return memory_info


if __name__ == '__main__':
    # 使用示例
    debugger = ModelDebugger(model, config)
    
    # 诊断梯度
    gradient_info = debugger.diagnose_gradients(model)
    
    # 诊断数值异常
    numerical_info = debugger.diagnose_numerical_issues(model, data_loader)
    
    # 诊断训练曲线
    training_info = debugger.diagnose_training_curves(model, data_loader)
    
    # 诊断内存泄漏
    memory_info = debugger.diagnose_memory_leaks(model)
```

### 训练调试代码模板

```python
"""
Debugger - 训练调试

任务描述：{任务描述}
调试类型：{调试类型}
"""

import torch
import torch.nn as nn
from typing import Dict, List, Tuple
import logging


class TrainingDebugger:
    """
    训练调试类
    
    功能：
    - 前向传播调试
    - 反向传播调试
    - 损失函数调试
    - 梯度调试
    """
    
    def __init__(self, model: nn.Module, config: Dict):
        self.model = model
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def debug_forward(self, model: nn.Module, data_loader) -> Dict:
        """调试前向传播"""
        forward_info = {
            "input_shapes": [],
            "output_shapes": [],
            "forward_time": [],
            "has_nan_forward": False,
            "has_inf_forward": False
        }
        
        for batch in data_loader:
            input_data = batch["input"]
            
            # 记录输入形状
            forward_info["input_shapes"].append(input_data.shape)
            
            # 前向传播
            start_time = torch.cuda.Event(enable_timing=True)
            end_time = torch.cuda.Event(enable_timing=True)
            
            start_time.record()
            
            with torch.no_grad():
                output = model(input_data)
            
            end_time.record()
            torch.cuda.synchronize()
            
            forward_time = start_time.elapsed_time(end_time)
            forward_info["forward_time"].append(forward_time)
            
            # 记录输出形状
            forward_info["output_shapes"].append(output.shape)
            
            # 检测数值异常
            if torch.isnan(output).any():
                forward_info["has_nan_forward"] = True
                self.logger.warning("NaN detected in forward pass")
            
            if torch.isinf(output).any():
                forward_info["has_inf_forward"] = True
                self.logger.warning("Inf detected in forward pass")
        
        return forward_info
    
    def debug_backward(self, model: nn.Module, data_loader, criterion) -> Dict:
        """调试反向传播"""
        backward_info = {
            "backward_time": [],
            "has_nan_backward": False,
            "has_inf_backward": False
        }
        
        for batch in data_loader:
            input_data = batch["input"]
            target = batch["target"]
            
            # 前向传播
            output = model(input_data)
            loss = criterion(output, target)
            
            # 反向传播
            start_time = torch.cuda.Event(enable_timing=True)
            end_time = torch.cuda.Event(enable_timing=True)
            
            start_time.record()
            
            loss.backward()
            
            end_time.record()
            torch.cuda.synchronize()
            
            backward_time = start_time.elapsed_time(end_time)
            backward_info["backward_time"].append(backward_time)
            
            # 清空梯度
            model.zero_grad()
        
        return backward_info
    
    def debug_loss(self, model: nn.Module, data_loader, criterion) -> Dict:
        """调试损失函数"""
        loss_info = {
            "loss_values": [],
            "loss_mean": 0.0,
            "loss_std": 0.0,
            "has_nan_loss": False,
            "has_inf_loss": False
        }
        
        for batch in data_loader:
            input_data = batch["input"]
            target = batch["target"]
            
            # 前向传播
            output = model(input_data)
            loss = criterion(output, target)
            
            # 记录损失值
            loss_info["loss_values"].append(loss.item())
            
            # 检测数值异常
            if torch.isnan(loss):
                loss_info["has_nan_loss"] = True
                self.logger.warning("NaN detected in loss")
            
            if torch.isinf(loss):
                loss_info["has_inf_loss"] = True
                self.logger.warning("Inf detected in loss")
        
        # 计算损失统计
        loss_values = np.array(loss_info["loss_values"])
        loss_info["loss_mean"] = np.mean(loss_values)
        loss_info["loss_std"] = np.std(loss_values)
        
        return loss_info
    
    def debug_gradients(self, model: nn.Module, data_loader, criterion) -> Dict:
        """调试梯度"""
        gradient_info = {
            "grad_norms": [],
            "grad_mean": [],
            "grad_std": [],
            "has_nan_gradient": False,
            "has_inf_gradient": False
        }
        
        for batch in data_loader:
            input_data = batch["input"]
            target = batch["target"]
            
            # 前向传播
            output = model(input_data)
            loss = criterion(output, target)
            
            # 反向传播
            loss.backward()
            
            # 记录梯度
            grad_norms = []
            grad_means = []
            grad_stds = []
            
            for name, param in model.named_parameters():
                if param.grad is not None:
                    grad = param.grad.data
                    grad_norms.append(grad.norm().item())
                    grad_means.append(grad.mean().item())
                    grad_stds.append(grad.std().item())
                    
                    # 检测数值异常
                    if torch.isnan(grad).any():
                        gradient_info["has_nan_gradient"] = True
                        self.logger.warning(f"NaN detected in gradient: {name}")
                    
                    if torch.isinf(grad).any():
                        gradient_info["has_inf_gradient"] = True
                        self.logger.warning(f"Inf detected in gradient: {name}")
            
            gradient_info["grad_norms"].append(np.mean(grad_norms))
            gradient_info["grad_mean"].append(np.mean(grad_means))
            gradient_info["grad_std"].append(np.mean(grad_stds))
            
            # 清空梯度
            model.zero_grad()
        
        return gradient_info


if __name__ == '__main__':
    # 使用示例
    debugger = TrainingDebugger(model, config)
    
    # 调试前向传播
    forward_info = debugger.debug_forward(model, data_loader)
    
    # 调试反向传播
    backward_info = debugger.debug_backward(model, data_loader, criterion)
    
    # 调试损失函数
    loss_info = debugger.debug_loss(model, data_loader, criterion)
    
    # 调试梯度
    gradient_info = debugger.debug_gradients(model, data_loader, criterion)
```

### 性能分析代码模板

```python
"""
Debugger - 性能分析

任务描述：{任务描述}
分析类型：{分析类型}
"""

import torch
import torch.nn as nn
import time
from typing import Dict, List, Tuple


class PerformanceAnalyzer:
    """
    性能分析类
    
    功能：
    - 计算性能分析
    - 内存性能分析
    - 数据加载性能分析
    - I/O 性能分析
    """
    
    def __init__(self, model: nn.Module, config: Dict):
        self.model = model
        self.config = config
    
    def analyze_compute_performance(self, model: nn.Module) -> Dict:
        """分析计算性能"""
        compute_info = {
            "flops": 0,
            "params": 0,
            "inference_time": 0.0,
            "training_time": 0.0
        }
        
        # 计算 FLOPS
        input_data = torch.randn(1, 3, 721, 1440)
        compute_info["flops"] = self._calculate_flops(model, input_data)
        
        # 计算参数量
        compute_info["params"] = sum(p.numel() for p in model.parameters())
        
        # 测量推理时间
        start_time = time.time()
        with torch.no_grad():
            output = model(input_data)
        end_time = time.time()
        compute_info["inference_time"] = end_time - start_time
        
        # 测量训练时间
        start_time = time.time()
        output = model(input_data)
        loss = nn.MSELoss()(output, input_data)
        loss.backward()
        end_time = time.time()
        compute_info["training_time"] = end_time - start_time
        
        return compute_info
    
    def analyze_memory_performance(self, model: nn.Module) -> Dict:
        """分析内存性能"""
        memory_info = {
            "model_memory": 0,
            "activation_memory": 0,
            "total_memory": 0,
            "memory_per_batch": 0
        }
        
        # 计算模型内存
        memory_info["model_memory"] = sum(p.numel() * p.element_size() for p in model.parameters())
        
        # 计算激活内存
        input_data = torch.randn(1, 3, 721, 1440)
        with torch.no_grad():
            output = model(input_data)
        
        memory_info["activation_memory"] = output.numel() * output.element_size()
        
        # 计算总内存
        memory_info["total_memory"] = memory_info["model_memory"] + memory_info["activation_memory"]
        
        # 计算每批次内存
        memory_info["memory_per_batch"] = memory_info["total_memory"] * self.config.get("batch_size", 1)
        
        return memory_info
    
    def analyze_dataloader_performance(self, data_loader) -> Dict:
        """分析数据加载性能"""
        dataloader_info = {
            "num_workers": data_loader.num_workers,
            "pin_memory": data_loader.pin_memory,
            "avg_load_time": 0.0,
            "bottleneck": ""
        }
        
        # 测量数据加载时间
        load_times = []
        for batch in data_loader:
            start_time = time.time()
            # 加载数据
            input_data = batch["input"]
            end_time = time.time()
            load_times.append(end_time - start_time)
        
        dataloader_info["avg_load_time"] = np.mean(load_times)
        
        # 分析瓶颈
        if dataloader_info["avg_load_time"] > 0.1:
            dataloader_info["bottleneck"] = "data_loading"
        else:
            dataloader_info["bottleneck"] = "none"
        
        return dataloader_info
    
    def analyze_io_performance(self, data_loader) -> Dict:
        """分析 I/O 性能"""
        io_info = {
            "data_path": "",
            "file_format": "",
            "avg_read_time": 0.0,
            "bottleneck": ""
        }
        
        # 测量数据读取时间
        read_times = []
        for batch in data_loader:
            start_time = time.time()
            # 读取数据
            input_data = batch["input"]
            end_time = time.time()
            read_times.append(end_time - start_time)
        
        io_info["avg_read_time"] = np.mean(read_times)
        
        # 分析瓶颈
        if io_info["avg_read_time"] > 0.1:
            io_info["bottleneck"] = "io"
        else:
            io_info["bottleneck"] = "none"
        
        return io_info


if __name__ == '__main__':
    # 使用示例
    analyzer = PerformanceAnalyzer(model, config)
    
    # 分析计算性能
    compute_info = analyzer.analyze_compute_performance(model)
    
    # 分析内存性能
    memory_info = analyzer.analyze_memory_performance(model)
    
    # 分析数据加载性能
    dataloader_info = analyzer.analyze_dataloader_performance(data_loader)
    
    # 分析 I/O 性能
    io_info = analyzer.analyze_io_performance(data_loader)
```

## 最佳实践

### 1. 模型诊断最佳实践

```python
# 模型诊断最佳实践
def model_diagnosis_best_practices(model: nn.Module, data_loader: DataLoader, config: Dict) -> Dict:
    # 1. 诊断梯度
    gradient_info = diagnose_gradients(model)
    
    # 2. 诊断数值异常
    numerical_info = diagnose_numerical_issues(model, data_loader)
    
    # 3. 诊断训练曲线
    training_info = diagnose_training_curves(model, data_loader)
    
    # 4. 诊断内存泄漏
    memory_info = diagnose_memory_leaks(model)
    
    return {
        "gradient_info": gradient_info,
        "numerical_info": numerical_info,
        "training_info": training_info,
        "memory_info": memory_info
    }
```

### 2. 训练调试最佳实践

```python
# 训练调试最佳实践
def training_debugging_best_practices(model: nn.Module, data_loader: DataLoader, criterion: nn.Module) -> Dict:
    # 1. 调试前向传播
    forward_info = debug_forward(model, data_loader)
    
    # 2. 调试反向传播
    backward_info = debug_backward(model, data_loader, criterion)
    
    # 3. 调试损失函数
    loss_info = debug_loss(model, data_loader, criterion)
    
    # 4. 调试梯度
    gradient_info = debug_gradients(model, data_loader, criterion)
    
    return {
        "forward_info": forward_info,
        "backward_info": backward_info,
        "loss_info": loss_info,
        "gradient_info": gradient_info
    }
```

### 3. 性能分析最佳实践

```python
# 性能分析最佳实践
def performance_analysis_best_practices(model: nn.Module, data_loader: DataLoader, config: Dict) -> Dict:
    # 1. 分析计算性能
    compute_info = analyze_compute_performance(model)
    
    # 2. 分析内存性能
    memory_info = analyze_memory_performance(model)
    
    # 3. 分析数据加载性能
    dataloader_info = analyze_dataloader_performance(data_loader)
    
    # 4. 分析 I/O 性能
    io_info = analyze_io_performance(data_loader)
    
    return {
        "compute_info": compute_info,
        "memory_info": memory_info,
        "dataloader_info": dataloader_info,
        "io_info": io_info
    }
```

## 错误处理

### 常见错误 1：梯度爆炸

**错误**：梯度爆炸

**解决**：使用梯度裁剪

```python
# 梯度裁剪
def gradient_clipping(model: nn.Module, max_norm: float = 1.0):
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)
```

### 常见错误 2：数值异常

**错误**：数值异常（NaN/Inf）

**解决**：使用数值稳定性技术

```python
# 数值稳定性技术
def numerical_stability(model: nn.Module):
    # 添加小的 epsilon
    model.epsilon = 1e-8
    
    # 使用数值稳定的函数
    model.softmax = nn.Softmax(dim=-1)
    model.sigmoid = nn.Sigmoid()
```

### 常见错误 3：性能瓶颈

**错误**：性能瓶颈

**解决**：使用性能分析工具

```python
# 性能分析工具
def performance_analysis(model: nn.Module, data_loader):
    # 分析计算性能
    compute_info = analyze_compute_performance(model)
    
    # 分析内存性能
    memory_info = analyze_memory_performance(model)
    
    # 分析数据加载性能
    dataloader_info = analyze_dataloader_performance(data_loader)
    
    # 分析 I/O 性能
    io_info = analyze_io_performance(data_loader)
    
    return {
        "compute_info": compute_info,
        "memory_info": memory_info,
        "dataloader_info": dataloader_info,
        "io_info": io_info
    }
```

## 总结

本技能提供了诊断层的完整解决方案：

- ✅ **模型诊断**：多种诊断方式
- ✅ **训练调试**：多种调试方式
- ✅ **性能分析**：多种分析方式
- ✅ **错误处理**：完善的错误处理机制
- ✅ **最佳实践**：遵循领域最佳实践

通过本技能，用户可以快速完成诊断层任务。
