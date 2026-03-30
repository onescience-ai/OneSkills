component:

  meta:
    name: OneEncoder
    alias: Unified Encoder Interface
    version: 1.0
    domain: deep_learning
    category: neural_network
    subcategory: encoder_factory
    author: OneScience
    license: Apache-2.0
    tags:
      - encoder
      - factory_pattern
      - unified_interface
      - modular_design
      - encoder_registry

  concept:

    description: >
      OneEncoder是统一的编码器接口模块，采用工厂模式设计，提供对不同编码器实现的统一访问。
      通过注册表机制管理多种编码器类型，包括UNet系列、GraphViT、MeshGraph、FengWu等，
      支持通过style参数动态选择具体的编码器实现，并提供了特殊的state_dict加载机制。

    intuition: >
      就像通用编码器设备：一个设备可以处理不同类型的编码任务（图像、时序、图数据等），
      只需选择对应的编码模式（style），设备就会自动调用相应的编码算法。OneEncoder就是这样一个"通用编码器"。

    problem_it_solves:
      - 多种编码器实现的统一管理
      - 动态编码器选择和切换
      - 模块化设计中的接口统一
      - 模型加载时的键名前缀处理

  theory:

    formula:

      factory_pattern:
        expression: |
          \text{encoder} = \text{OneEncoder}(\text{style}, \text{**kwargs})
          \text{output} = \text{encoder}(\text{*args}, \text{**kwargs})

      state_dict_mapping:
        expression: |
          \text{new\_state}[k'] = v \quad \text{where } k' = \text{'encoder.'} + k

    variables:

      style:
        name: EncoderStyle
        description: 编码器类型标识符

      kwargs:
        name: EncoderParameters
        description: 传递给具体编码器的参数

  structure:

    architecture: factory_pattern_interface

    pipeline:

      - name: StyleValidation
        operation: check_style_in_registry

      - name: EncoderInstantiation
        operation: create_specific_encoder

      - name: ForwardDelegation
        operation: delegate_to_concrete_encoder

      - name: StateDictMapping
        operation: load_state_dict_with_prefix

      - name: AttributeDelegation
        operation: attribute_access_forwarding

  interface:

    parameters:

      style:
        type: str
        description: 编码器类型，可选值见ENCODER_REGISTRY

      kwargs:
        type: dict
        description: 传递给具体编码器的参数

    available_styles:

      UNetEncoder1D:
        description: 一维U-Net编码器

      UNetEncoder2D:
        description: 二维U-Net编码器

      UNetEncoder3D:
        description: 三维U-Net编码器

      GraphViTEncoder:
        description: GraphViT编码器

      MeshGraphEncoder:
        description: MeshGraph编码器

      FengWuEncoder:
        description: FengWu气象编码器

    inputs:

      args:
        type: variadic
        description: 传递给具体编码器的位置参数

      kwargs:
        type: variadic
        description: 传递给具体编码器的关键字参数

    outputs:

      output:
        type: encoder_output
        description: 具体编码器的输出

  types:

    EncoderRegistry:
      description: 编码器注册表，映射style到具体实现类

  implementation:

    framework: pytorch

    code: |

      import torch
      from torch import nn
      from .unet_encoder import UNetEncoder1D, UNetEncoder2D, UNetEncoder3D
      from .graphvit_encoder import GraphViTEncoder
      from .mesh_graph_encoder import MeshGraphEncoder
      from .fengwuencoder import FengWuEncoder

      _ENCODER_REGISTRY = {
          "UNetEncoder1D": UNetEncoder1D,
          "UNetEncoder2D": UNetEncoder2D,
          "UNetEncoder3D": UNetEncoder3D,
          "GraphViTEncoder": GraphViTEncoder,
          "MeshGraphEncoder": MeshGraphEncoder,
          "FengWuEncoder": FengWuEncoder,
      }

      class OneEncoder(nn.Module):
          def __init__(self, style: str, **kwargs):
              super().__init__()
              
              if style not in _ENCODER_REGISTRY:
                  raise NotImplementedError(
                      f"Unknown style: '{style}'. Available options are: {list(_ENCODER_REGISTRY.keys())}"
                  )
              
              self.encoder = _ENCODER_REGISTRY[style](**kwargs)

          def forward(self, *args, **kwargs):
              return self.encoder(*args, **kwargs)

          def load_state_dict(self, state_dict, strict=True):
              # 处理state_dict键名前缀
              new_state = {'encoder.' + k: v for k, v in state_dict.items()}
              return super().load_state_dict(new_state, strict=strict)
          
          def __getattr__(self, name):
              try:
                  return super().__getattr__(name)
              except AttributeError:
                  return getattr(self.encoder, name)

  skills:

    build_unified_encoder:

      description: 构建统一编码器接口

      inputs:
        - style
        - encoder_parameters

      prompt_template: |

        构建OneEncoder统一接口，支持多种编码器类型。

        参数：
        style = {{style}}
        encoder_parameters = {{encoder_parameters}}

        要求：
        1. 支持动态编码器选择
        2. 统一的前向传播接口
        3. state_dict键名前缀处理
        4. 属性访问转发

    manage_encoder_registry:

      description: 管理编码器注册表

      checks:
        - style_availability (检查style是否可用)
        - parameter_compatibility (参数兼容性)
        - state_dict_compatibility (状态字典兼容性)

  knowledge:

    usage_patterns:

      dynamic_encoder_selection:

        pipeline:
          - Config: 配置文件指定encoder类型
          - Factory: OneEncoder工厂创建实例
          - Usage: 统一接口调用
          - Loading: 特殊的state_dict处理

      modular_architecture:

        pipeline:
          - Registry: 编码器注册表
          - Interface: 统一访问接口
          - Implementation: 具体编码器实现
          - Integration: 系统集成

    hot_models:

      - model: Factory Pattern
        year: 1994
        role: 设计模式经典实现
        architecture: creational pattern

      - model: Registry Pattern
        year: 1990s
        role: 组件注册和管理
        architecture: behavioral pattern

    best_practices:

      - 保持接口的一致性和简洁性
      - 提供清晰的错误信息
      - 正确处理模型加载的键名映射
      - 维护完整的注册表文档

    anti_patterns:

      - 注册表不一致导致运行时错误
      - state_dict加载时键名不匹配
      - 接口设计过于复杂
      - 缺少适当的错误处理

    paper_references:

      - title: "Design Patterns: Elements of Reusable Object-Oriented Software"
        authors: Gamma et al.
        year: 1994

  graph:

    is_a:
      - FactoryModule
      - UnifiedInterface
      - NeuralNetworkWrapper

    part_of:
      - ModularArchitecture
      - EncoderSystem
      - ComponentRegistry

    depends_on:
      - UNetEncoder1D/2D/3D
      - GraphViTEncoder
      - MeshGraphEncoder
      - FengWuEncoder

    variants:
      - OneDecoder (解码器统一接口)
      - OneFuser (融合器统一接口)
      - OneMLP (MLP统一接口)

    used_in_models:
      - 模块化深度学习系统
      - 多模型集成框架
      - 动态模型选择系统

    compatible_with:

      inputs:
        - EncoderConfigurations
        - ModelParameters
        - InputData

      outputs:
        - EncoderResults
        - FeatureEmbeddings
        - CompressedRepresentations
