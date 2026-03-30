component:

  meta:
    name: OneFCWrapper
    alias: OneFC
    version: 1.0
    domain: ai_for_science
    category: neural_network
    subcategory: component_factory
    author: OneScience
    license: Apache-2.0
    tags:
      - factory_pattern
      - module_registry
      - wrapper
      - feed_forward
      - fuxi
      - fourcastnet

  concept:

    description: >
      OneFC 是一个统一的全连接层（FC / FFN）工厂和包装器模块。
      它通过内置的注册表（Registry）机制，将气象和流体力学大模型中（如伏羲 FuXi、FourCastNet）不同的特定全连接层实现整合在一个统一的接口下。
      调用者只需指定模型的风格（Style）字符串，即可动态实例化并调用对应的底层 FC 模块。

    intuition: >
      类似于软件工程中的“工厂模式”（Factory Pattern），该模块将对象实例化的逻辑提取出来。
      当开发大型统一 AI 框架时，通常会通过配置文件（如 YAML/JSON）来实验不同的模型架构。
      使用 OneFC，代码不需要大量的 if-else 导入分支，只需向大门（OneFC）递交一张写着具体模型名字的通行证（style），
      它就会自动为你调配出对应的“特征处理车间”。

    problem_it_solves:
      - 解决 AI 框架中不同子模型组件的统一调用与解耦问题
      - 遵循“开闭原则”（Open-Closed Principle），增加新模型时只需向 Registry 注册，无需修改调用逻辑
      - 方便通过超参数配置文件无缝切换和对比不同架构（如 FuxiFC vs FourCastNetFC）的性能

  theory:

    formula:

      one_fc_dispatch:
        expression: y = Registry[style](x, **kwargs)

    variables:

      style:
        name: ModelStyle
        description: 用于在注册表中选择特定模块实现的键值（字符串）

      kwargs:
        name: HyperParameters
        description: 透传给具体被选中模块初始化函数的关键字参数字典

      x:
        name: Input
        shape: dynamic
        description: 输入张量，形状取决于所选的具体模块要求

  structure:

    architecture: factory_wrapper

    pipeline:

      - name: DynamicDispatch
        operation: retrieve_class_from_registry

      - name: ModuleInstantiation
        operation: initialize_with_kwargs

      - name: ForwardPass
        operation: pass_input_to_instantiated_module

  interface:

    parameters:

      style:
        type: str
        description: 选择要使用的 FC 层类型。当前支持的选项为 "FuxiFC" 和 "FourCastNetFC"

      kwargs:
        type: dict
        description: 传递给具体底层 FC 层实现的超参数（如 in_channels, out_features, drop 等）

    inputs:

      x:
        type: Tensor
        shape: dynamic
        dtype: float32
        description: 输入张量，形状要求由被实例化的目标模块决定

    outputs:

      output:
        type: Tensor
        shape: dynamic
        description: 对应底层模块处理后的输出张量

  types:

    Tensor:
      shape: dynamic
      description: 任意维度的 PyTorch 张量

  implementation:

    framework: pytorch

    code: |
      import torch
      from torch import nn

      from .fuxifc import FuxiFC
      from .fourcastnetfc import FourCastNetFC

      _FC_REGISTRY = {
          "FuxiFC": FuxiFC,
          "FourCastNetFC": FourCastNetFC,
      }

      class OneFC(nn.Module):
          def __init__(self, style: str, **kwargs):
              super().__init__()

              if style not in _FC_REGISTRY:
                  raise NotImplementedError(f"Unknown style: {style}")
              
              self.fc = _FC_REGISTRY[style](**kwargs)
              
          def forward(self, x):
              
              return self.fc(x)

  skills:

    build_unified_fc:

      description: 使用统一接口为不同的 AI 物理模型构建特定的全连接层

      inputs:
        - style
        - kwargs

      prompt_template: |
        构建一个 OneFC 模块。
        模型风格：{{style}}
        请确保为该风格提供正确的额外参数：{{kwargs}}。

    diagnose_factory_issues:

      description: 分析由动态包装器引起的常见传参和注册错误

      checks:
        - not_implemented_error_for_unknown_style
        - type_error_due_to_mismatched_kwargs_for_specific_style

  knowledge:

    usage_patterns:

      config_driven_builder:

        pipeline:
          - LoadConfig (解析 YAML/JSON)
          - OneFC (传入 config.style 和 config.params)
          - Forward

    design_patterns:

      module_registry:

        structure:
          - 维护一个全局字典 `_FC_REGISTRY` 映射字符串标识到实际的类对象
          - 在初始化时进行查表验证，解耦了调用方和具体实现类

    hot_models:

      - model: Unified Earth System / Fluid Dynamics Frameworks
        year: 2023-2024
        role: 集成多种 AI 气象/流体力学模型的统一代码库
        architecture: dynamic_routing
        attention_type: None

    model_usage_details:

      SupportedStyles:

        - FuxiFC: 伏羲模型专用，通常用于通道上的 Pointwise 投影 (Channels-Last)
        - FourCastNetFC: FourCastNet 专用，基于 GELU 和 Dropout 的 4x 隐藏层放大的标准 FFN

    best_practices:

      - 使用此模块可以极大简化主干网络（Backbone）的代码编写，主干代码只需调用 `OneFC`，将具体细节交由外部配置控制。
      - 如果需要增加新的模型支持（例如 PanguWeatherFC），只需将其 `import` 并添加到 `_FC_REGISTRY` 字典中即可，无需改动 `OneFC` 的核心逻辑。
      - 传入 `**kwargs` 时，必须清楚目标 `style` 的构造函数签名。例如，如果 `style="FuxiFC"`，则不能传入 FourCastNetFC 专属的 `drop` 参数。

    anti_patterns:

      - 为了适配某个特殊的 FC 层，直接在 `OneFC.__init__` 里面写死针对该 `style` 的特定参数解析逻辑（应保持 Wrapper 的纯粹性，让 `**kwargs` 原样穿透）。
      - 传入未注册的 `style` 字符串，会导致程序直接触发 `NotImplementedError` 崩溃。

    paper_references:

      - title: "Software Engineering for Machine Learning: A Case Study"
        authors: Amershi et al.
        year: 2019

      - title: (关联底层模块文献) "FourCastNet: A Global Data-driven High-resolution Weather Model using Adaptive Fourier Neural Operators"
        authors: Pathak et al.
        year: 2022

  graph:

    is_a:
      - NeuralNetworkWrapper
      - FactoryModule
      - Dispatcher

    part_of:
      - UnifiedModelBuilder
      - AIEngineeringFramework

    depends_on:
      - FuxiFC
      - FourCastNetFC

    variants:
      - DynamicModule

    used_in_models:
      - 支持多后端的通用气象与流体力学 AI 框架

    compatible_with:

      inputs:
        - Tensor

      outputs:
        - Tensor