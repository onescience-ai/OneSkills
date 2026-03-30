component:

  meta:
    name: OneDiffusionWrapper
    alias: OneDiffusion
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
      - proxy_pattern
      - diffusion_model
      - alphafold3

  concept:

    description: >
      OneDiffusion 是一个统一的扩散生成模块（Diffusion Module）工厂和包装器。
      它通过注册表（Registry）机制动态管理和实例化不同的扩散算法组件。当前它主要服务于 AlphaFold 3 (AF3) 以及开源复现项目（如 Protenix）中的扩散核心逻辑。
      除了标准的动态路由（Dispatch）外，它还通过重载 `__getattr__` 实现了透明的属性代理（Proxy Pattern），使得外部调用者可以直接访问底层实例的特有方法。

    intuition: >
      在复杂的大分子生成模型中，扩散过程往往包含多种不同的组件（如去噪网络本身、噪声调度器 Schedule、条件注入模块 Conditioning）。
      OneDiffusion 就像是一个“通用插座”或“万能代理”。主控程序只要告诉它需要什么类型的插头（`style`），它就能接通对应的扩散模块。
      得益于 `__getattr__` 的魔法，如果主控程序想调用内部专属的功能（比如 AF3 `DiffusionModule` 里的 `f_forward`），它可以直接对 `OneDiffusion` 喊话，而不需要知道中间包装器的存在。

    problem_it_solves:
      - 提供大模型统一框架下的多种扩散策略和去噪网络架构的热插拔机制
      - 解耦调用方与具体的扩散模块实现细节（遵循开闭原则）
      - 解决传统包装器（Wrapper）阻断对底层模型特有方法（如自定义推理函数、采样器）访问的问题

  theory:

    formula:

      one_diffusion_dispatch:
        expression: y = \text{Registry}[\text{style}](*\text{args}, **\text{kwargs})

      attribute_delegation:
        expression: \text{getattr}(\text{OneDiffusion}, \text{name}) \rightarrow \text{getattr}(\text{OneDiffusion.Diffusion}, \text{name})

    variables:

      style:
        name: ModelStyle
        description: 用于在注册表中选择特定扩散模块实现的键值（字符串）

      args, kwargs:
        name: ForwardArguments
        description: 透传给具体被选中扩散模块的前向传播参数（如 x_noisy, t_hat_noise_level 等）

      name:
        name: AttributeName
        description: 外部尝试访问的属性或方法名称

  structure:

    architecture: factory_wrapper_with_proxy

    pipeline:

      - name: DynamicDispatch
        operation: retrieve_class_from_registry

      - name: ModuleInstantiation
        operation: initialize_with_kwargs

      - name: ForwardPass
        operation: pass_all_args_to_instantiated_module

      - name: AttributeDelegation
        operation: fallback_to_underlying_module_attributes

  interface:

    parameters:

      style:
        type: str
        description: 选择要使用的扩散相关层类型。如 "DiffusionModule" 或未来的 "ProtenixDiffusionSchedule"

      kwargs:
        type: dict
        description: 传递给具体底层扩散模块初始化的超参数

    inputs:

      args, kwargs:
        type: dynamic
        description: 输入参数的签名完全由实例化的底层扩散模块决定

    outputs:

      output:
        type: dynamic
        description: 底层模块的输出，如去噪后的坐标张量 (x_denoised)

  types:

    Tensor:
      shape: dynamic
      description: 任意维度的 PyTorch 张量

  implementation:

    framework: pytorch

    code: |
      from torch import nn

      from .diffusionmodule import DiffusionModule
      # from .protenixdiffusion import (
      #     ProtenixDiffusionConditioning,
      #     ProtenixDiffusionSchedule,
      #     ProtenixDiffusionModule,
      # )

      _DIFFUSION_REGISTRY = {
          "DiffusionModule": DiffusionModule,
          # "ProtenixDiffusionConditioning": ProtenixDiffusionConditioning,
          # "ProtenixDiffusionSchedule": ProtenixDiffusionSchedule,
          # "ProtenixDiffusionModule": ProtenixDiffusionModule,
      }


      class OneDiffusion(nn.Module):
          """
          OneDiffusion module for diffusion operations with various styles.

          Supports:
          - DiffusionModule: Generic diffusion module
          - ProtenixDiffusionConditioning: Protenix conditioning (Algorithm 21)
          - ProtenixDiffusionSchedule: Protenix noise schedule
          - ProtenixDiffusionModule: Protenix diffusion module (Algorithm 20)
          """

          def __init__(self, style: str, **kwargs):
              super().__init__()

              if style not in _DIFFUSION_REGISTRY:
                  raise NotImplementedError(f"Unknown style: {style}")

              self.Diffusion = _DIFFUSION_REGISTRY[style](**kwargs)

          def forward(self, *args, **kwargs):
              return self.Diffusion(*args, **kwargs)


          def __getattr__(self, name):
              try:
                  return super().__getattr__(name)
              except AttributeError:
                  return getattr(self.Diffusion, name)

  skills:

    build_unified_diffusion:

      description: 使用代理模式工厂为 AI 预测架构构建指定的扩散组件

      inputs:
        - style
        - kwargs

      prompt_template: |
        构建一个 OneDiffusion 模块。
        指定风格为 {{style}}。
        传入相关的扩散超参数：{{kwargs}}。

    diagnose_proxy_delegation:

      description: 分析使用 __getattr__ 代理时由底层模块缺失属性引发的错误

      checks:
        - recursion_error_if_getattr_is_misconfigured
        - missing_method_in_underlying_diffusion_style

  knowledge:

    usage_patterns:

      config_driven_diffusion_pipeline:

        pipeline:
          - CheckConfig (获取 style)
          - OneDiffusion (动态构建 Denoising Network / Schedule)
          - ForwardPass
          - Implicit Method Call (通过 OneDiffusion 直接调用底层如 f_forward 等特有方法)

    design_patterns:

      proxy_pattern:

        structure:
          - 不仅仅是一个实例化工厂（Factory），还充当代理（Proxy）。
          - `__getattr__` 的魔法方法捕获了对包装器不存在属性的访问，并将其重定向到被包装的对象（`self.Diffusion`）。这在深度学习框架中非常优雅，避免了开发者必须写 `model.module.f_forward()` 这样累赘且破坏封装的代码。

    hot_models:

      - model: Protenix / AlphaFold 3
        year: 2024
        role: 蛋白质复合物三维结构的高精度预测
        architecture: diffusion_generative_model
        attention_type: None (此处为包装器)

    model_usage_details:

      SupportedStyles:

        - DiffusionModule: AF3 中 Algorithm 20 的主干去噪模型
        - ProtenixDiffusionSchedule: 控制扩散加噪/去噪时间步的调度器（目前被注释，预留扩展）

    best_practices:

      - 当需要增加其他公司的扩散实现（例如 RoseTTAFold All-Atom 的扩散模块）时，只需解除注释或添加新的 `import` 并注册到 `_DIFFUSION_REGISTRY` 中。
      - 利用 `__getattr__` 带来的便利性，主循环可以直接执行 `one_diffusion_instance.f_forward(...)`，代码应当放心使用这种透明调用。
      - 当 `forward` 被重载处理 `*args, **kwargs` 时，必须确保外层传参和所选 `style` 对应的 `forward` 签名严丝合缝。

    anti_patterns:

      - 错误地在外部调用时写出 `wrapper.Diffusion.forward(...)`，这违背了包装器设计意图。
      - 在 `__getattr__` 中没有正确使用 `super().__getattr__(name)` 捕获基类 `nn.Module` 的原生属性（如 `training`, `parameters`），会导致 PyTorch 内部机制崩溃。当前代码完美避开了这一陷阱。

    paper_references:

      - title: "Design Patterns: Elements of Reusable Object-Oriented Software" (设计模式，关联 Proxy 模式)
        authors: Gamma et al.
        year: 1994

  graph:

    is_a:
      - NeuralNetworkWrapper
      - FactoryModule
      - ProxyModule

    part_of:
      - UnifiedModelBuilder
      - GenerativeDiffusionPipeline

    depends_on:
      - DiffusionModule
      - Python Magic Method (__getattr__)

    variants:
      - DynamicModule

    used_in_models:
      - 生物分子扩散生成统一框架 (如 Protenix)

    compatible_with:

      inputs:
        - Dynamic (*args, **kwargs)

      outputs:
        - Dynamic