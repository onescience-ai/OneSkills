component:

  meta:
    name: OneLinear
    alias: LinearFactory
    version: 1.0
    domain: deep_learning
    category: neural_network
    subcategory: module_dispatcher
    author: OneScience
    license: Apache-2.0
    tags:
      - linear
      - registry
      - factory_pattern
      - wrapper
      - pytorch


  concept:

    description: >
      OneLinear 通过注册表机制统一实例化不同风格的线性层实现（ProtenixLinear 系列）。
      其 forward 透传参数到目标线性层，并通过 __getattr__ 将未定义属性代理到底层模块，
      以保持调用侧对底层属性和方法的透明访问。

    intuition: >
      该模块像“线性层路由器 + 代理器”：负责按 style 选实现，同时把底层对象当作自身暴露，
      让上层代码无需感知具体类差异。

    problem_it_solves:
      - 统一多种线性实现的创建入口
      - 降低上层网络与具体线性类的耦合
      - 提供属性代理以提升兼容性和可扩展性
      - 对非法 style 立即抛出错误


  theory:

    formula:

      registry_dispatch:
        expression: |
          f_{linear} = Registry[style](**kwargs)
          y = f_{linear}(*args, **kwargs)

      attribute_proxy:
        expression: |
          attr(OneLinear, name) = attr(LinearImpl, name)\ \text{if local attr missing}

    variables:

      style:
        name: LinearStyle
        description: 线性层风格键

      Registry:
        name: LinearRegistry
        description: 风格到线性层类的映射

      LinearImpl:
        name: TargetLinearModule
        description: 实际执行线性运算的底层模块


  structure:

    architecture: registry_proxy_wrapper

    pipeline:

      - name: StyleValidation
        operation: check_style_in_registry

      - name: ModuleInstantiation
        operation: build_target_linear_module

      - name: ForwardDelegation
        operation: passthrough_to_linear_impl

      - name: AttributeFallback
        operation: proxy_unknown_attributes


  interface:

    parameters:

      style:
        type: str
        description: 目标线性实现名称

      kwargs:
        type: dict
        description: 构造目标线性层所需参数

    inputs:

      args:
        type: tuple
        description: 前向透传参数

      kwargs:
        type: dict
        description: 前向透传关键字参数

    outputs:

      output:
        type: Tensor
        description: 目标线性层的输出


  types:

    Tensor:
      description: PyTorch 张量


  implementation:

    framework: pytorch

    code: |

      from torch import nn
      from .protenixlinear import ProtenixLinear, ProtenixLinearNoBias, ProtenixBiasInitLinear

      _LINEAR_REGISTRY = {
          "ProtenixLinear": ProtenixLinear,
          "ProtenixLinearNoBias": ProtenixLinearNoBias,
          "ProtenixBiasInitLinear": ProtenixBiasInitLinear,
      }

      class OneLinear(nn.Module):
          def __init__(self, style: str, **kwargs):
              super().__init__()
              if style not in _LINEAR_REGISTRY:
                  raise NotImplementedError(f"Unknown style: {style}")
              self.Linear = _LINEAR_REGISTRY[style](**kwargs)

          def forward(self, *args, **kwargs):
              return self.Linear(*args, **kwargs)

          def __getattr__(self, name):
              try:
                  return super().__getattr__(name)
              except AttributeError:
                  return getattr(self.Linear, name)


  skills:

    build_linear_dispatcher:

      description: 构建统一线性层分发与代理模块

      inputs:
        - style
        - kwargs

      prompt_template: |

        构建 OneLinear 模块。

        参数：
        style = {{style}}
        kwargs = {{kwargs}}

        要求：
        采用注册表分发并支持属性代理访问。


    diagnose_linear_dispatcher:

      description: 分析线性层分发器中的配置和代理行为问题

      checks:
        - unknown_style_registration
        - missing_registry_entry
        - attribute_proxy_shadowing
        - forward_argument_mismatch


  knowledge:

    usage_patterns:

      modular_linear_switch:

        pipeline:
          - ParseStyle
          - InstantiateOneLinear
          - ForwardPassthrough

      transparent_wrapper:

        pipeline:
          - AccessWrapperAttr
          - FallbackToInnerModule


    hot_models:

      - model: ProtenixLinear Family
        year: 2024
        role: OneLinear 当前注册目标
        architecture: customized_linear


    best_practices:

      - 注册表键名与配置文件中的 style 保持严格一致。
      - 新增线性类后同步更新注册表与测试用例。
      - 对 __getattr__ 代理行为进行冲突检查，避免覆盖本地属性。


    anti_patterns:

      - 用 if-else 链替代注册表，造成扩展困难。
      - 未知 style 静默回退默认实现，导致实验不可追踪。


    paper_references:

      - title: "Design Patterns: Elements of Reusable Object-Oriented Software"
        authors: Gamma et al.
        year: 1994


  graph:

    is_a:
      - NeuralNetworkComponent
      - FactoryWrapper

    part_of:
      - LinearModuleSystem

    depends_on:
      - RegistryPattern
      - ProtenixLinear
      - ProtenixLinearNoBias
      - ProtenixBiasInitLinear

    variants:
      - OneAFNO
      - OneEdge
      - OneEquivariant

    used_in_models:
      - Protenix Pipelines
      - Modular Backbones
      - Research Prototypes

    compatible_with:

      inputs:
        - SequenceEmbedding

      outputs:
        - SequenceEmbedding