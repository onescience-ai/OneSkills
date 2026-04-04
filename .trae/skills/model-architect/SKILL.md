---
name: model-architect
description: 模型层技能，负责模型搭建、修改、创新和论文复现
---

# Skill: model-architect

## 能力描述

本技能负责 AI4S Pipeline 的模型层任务，包括模型搭建、模型修改、模型创新和论文复现。基于 OneScience 组件库和构建的知识体系，提供完整的模型架构解决方案。

## 核心能力

### 1. 模型搭建

支持多种模型搭建方式：

| 搭建方式 | 支持情况 | 说明 |
|---------|---------|------|
| 快速搭建 | ✅ 完全支持 | 使用预定义模板 |
| 论文复现 | ✅ 完全支持 | 从论文中提取结构 |
| 自定义搭建 | ✅ 完全支持 | 完全自定义架构 |
| 组合搭建 | ✅ 完全支持 | 组合多个组件 |

### 2. 模型修改

支持多种模型修改方式：

| 修改方式 | 支持情况 | 说明 |
|---------|---------|------|
| 组件替换 | ✅ 完全支持 | 替换模型组件 |
| 结构修改 | ✅ 完全支持 | 修改模型结构 |
| 参数调整 | ✅ 完全支持 | 调整模型参数 |
| 维度适配 | ✅ 完全支持 | 适配不同维度 |

### 3. 模型创新

支持多种模型创新方式：

| 创新方式 | 支持情况 | 说明 |
|---------|---------|------|
| 架构创新 | ✅ 完全支持 | 设计新架构 |
| 组件创新 | ✅ 完全支持 | 设计新组件 |
| 融合创新 | ✅ 完全支持 | 融合多个架构 |
| 物理约束 | ✅ 完全支持 | 添加物理约束 |

### 4. 论文复现

支持多种论文复现方式：

| 复现方式 | 支持情况 | 说明 |
|---------|---------|------|
| 结构提取 | ✅ 完全支持 | 从论文中提取结构 |
| 组件映射 | ✅ 完全支持 | 映射到 OneScience 组件 |
| 参数还原 | ✅ 完全支持 | 还原论文参数 |
| 验证复现 | ✅ 完全支持 | 验证复现效果 |

## 使用方法

### 场景 1：模型快速搭建

**用户需求**：快速搭建 Pangu-Weather 模型。

**Prompt**：
```
基于./oneskills/trae/task/react_prompt.md中的工作流执行以下任务：
快速搭建 Pangu-Weather 模型，要求：
1. 使用 OneScience 组件
2. 实现 Encoder-Processor-Decoder 架构
3. 生成配置文件
4. 保存至 pangu_weather.py
```

**输出**：模型代码和配置文件

### 场景 2：模型修改

**用户需求**：将 Pangu-Weather 模型中的 Swin-Transformer Fuser 替换为 AFNO。

**Prompt**：
```
基于./oneskills/trae/task/react_prompt.md中的工作流执行以下任务：
将 Pangu-Weather 模型中的 Swin-Transformer Fuser 替换为 FourCastNet 的 AFNO 模块，要求：
1. 设计维度适配器
2. 实现组件替换
3. 生成完整模型代码
4. 保存至 hybrid_pangu_afno.py
```

**输出**：修改后的模型代码

### 场景 3：模型创新

**用户需求**：在 GraphCast 基础上创新设计多尺度融合模型。

**Prompt**：
```
基于./oneskills/trae/task/react_prompt.md中的工作流执行以下任务：
在 GraphCast 基础上创新设计多尺度融合模型，要求：
1. 保留 GraphCast 的图神经网络架构
2. 添加多尺度特征融合模块
3. 支持全球-区域嵌套建模
4. 保存至 multiscale_graphcast.py
```

**输出**：创新模型代码

### 场景 4：论文复现

**用户需求**：复现 GraphCast 论文。

**Prompt**：
```
基于./oneskills/trae/task/react_prompt.md中的工作流执行以下任务：
复现 GraphCast 论文中的模型架构，要求：
1. 从论文中提取 Encoder-Processor-Decoder 架构
2. 使用 OneScience 组件实现
3. 实现多尺度消息传递
4. 保存至 graphcast_reproduction.py
```

**输出**：论文复现代码

## 核心规则

### 1. 组件导入规范（强制）

所有组件必须通过 `onescience.modules` 统一导入：

```python
# ✅ 正确示例
from onescience.modules import (
    PanguEmbedding2D,
    EarthTransformer2DBlock,
    PanguDownSample3D
)

# ❌ 错误示例
from onescience.models.module import Module
```

### 2. 模型搭建流程规范（强制）

模型搭建必须遵循以下流程：

```python
# 模型搭建流程
def model_building_pipeline(config):
    # 1. 组件选择
    components = select_components(config)
    
    # 2. 架构设计
    architecture = design_architecture(components)
    
    # 3. 参数配置
    parameters = configure_parameters(architecture)
    
    # 4. 模型实例化
    model = instantiate_model(parameters)
    
    # 5. 验证模型
    validate_model(model)
    
    return model
```

### 3. 组件替换规范（强制）

组件替换必须遵循以下规范：

```python
# 组件替换规范
def component_replacement(model, old_component, new_component):
    # 1. 维度分析
    old_dim = analyze_dimension(old_component)
    new_dim = analyze_dimension(new_component)
    
    # 2. 维度适配
    if old_dim != new_dim:
        adapter = create_adapter(old_dim, new_dim)
    else:
        adapter = nn.Identity()
    
    # 3. 组件替换
    replace_component(model, old_component, new_component, adapter)
    
    return model
```

## 输出格式

### 模型代码模板

```python
"""
Model Architect - 模型搭建

任务描述：{任务描述}
模型类型：{模型类型}
架构：{架构描述}
"""

import torch
import torch.nn as nn
from typing import Dict, List, Tuple

from onescience.modules import Component1, Component2, Component3


class TargetModel(nn.Module):
    """
    目标模型描述
    
    架构：
    - Encoder: ...
    - Processor: ...
    - Decoder: ...
    
    组件：
    - Component1: ...
    - Component2: ...
    - Component3: ...
    """
    
    def __init__(self, config: Dict):
        super().__init__()
        self.config = config
        
        # Encoder
        self.encoder = self._build_encoder()
        
        # Processor
        self.processor = self._build_processor()
        
        # Decoder
        self.decoder = self._build_decoder()
    
    def _build_encoder(self) -> nn.Module:
        """构建编码器"""
        encoder = Component1(**self.config["encoder"])
        return encoder
    
    def _build_processor(self) -> nn.Module:
        """构建处理器"""
        processor = Component2(**self.config["processor"])
        return processor
    
    def _build_decoder(self) -> nn.Module:
        """构建解码器"""
        decoder = Component3(**self.config["decoder"])
        return decoder
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """前向传播"""
        # Encoder
        x = self.encoder(x)
        
        # Processor
        x = self.processor(x)
        
        # Decoder
        x = self.decoder(x)
        
        return x


if __name__ == '__main__':
    # 使用示例
    config = {
        "encoder": {...},
        "processor": {...},
        "decoder": {...}
    }
    
    model = TargetModel(config)
    x = torch.randn(1, 3, 721, 1440)
    output = model(x)
    print(f'Output shape: {output.shape}')
```

### 组件替换代码模板

```python
"""
Model Architect - 组件替换

任务描述：{任务描述}
替换组件：{替换组件}
新组件：{新组件}
"""

import torch
import torch.nn as nn
from typing import Dict, List, Tuple

from onescience.modules import OldComponent, NewComponent


class ComponentReplacer:
    """
    组件替换类
    
    功能：
    - 维度分析
    - 维度适配
    - 组件替换
    """
    
    def __init__(self, config: Dict):
        self.config = config
    
    def analyze_dimension(self, component: nn.Module) -> Dict:
        """分析组件维度"""
        # 分析输入输出维度
        input_dim = self._get_input_dim(component)
        output_dim = self._get_output_dim(component)
        
        return {
            "input_dim": input_dim,
            "output_dim": output_dim
        }
    
    def create_adapter(self, old_dim: Dict, new_dim: Dict) -> nn.Module:
        """创建维度适配器"""
        if old_dim == new_dim:
            return nn.Identity()
        
        adapter = nn.Sequential(
            nn.Linear(old_dim["output_dim"], new_dim["input_dim"]),
            nn.LayerNorm(new_dim["input_dim"])
        )
        
        return adapter
    
    def replace_component(self, model: nn.Module, old_component: str, new_component: str, adapter: nn.Module) -> nn.Module:
        """替换组件"""
        # 获取旧组件
        old_module = self._get_module(model, old_component)
        
        # 获取新组件
        new_module = self._get_module(model, new_component)
        
        # 替换组件
        if adapter is not None:
            # 使用适配器
            new_module = nn.Sequential(adapter, new_module)
        
        # 替换
        self._set_module(model, old_component, new_module)
        
        return model


if __name__ == '__main__':
    # 使用示例
    replacer = ComponentReplacer(config)
    
    # 分析维度
    old_dim = replacer.analyze_dimension(old_component)
    new_dim = replacer.analyze_dimension(new_component)
    
    # 创建适配器
    adapter = replacer.create_adapter(old_dim, new_dim)
    
    # 替换组件
    model = replacer.replace_component(model, old_component, new_component, adapter)
```

### 模型创新代码模板

```python
"""
Model Architect - 模型创新

任务描述：{任务描述}
创新点：{创新点}
"""

import torch
import torch.nn as nn
from typing import Dict, List, Tuple

from onescience.modules import BaseComponent, NewComponent


class InnovativeModel(nn.Module):
    """
    创新模型描述
    
    架构：
    - Encoder: ...
    - Processor: ...
    - Decoder: ...
    
    创新点：
    - 新组件：...
    - 新架构：...
    """
    
    def __init__(self, config: Dict):
        super().__init__()
        self.config = config
        
        # 基础组件
        self.base_encoder = BaseComponent(**config["base_encoder"])
        self.base_processor = BaseComponent(**config["base_processor"])
        self.base_decoder = BaseComponent(**config["base_decoder"])
        
        # 创新组件
        self.innovative_component = NewComponent(**config["innovative_component"])
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """前向传播"""
        # 基础处理
        x = self.base_encoder(x)
        x = self.base_processor(x)
        
        # 创新处理
        x = self.innovative_component(x)
        
        # 基础解码
        x = self.base_decoder(x)
        
        return x


if __name__ == '__main__':
    # 使用示例
    config = {
        "base_encoder": {...},
        "base_processor": {...},
        "base_decoder": {...},
        "innovative_component": {...}
    }
    
    model = InnovativeModel(config)
    x = torch.randn(1, 3, 721, 1440)
    output = model(x)
    print(f'Output shape: {output.shape}')
```

### 论文复现代码模板

```python
"""
Model Architect - 论文复现

任务描述：{任务描述}
论文标题：{论文标题}
复现内容：{复现内容}
"""

import torch
import torch.nn as nn
from typing import Dict, List, Tuple

from onescience.modules import Component1, Component2, Component3


class PaperReproductionModel(nn.Module):
    """
    论文复现模型
    
    论文标题：{论文标题}
    架构：{架构描述}
    组件：{组件列表}
    """
    
    def __init__(self, config: Dict):
        super().__init__()
        self.config = config
        
        # 从论文中提取的组件
        self.component1 = Component1(**config["component1"])
        self.component2 = Component2(**config["component2"])
        self.component3 = Component3(**config["component3"])
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """前向传播"""
        # 论文中的前向传播逻辑
        x = self.component1(x)
        x = self.component2(x)
        x = self.component3(x)
        
        return x


if __name__ == '__main__':
    # 使用示例
    config = {
        "component1": {...},
        "component2": {...},
        "component3": {...}
    }
    
    model = PaperReproductionModel(config)
    x = torch.randn(1, 3, 721, 1440)
    output = model(x)
    print(f'Output shape: {output.shape}')
```

## 最佳实践

### 1. 模型搭建最佳实践

```python
# 模型搭建最佳实践
def model_building_best_practices(config: Dict) -> nn.Module:
    # 1. 组件选择
    components = select_components(config)
    
    # 2. 架构设计
    architecture = design_architecture(components)
    
    # 3. 参数配置
    parameters = configure_parameters(architecture)
    
    # 4. 模型实例化
    model = instantiate_model(parameters)
    
    # 5. 验证模型
    validate_model(model)
    
    return model
```

### 2. 组件替换最佳实践

```python
# 组件替换最佳实践
def component_replacement_best_practices(model: nn.Module, old_component: str, new_component: str) -> nn.Module:
    # 1. 维度分析
    old_dim = analyze_dimension(old_component)
    new_dim = analyze_dimension(new_component)
    
    # 2. 维度适配
    if old_dim != new_dim:
        adapter = create_adapter(old_dim, new_dim)
    else:
        adapter = nn.Identity()
    
    # 3. 组件替换
    replace_component(model, old_component, new_component, adapter)
    
    # 4. 验证替换结果
    validate_replaced_model(model)
    
    return model
```

### 3. 模型创新最佳实践

```python
# 模型创新最佳实践
def model_innovation_best_practices(base_model: nn.Module,创新组件: nn.Module) -> nn.Module:
    # 1. 分析基础模型
    analyze_base_model(base_model)
    
    # 2. 设计创新点
    design_innovation(创新组件)
    
    # 3. 实现创新模型
    innovative_model = implement_innovation(base_model, 创新组件)
    
    # 4. 验证创新效果
    validate_innovation(innovative_model)
    
    return innovative_model
```

## 错误处理

### 常见错误 1：组件维度不匹配

**错误**：组件维度不匹配

**解决**：使用维度适配器

```python
# 维度适配器
def dimension_adapter(old_dim: Dict, new_dim: Dict) -> nn.Module:
    if old_dim == new_dim:
        return nn.Identity()
    
    adapter = nn.Sequential(
        nn.Linear(old_dim["output_dim"], new_dim["input_dim"]),
        nn.LayerNorm(new_dim["input_dim"])
    )
    
    return adapter
```

### 常见错误 2：组件替换失败

**错误**：组件替换失败

**解决**：使用组件替换工作流

```python
# 组件替换工作流
def component_replacement_workflow(model: nn.Module, old_component: str, new_component: str) -> nn.Module:
    # 1. 分析维度
    old_dim = analyze_dimension(old_component)
    new_dim = analyze_dimension(new_component)
    
    # 2. 创建适配器
    if old_dim != new_dim:
        adapter = create_adapter(old_dim, new_dim)
    else:
        adapter = nn.Identity()
    
    # 3. 替换组件
    replace_component(model, old_component, new_component, adapter)
    
    # 4. 验证替换结果
    validate_replaced_model(model)
    
    return model
```

### 常见错误 3：论文复现效果不佳

**错误**：论文复现效果不佳

**解决**：使用论文复现验证流程

```python
# 论文复现验证流程
def paper_reproduction_validation_workflow(config: Dict) -> nn.Module:
    # 1. 结构提取
    architecture = extract_architecture_from_paper(config["paper"])
    
    # 2. 组件映射
    components = map_components_to_onescience(architecture)
    
    # 3. 参数还原
    parameters = restore_parameters_from_paper(config["paper"])
    
    # 4. 模型实例化
    model = instantiate_model(components, parameters)
    
    # 5. 验证复现效果
    validate_reproduction(model, config["paper"])
    
    return model
```

## 总结

本技能提供了模型层的完整解决方案：

- ✅ **模型搭建**：多种搭建方式
- ✅ **模型修改**：多种修改方式
- ✅ **模型创新**：多种创新方式
- ✅ **论文复现**：完整的复现流程
- ✅ **错误处理**：完善的错误处理机制
- ✅ **最佳实践**：遵循领域最佳实践

通过本技能，用户可以快速完成模型层任务。
