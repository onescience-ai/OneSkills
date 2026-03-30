component:

  meta:
    name: OnePairformer
    alias: PairformerFactory
    version: 1.0
    domain: deep_learning
    category: neural_network
    subcategory: module_dispatcher
    author: OneScience
    license: Apache-2.0
    tags:
      - pairformer
      - registry
      - wrapper
      - factory_pattern
      - protenix


  concept:

    description: >
      OnePairformer 是 Pairformer 模块统一入口，按 style 从注册表中实例化对应实现并透传 forward。
      提供 __getattr__ 代理以暴露底层模块属性。
      当前源码中注册表项被注释，默认 style 校验会失败。

    intuition: >
      与 OneMSA/OneLinear 等一致，它将复杂 pairformer 实现隐藏在统一壳层后，
      通过配置路由不同 block 或 stack。

    problem_it_solves:
      - 统一 Pairformer 实例化和调用接口
      - 降低上层代码对具体 Pairformer 类依赖
      - 支持后续 block/stack 扩展
      - 提供错误可诊断性


  theory:

    formula:

      registry_dispatch:
        expression: |
          f_{pair} = Registry[style](**kwargs)
          y = f_{pair}(*args, **kwargs)

      attribute_proxy:
        expression: |
          attr(OnePairformer, name) = attr(pair_impl, name)\ \text{if local attr missing}

    variables:

      style:
        name: PairformerStyle
        description: Pairformer 风格键

      Registry:
        name: PairformerRegistry
        description: 风格到实现类映射

      pair_impl:
        name: ConcretePairformer
        description: 被实例化的 Pairformer 实现


  structure:

    architecture: registry_proxy_wrapper

    pipeline:

      - name: StyleValidation
        operation: check_style

      - name: ImplementationInstantiation
        operation: create_pairformer_impl

      - name: ForwardPassthrough
        operation: delegate_call

      - name: AttributeDelegation
        operation: fallback_to_inner_module


  interface:

    parameters:

      style:
        type: str
        description: Pairformer 实现名称

      kwargs:
        type: dict
        description: 构造目标 Pairformer 参数

    inputs:

      args:
        type: tuple
        description: 前向透传参数

      kwargs:
        type: dict
        description: 前向透传关键字参数

    outputs:

      output:
        type: TensorOrTuple
        description: Pairformer 输出


  types:

    TensorOrTuple:
      description: 具体 Pairformer 定义的返回结构


  implementation:

    framework: pytorch

    code: |

      _PAIRFORMER_REGISTRY = {
          # "ProtenixPairformerBlock": ProtenixPairformerBlock,
          # "ProtenixPairformerStack": ProtenixPairformerStack,
      }

      class OnePairformer(nn.Module):
          def __init__(self, style: str, **kwargs):
              super().__init__()
              if style not in _PAIRFORMER_REGISTRY:
                  raise NotImplementedError(f"Unknown style: {style}")
              self.Pairformer = _PAIRFORMER_REGISTRY[style](**kwargs)

          def forward(self, *args, **kwargs):
              return self.Pairformer(*args, **kwargs)

          def __getattr__(self, name):
              try:
                  return super().__getattr__(name)
              except AttributeError:
                  return getattr(self.Pairformer, name)


  skills:

    build_pairformer_dispatcher:

      description: 构建统一 Pairformer 分发器

      inputs:
        - style
        - kwargs

      prompt_template: |

        构建 OnePairformer 模块。

        参数：
        style = {{style}}
        kwargs = {{kwargs}}

        要求：
        使用注册表路由并支持属性代理。


    diagnose_pairformer_dispatcher:

      description: 分析 Pairformer 分发层的可用性问题

      checks:
        - empty_pairformer_registry
        - unknown_style
        - missing_implementation_import
        - attribute_proxy_collision


  knowledge:

    usage_patterns:

      modular_pairformer_entry:

        pipeline:
          - SelectStyle
          - InstantiateOnePairformer
          - DelegateForward

      integration_with_msa:

        pipeline:
          - ProtenixMSABlock
          - OnePairformer
          - PairRepresentationUpdate


    hot_models:

      - model: ProtenixPairformerBlock
        year: 2024
        role: 预期注册的基础块
        architecture: pairformer_block

      - model: ProtenixPairformerStack
        year: 2024
        role: 预期注册的堆栈版本
        architecture: stacked_pairformer


    best_practices:

      - 确保注册表和导入语句保持一致。
      - 在 config 中显式声明 style。
      - 为 style->class 映射添加单元测试。


    anti_patterns:

      - 注册表为空仍将模块接入主训练流程。
      - 依赖动态字符串拼装导入而不做白名单限制。


    paper_references:

      - title: "Design Patterns: Elements of Reusable Object-Oriented Software"
        authors: Gamma et al.
        year: 1994


  graph:

    is_a:
      - NeuralNetworkComponent
      - FactoryWrapper

    part_of:
      - PairformerModuleSystem

    depends_on:
      - RegistryPattern
      - ProtenixPairformerBlock
      - ProtenixPairformerStack

    variants:
      - OneMSA
      - OneLinear
      - OneProcessor

    used_in_models:
      - AF3-style Pair Pipelines
      - Protenix Architectures
      - Structure Prediction Prototypes

    compatible_with:

      inputs:
        - TensorOrTuple

      outputs:
        - TensorOrTuple