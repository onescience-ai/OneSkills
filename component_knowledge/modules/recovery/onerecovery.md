component:

  meta:
    name: OneRecoveryWrapper
    alias: OneRecovery
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
      - patch_recovery
      - pangu_weather
      - xihe

  concept:

    description: >
      OneRecovery 是一个统一的特征重构（Patch Recovery / 解码）层工厂和包装器模块。
      它通过内置的注册表（Registry）机制，将气象大模型中（如盘古 Pangu-Weather 的 2D/3D 版本、羲和 Xihe）用于将隐藏层 Token/Patch 映射回物理空间网格的不同重构模块整合在统一接口下。
      调用方只需指定所需的模型风格（Style），模块便会自动动态实例化并调用对应的底层重构逻辑。

    intuition: >
      在 Vision Transformer 或类似架构的末端，通常需要一个“反 Patch 化”（Un-patchify）或重构模块将低分辨率的高维特征恢复为高分辨率的物理场（如经纬度网格上的气象变量）。
      类似于 `OneFC`，`OneRecovery` 充当一个中央调度站（Dispatcher）。开发者通过配置文件传递一张“图纸”（style），它就能自动调配出合适的“重构车间”（如 PanguPatchRecovery3D），极大提升了代码框架的复用性和整洁度。

    problem_it_solves:
      - 解决统一 AI 框架中各种模型反 Patch 化（Patch Recovery）模块的统一调用与解耦问题
      - 遵循“开闭原则”，增加新模型的重构层时只需向 Registry 注册，主干解码代码无需改动
      - 方便通过超参数配置文件无缝切换不同的空间重构策略（如 2D 恢复与 3D 恢复的对比测试）

  theory:

    formula:

      one_recovery_dispatch:
        expression: y = \text{Registry}[\text{style}](x, \text{**kwargs})

    variables:

      style:
        name: ModelStyle
        description: 用于在注册表中选择特定重构模块实现的键值（字符串）

      kwargs:
        name: HyperParameters
        description: 透传给具体被选中重构模块初始化函数的关键字参数字典

      x:
        name: Input
        shape: dynamic
        description: 输入张量（通常为 Transformer Block 输出的隐层 Token 序列或特征图）

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
        description: 选择要使用的重构层类型。当前支持 "PanguPatchRecovery3D", "PanguPatchRecovery2D" 和 "XihePatchRecovery"

      kwargs:
        type: dict
        description: 传递给具体底层 Patch Recovery 层实现的超参数（如 patch_size, embed_dim, output_shape 等）

    inputs:

      x:
        type: Tensor
        shape: dynamic
        dtype: float32
        description: 输入的特征张量，形状要求由被实例化的目标模块决定

    outputs:

      output:
        type: Tensor
        shape: dynamic
        description: 经过底层模块重构后恢复的物理场网格张量

  types:

    Tensor:
      shape: dynamic
      description: 任意维度的 PyTorch 张量

  implementation:

    framework: pytorch

    code: |
      import torch
      from torch import nn

      from .pangupatchrecovery2d import PanguPatchRecovery2D
      from .pangupatchrecovery3d import PanguPatchRecovery3D
      from .xihepatchrecovery    import XihePatchRecovery

      _RECOVERY_REGISTRY = {
          "PanguPatchRecovery3D": PanguPatchRecovery3D,
          "PanguPatchRecovery2D": PanguPatchRecovery2D,
          "XihePatchRecovery":XihePatchRecovery,
      }

      class OneRecovery(nn.Module):
          def __init__(self, style: str, **kwargs):
              super().__init__()

              if style not in _RECOVERY_REGISTRY:
                  raise NotImplementedError(f"Unknown style: {style}")
              
              self.Reconvery = _RECOVERY_REGISTRY[style](**kwargs)
              
          def forward(self, x):
              
              return self.Reconvery(x) 

  skills:

    build_unified_recovery:

      description: 使用统一接口为不同的 AI 气象/物理模型构建特定的特征重构（解码）层

      inputs:
        - style
        - kwargs

      prompt_template: |
        构建一个 OneRecovery 模块。
        模型风格：{{style}}
        请确保为该重构风格提供正确的额外参数：{{kwargs}}。

    diagnose_factory_issues:

      description: 分析由动态包装器引起的常见传参和注册错误

      checks:
        - not_implemented_error_for_unknown_style
        - type_error_due_to_mismatched_kwargs_for_specific_recovery_style

  knowledge:

    usage_patterns:

      config_driven_decoder:

        pipeline:
          - DeepLatentFeatures (来自 Encoder 或 Processor)
          - OneRecovery (传入 config.recovery_style 和 config.recovery_params)
          - ReshapedPhysicalGrid (物理场输出)

    design_patterns:

      module_registry:

        structure:
          - 维护一个全局字典 `_RECOVERY_REGISTRY` 映射字符串标识到实际的重构类对象
          - 在初始化时进行查表验证，解耦了调用方和具体实现类

    hot_models:

      - model: Unified Earth System / Fluid Dynamics Frameworks
        year: 2023-2024
        role: 集成多种 AI 气象/流体力学模型的统一代码库
        architecture: dynamic_routing
        attention_type: None

    model_usage_details:

      SupportedStyles:

        - PanguPatchRecovery3D: 盘古气象大模型 3D 版的 Patch 恢复模块
        - PanguPatchRecovery2D: 盘古气象大模型 2D 版的 Patch 恢复模块
        - XihePatchRecovery: 羲和（Xihe）气象大模型的 Patch 恢复模块

    best_practices:

      - 就像使用 `OneFC` 一样，主干网络的 Decoder 末端只需调用 `OneRecovery`，具体如何将 Patch 还原为经纬度网格的细节由配置文件决定。
      - 当新增其他气象模型（如 FengWu, GraphCast 的网格映射层）时，只需将其 `import` 并注册到 `_RECOVERY_REGISTRY`，遵循了良好的软件工程规范。
      - 传入 `**kwargs` 时必须与目标类的 `__init__` 参数对齐。例如，3D 恢复可能需要深度维度（Depth/Pls）参数，而 2D 恢复则不需要。

    anti_patterns:

      - 在主网络代码中写大量 `if style == 'PanguPatchRecovery3D': ... elif ...` 分支（这正是 OneRecovery 设计来消除的代码坏味道）。
      - 传入拼写错误或未注册的 `style` 字符串（将抛出 `NotImplementedError`）。
      - （注意代码细节）代码实现中存在拼写错误 `self.Reconvery`（应为 `Recovery`），在外部调用或调试对象属性时需要注意这个命名。

    paper_references:

      - title: "Pangu-Weather: A 3D High-Resolution Model for Fast and Accurate Global Weather Forecast"
        authors: Bi et al.
        year: 2023

      - title: (关联底层模块文献) "Xihe: A Data-Driven Model for Global Weather Forecasting"
        authors: (Xihe Authors)
        year: 2023-2024

  graph:

    is_a:
      - NeuralNetworkWrapper
      - FactoryModule
      - DecoderComponent

    part_of:
      - UnifiedModelBuilder
      - WeatherForecastingDecoder

    depends_on:
      - PanguPatchRecovery2D
      - PanguPatchRecovery3D
      - XihePatchRecovery

    variants:
      - DynamicModule

    used_in_models:
      - 支持多后端的通用气象大模型框架

    compatible_with:

      inputs:
        - Tensor (Latent Tokens)

      outputs:
        - Tensor (Physical Grid)