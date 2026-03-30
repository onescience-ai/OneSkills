component:

  meta:
    name: OneTransformer
    alias: UnifiedTransformerFactory
    version: 1.0
    domain: deep_learning
    category: neural_network
    subcategory: unified_interface
    author: OneScience
    license: Apache-2.0
    tags:
      - factory_pattern
      - unified_interface
      - dynamic_instantiation
      - transformer_registry


  concept:

    description: >
      OneTransformer 是整个组件库中所有 Transformer 变体的统一调用入口。
      它采用了设计模式中的工厂模式（Factory）与代理模式（Proxy），通过内部维护的 
      _TRANSFORMER_REGISTRY 注册表，根据传入的 style 字符串动态实例化对应的核心模块，
      并将所有的前向传播（forward）和属性访问（__getattr__）无缝代理给底层的具体实例。

    intuition: >
      就像一个拥有各种专业工具的大型“工具箱”。当你需要处理气象数据时，不需要到处去翻找具体的气象模块代码，
      只需要对着工具箱喊一声“给我一个 EarthTransformer3DBlock”，工具箱（OneTransformer）就会自动把这个工具递给你，
      并且在使用时，你感觉就像是在直接使用那个特定工具一样顺手。

    problem_it_solves:
      - 消除 AI 工程流中硬编码具体模型类名所带来的强耦合问题
      - 允许通过外部配置文件（如 JSON/YAML）直接驱动模型架构的动态切换和组装
      - 提供统一的代码接口，极大地简化了复杂流水线（Pipeline）的开发和维护成本


  theory:

    formula:

      dynamic_dispatch:
        expression: $$y = \text{Registry}[\text{style}](x, \dots)$$

    variables:

      Registry:
        name: TransformerRegistry
        description: 内部维护的字典 _TRANSFORMER_REGISTRY，映射组件名称与对应的 Python 类

      style:
        name: ModuleStyle
        description: 字符串键值，用于在注册表中查找特定的模型架构


  structure:

    architecture: factory_proxy_wrapper

    pipeline:

      - name: StyleLookup
        operation: dict_get (检查 style 是否在注册表中)

      - name: DynamicInstantiation
        operation: class_init (将 **kwargs 透传给具体类进行初始化)

      - name: ForwardDelegation
        operation: forward_pass (将输入直接传递给底层 self.transformer)

      - name: AttributeProxy
        operation: getattr (拦截未定义的属性访问，并转发给底层实例)


  interface:

    parameters:

      style:
        type: str
        description: 目标 Transformer 模块的名称，如 "FuxiTransformer" 或 "Galerkin_Transformer_block"

      kwargs:
        type: dict
        description: 目标模块初始化所需的全部关键字参数，将通过 **kwargs 直接透传

    inputs:

      args:
        type: any
        description: 传递给目标模块 forward 方法的位置参数

      kwargs_forward:
        type: any
        description: 传递给目标模块 forward 方法的关键字参数

    outputs:

      output:
        type: any
        description: 由底层具体 Transformer 模块返回的处理结果


  implementation:

    framework: pytorch

    code: |

      import torch
      from torch import nn

      # 导入所有具体的 Transformer 模块 (省略了具体的 import 列表)
      
      _TRANSFORMER_REGISTRY = {
          "XiHeTransformer3D": XiHeTransformer3D,
          "PreLNTransformerBlock": PreLNTransformerBlock,
          "Factformer_block": Factformer_block,
          "Galerkin_Transformer_block": Galerkin_Transformer_block,
          "GNOTTransformerBlock": GNOTTransformerBlock,
          "NeuralSpectralBlock1D": NeuralSpectralBlock1D,
          "NeuralSpectralBlock2D": NeuralSpectralBlock2D,
          "NeuralSpectralBlock3D": NeuralSpectralBlock3D,
          "OrthogonalNeuralBlock": OrthogonalNeuralBlock,
          "SwinTransformerBlock": SwinTransformerBlock,
          "Transolver_block": Transolver_block,
          "FuxiTransformer": FuxiTransformer,
          "EarthTransformer2DBlock": EarthTransformer2DBlock,
          "EarthTransformer3DBlock": EarthTransformer3DBlock,
          "EarthDistributedTransformer3DBlock": EarthDistributedTransformer3DBlock,
          "XihelocalTransformer": XihelocalTransformer,
      }

      class OneTransformer(nn.Module):
          def __init__(self, style: str, **kwargs):
              super().__init__()

              if style not in _TRANSFORMER_REGISTRY:
                  raise NotImplementedError(
                      f"Unknown style: '{style}'. Available options are: {list(_TRANSFORMER_REGISTRY.keys())}"
                  )
              
              self.transformer = _TRANSFORMER_REGISTRY[style](**kwargs)
              
          def forward(self, *args, **kwargs):
              return self.transformer(*args, **kwargs)

          def __getattr__(self, name):
              try:
                  return super().__getattr__(name)
              except AttributeError:
                  return getattr(self.transformer, name)


  skills:

    build_unified_transformer:

      description: 通过统一的接口调用具体的 Transformer 变体

      inputs:
        - style
        - kwargs

      prompt_template: |

        请实例化 OneTransformer。
        必须指定合法的 style 参数（如 "GNOTTransformerBlock"），并将该底层模块所需的参数通过 kwargs 一并传入。


    diagnose_factory_issues:

      description: 排查动态工厂模式的调用错误

      checks:
        - unregistered_style (传入了未在 _TRANSFORMER_REGISTRY 中注册的字符串)
        - kwargs_mismatch (传入的参数与底层具体目标类的 __init__ 签名不匹配)



  knowledge:

    usage_patterns:

      config_driven_architecture:

        pipeline:
          - 从 JSON/YAML 配置文件中读取 `style` 和 `args`
          - `model = OneTransformer(style=config.style, **config.args)`
          - `output = model(input)`


    best_practices:

      - 充分利用 `__getattr__` 的魔法方法设计。如果外部代码试图访问特定底层模块的特有属性（比如 `model.modes_list`），`OneTransformer` 会自动代理这个请求，避免了复杂的接口暴露问题。
      - 每次开发新的 Transformer 变体后，务必记得在此文件的 `_TRANSFORMER_REGISTRY` 中进行注册，否则配置驱动的构建流程会失败。


    anti_patterns:

      - 绕过 `OneTransformer`，在业务流的高层代码中直接硬编码 `import GNOTTransformerBlock`。这会破坏整体的组件化抽象原则，降低系统可扩展性。



  graph:

    is_a:
      - FactoryModule
      - Wrapper

    part_of:
      - ComponentLibrary

    depends_on:
      - _TRANSFORMER_REGISTRY (包含所有底层组件)

    variants:
      - None

    used_in_models:
      - Generic Pipeline Builders

    compatible_with:

      inputs:
        - Any (透传)

      outputs:
        - Any (透传)