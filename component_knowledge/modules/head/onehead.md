component:

  meta:
    name: OneHeadWrapper
    alias: OneHead
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
      - prediction_head
      - task_specific_head

  concept:

    description: >
      OneHead 是一个统一的预测头（Prediction Head）工厂和包装器模块。
      它通过内置的注册表（Registry）机制，将用于不同下游任务和不同数据维度的输出层（如蛋白质 MSA 预测的 `MaskedMSAHead`，
      以及用于一维、二维、三维物理场预测的 `UNetHead1D/2D/3D`）整合在一个统一的调用接口下。
      开发者只需通过 `style` 字符串即可动态实例化对应的网络尾部组件。

    intuition: >
      在多任务或支持多种空间维度的 AI 统一框架中，网络的主干（Backbone）输出的隐层特征往往需要特定任务的“翻译官”将其映射为最终的物理量或分类概率。
      OneHead 就像一个可更换工作台的适配器接口。主网络不需要知道自己接的是 2D 流场预测头还是蛋白质序列分类头，
      它只管向 OneHead 输送特征，由 OneHead 根据配置（style）自动“分配”给正确的处理模块。

    problem_it_solves:
      - 解决统一大模型框架中下游任务预测头繁杂、硬编码带来的主干网络代码臃肿问题
      - 遵循软件工程的“开闭原则”（Open-Closed Principle），扩展新任务头部时无需修改原有逻辑代码
      - 为基于配置（Config-driven）的动态模型构建提供标准化的尾部出口

  theory:

    formula:

      one_head_dispatch:
        expression: $y = \text{Registry}[\text{style}](*\text{args}, **\text{kwargs})$

    variables:

      style:
        name: ModelStyle
        description: 用于在注册表中选择特定预测头实现的键值（字符串标识符）

      args:
        name: PositionalArguments
        description: 透传给具体被选中预测头模块前向传播的位置参数（如特征张量）

      kwargs:
        name: KeywordArguments
        description: 透传给具体被选中预测头模块初始化或前向传播的关键字参数

  structure:

    architecture: factory_wrapper

    pipeline:

      - name: DynamicDispatch
        operation: retrieve_class_from_registry

      - name: ModuleInstantiation
        operation: initialize_with_kwargs

      - name: ForwardPass
        operation: pass_inputs_to_instantiated_head

  interface:

    parameters:

      style:
        type: str
        description: 选择要使用的预测头类型。当前支持的选项为 "MaskedMSAHead", "UNetHead1D", "UNetHead2D", "UNetHead3D"

      kwargs:
        type: dict
        description: 传递给具体底层预测头实现的超参数（例如 c_m, c_out，或 in_channels 等）

    inputs:

      args, kwargs:
        type: dynamic
        description: 前向传播时的输入张量，其形状要求由被实例化的具体底层模块决定

    outputs:

      output:
        type: dynamic
        description: 对应底层预测头处理后的输出张量（如 Logits 分布或物理场重构特征）

  types:

    Tensor:
      shape: dynamic
      description: 任意维度的 PyTorch 张量

  implementation:

    framework: pytorch

    code: |
      import torch
      from torch import nn
      from .maskedmsahead import MaskedMSAHead
      from .unet_head import UNetHead1D, UNetHead2D, UNetHead3D

      # 构建统一的注册表
      _HEAD_REGISTRY = {
          "MaskedMSAHead": MaskedMSAHead,
          "UNetHead1D": UNetHead1D,
          "UNetHead2D": UNetHead2D,
          "UNetHead3D": UNetHead3D,
      }

      class OneHead(nn.Module):
          """
          OneHead 统一预测头调用接口。
          """
          def __init__(self, style: str, **kwargs):
              super().__init__()

              if style not in _HEAD_REGISTRY:
                  raise NotImplementedError(
                      f"Unknown style: '{style}'. Available options are: {list(_HEAD_REGISTRY.keys())}"
                  )
              
              # 实例化具体的预测头层
              self.head = _HEAD_REGISTRY[style](**kwargs)

          def forward(self, *args, **kwargs):
              """
              前向传播
              """
              return self.head(*args, **kwargs)

  skills:

    build_unified_head:

      description: 使用统一接口为不同的 AI 任务构建特定的尾部预测层

      inputs:
        - style
        - kwargs

      prompt_template: |
        构建一个 OneHead 模块。
        模型风格：{{style}}
        请确保为该预测头提供正确的额外参数：{{kwargs}}。

    diagnose_factory_issues:

      description: 分析由动态包装器引起的常见传参和注册错误

      checks:
        - not_implemented_error_for_unknown_style
        - type_error_due_to_mismatched_kwargs_for_specific_head

  knowledge:

    usage_patterns:

      config_driven_task_head:

        pipeline:
          - DeepLatentFeatures (来自主干网络 Backbone)
          - OneHead (传入 config.head_style 和 config.head_params)
          - Loss Computation (结合 Label 算 Loss)

    design_patterns:

      module_registry:

        structure:
          - 维护一个全局字典 `_HEAD_REGISTRY` 映射字符串标识到实际的类对象
          - 初始化时进行防御性查表验证，将控制反转（IoC），使得主网络架构彻底与任务层解耦

    hot_models:

      - model: Unified Earth System / Bio-Molecular Frameworks
        year: 2023-2024
        role: 集成多种跨尺度模型的统一代码库（如融合 AF3 与流体力学替代模型）
        architecture: dynamic_routing
        attention_type: None

    model_usage_details:

      SupportedStyles:

        - MaskedMSAHead: 蛋白质大模型中的遮蔽多序列比对预测头
        - UNetHead1D/2D/3D: 流体或 PDE 替代模型中的特定空间维度物理场预测头

    best_practices:

      - 与 `OneFC` 和 `OneRecovery` 的设计哲学保持一致，使用本模块作为模型输出端的“黑盒”，将具体的维度拼接、上采样或分类层逻辑封闭在独立的 Head 文件中。
      - 如果新增任务（如属性分类头 `PropertyClassificationHead`），应优先建立新的类文件，再将其导入并添加到 `_HEAD_REGISTRY` 字典中。
      - 在调用遇到 `NotImplementedError` 时，注意查看异常抛出信息中包含的 `Available options are: ...` 提示以排查配置字符串拼写错误。

    anti_patterns:

      - 在实例化 `OneHead` 时传递了目标 Head 类不支持的 kwargs 关键字参数（例如为 `MaskedMSAHead` 传递了只有 UNet 才支持的 `bilinear` 参数），会导致底层初始化时崩溃。
      - 在 `forward` 阶段直接修改内部 `self.head` 的状态或手动解包其内容，破坏了封装的独立性。

    paper_references:

      - title: "Software Engineering for Machine Learning: A Case Study"
        authors: Amershi et al.
        year: 2019
        note: (关联软件设计模式在深度学习框架中的最佳实践)

  graph:

    is_a:
      - NeuralNetworkWrapper
      - FactoryModule
      - PredictionHead

    part_of:
      - UnifiedModelBuilder
      - DownstreamTaskPipeline

    depends_on:
      - MaskedMSAHead
      - UNetHead1D
      - UNetHead2D
      - UNetHead3D

    variants:
      - DynamicModule

    used_in_models:
      - 支持多任务的通用 AI 基础框架

    compatible_with:

      inputs:
        - Tensor (Dynamic Latent Features)

      outputs:
        - Tensor (Task specific predictions)