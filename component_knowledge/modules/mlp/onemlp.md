component:

  meta:
    name: OneMlp
    alias: Unified MLP Interface
    version: 1.0
    domain: deep_learning
    category: neural_network
    subcategory: mlp_factory
    author: OneScience
    license: Apache-2.0
    tags:
      - mlp
      - factory_pattern
      - unified_interface
      - modular_design
      - multi_layer_perceptron

  concept:

    description: >
      OneMlp是统一的多层感知机接口模块，采用工厂模式设计，提供对不同MLP实现的统一访问。
      通过注册表机制管理多种MLP类型，包括标准MLP、图神经网络MLP、群等变MLP、XiheMLP等，
      支持通过style参数动态选择具体的MLP实现。

    intuition: >
      就像通用处理器：一个设备可以执行不同类型的计算任务（标准MLP计算、图MLP计算、群等变计算等），
      只需选择对应的计算模式（style），设备就会自动调用相应的MLP算法。OneMlp就是这样一个"通用MLP处理器"。

    problem_it_solves:
      - 多种MLP实现的统一管理
      - 动态MLP选择和切换
      - 模块化设计中的接口统一
      - MLP算法的灵活配置

  theory:

    formula:

      factory_pattern:
        expression: |
          \text{mlp} = \text{OneMlp}(\text{style}, \text{**kwargs})
          \text{output} = \text{mlp}(\text{*args}, \text{**kwargs})

      registry_mechanism:
        expression: |
          \text{mlp} = \text{MLP\_REGISTRY}[\text{style}](\text{**kwargs})
          \text{if } \text{style} \notin \text{MLP\_REGISTRY}: \text{raise NotImplementedError}

    variables:

      style:
        name: MlpStyle
        description: MLP类型标识符

      kwargs:
        name: MlpParameters
        description: 传递给具体MLP的参数

  structure:

    architecture: factory_pattern_interface

    pipeline:

      - name: StyleValidation
        operation: check_style_in_registry

      - name: MlpInstantiation
        operation: create_specific_mlp

      - name: ForwardDelegation
        operation: delegate_to_concrete_mlp

  interface:

    parameters:

      style:
        type: str
        description: MLP类型，可选值见MLP_REGISTRY

      kwargs:
        type: dict
        description: 传递给具体MLP的参数

    available_styles:

      MeshGraphMLP:
        description: MeshGraph图神经网络MLP

      MeshGraphEdgeMLPConcat:
        description: MeshGraph边MLP（拼接版本）

      MeshGraphEdgeMLPSum:
        description: MeshGraph边MLP（求和版本）

      StandardMLP:
        description: 标准多层感知机

      SimpleMLP:
        description: 简化MLP

      DeepResMLP:
        description: 深度残差MLP

      RegularizedMLP:
        description: 正则化MLP

      LightweightMLP:
        description: 轻量级MLP

      GroupEquivariantMLP2d:
        description: 2D群等变MLP

      GroupEquivariantMLP3d:
        description: 3D群等变MLP

      XiheMlp:
        description: Xihe组传播MLP

    inputs:

      args:
        type: variadic
        description: 传递给具体MLP的位置参数

      kwargs:
        type: variadic
        description: 传递给具体MLP的关键字参数

    outputs:

      output:
        type: mlp_output
        description: 具体MLP的输出

  types:

    MlpRegistry:
      description: MLP注册表，映射style到具体实现类

  implementation:

    framework: pytorch

    code: |

      import torch
      from torch import nn
      from .mesh_graph_mlp import MeshGraphMLP, MeshGraphEdgeMLPConcat, MeshGraphEdgeMLPSum
      from .MLP import StandardMLP, SimpleMLP, DeepResMLP, RegularizedMLP, LightweightMLP
      from .GMLP import GroupEquivariantMLP2d, GroupEquivariantMLP3d
      from .xihemlp import XiheMlp

      _MLP_REGISTRY = {
          "MeshGraphMLP": MeshGraphMLP,
          "MeshGraphEdgeMLPConcat": MeshGraphEdgeMLPConcat,
          "MeshGraphEdgeMLPSum": MeshGraphEdgeMLPSum,
          "StandardMLP": StandardMLP,
          "SimpleMLP": SimpleMLP,
          "DeepResMLP": DeepResMLP,
          "RegularizedMLP": RegularizedMLP,
          "LightweightMLP": LightweightMLP,
          "GroupEquivariantMLP2d": GroupEquivariantMLP2d,
          "GroupEquivariantMLP3d": GroupEquivariantMLP3d,
          "XiheMlp": XiheMlp,
      }

      class OneMlp(nn.Module):
          def __init__(self, style: str, **kwargs):
              super().__init__()
              
              if style not in _MLP_REGISTRY:
                  raise NotImplementedError(f"Unknown style: {style}")
              
              # 使用 **kwargs 动态接收参数，避免硬编码
              self.mlp = _MLP_REGISTRY[style](**kwargs)
               
          def forward(self, *args, **kwargs): 
              return self.mlp(*args, **kwargs)

  skills:

    build_unified_mlp:

      description: 构建统一MLP接口

      inputs:
        - style
        - mlp_parameters

      prompt_template: |

        构建OneMlp统一接口，支持多种MLP类型。

        参数：
        style = {{style}}
        mlp_parameters = {{mlp_parameters}}

        要求：
        1. 支持动态MLP选择
        2. 统一的前向传播接口
        3. 参数动态透传
        4. 错误处理和验证

    manage_mlp_registry:

      description: 管理MLP注册表

      checks:
        - style_availability (检查style是否可用)
        - parameter_compatibility (参数兼容性)
        - interface_consistency (接口一致性)

  knowledge:

    usage_patterns:

      dynamic_mlp_selection:

        pipeline:
          - Config: 配置文件指定MLP类型
          - Factory: OneMlp工厂创建实例
          - Usage: 统一接口调用
          - Output: MLP计算结果

      modular_mlp:

        pipeline:
          - Registry: MLP注册表
          - Interface: 统一访问接口
          - Implementation: 具体MLP实现
          - Integration: 系统集成

    hot_models:

      - model: Factory Pattern
        year: 1994
        role: 设计模式经典实现
        architecture: creational pattern

      - model: Multi-Layer Perceptron
        year: 1957
        role: 神经网络基础组件
        architecture: feedforward neural network

    best_practices:

      - 保持接口的一致性和简洁性
      - 提供清晰的错误信息
      - 支持参数动态透传
      - 维护完整的注册表文档

    anti_patterns:

      - 注册表不一致导致运行时错误
      - 接口设计过于复杂
      - 缺少适当的错误处理
      - 参数验证不充分

    paper_references:

      - title: "Design Patterns: Elements of Reusable Object-Oriented Software"
        authors: Gamma et al.
        year: 1994

      - title: "Learning representations by back-propagating errors"
        authors: Rumelhart et al.
        year: 1986

  graph:

    is_a:
      - FactoryModule
      - UnifiedInterface
      - MlpWrapper

    part_of:
      - ModularArchitecture
      - MlpSystem
      - ComponentRegistry

    depends_on:
      - MeshGraphMLP
      - StandardMLP
      - GroupEquivariantMLP2d/3d
      - XiheMlp

    variants:
      - OneEncoder (编码器统一接口)
      - OneDecoder (解码器统一接口)
      - OneFuser (融合器统一接口)

    used_in_models:
      - 模块化深度学习系统
      - 多MLP集成框架
      - 动态MLP选择系统

    compatible_with:

      inputs:
        - MlpConfigurations
        - ModelParameters
        - InputFeatures

      outputs:
        - MlpResults
        - TransformedFeatures
        - ComputedValues
