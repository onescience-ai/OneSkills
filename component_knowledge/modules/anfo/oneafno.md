component:

  meta:
    name: OneAFNO
    alias: AFNOFactory
    version: 1.0
    domain: deep_learning
    category: neural_network
    subcategory: module_dispatcher
    author: OneScience
    license: Apache-2.0
    tags:
      - afno
      - registry
      - factory_pattern
      - module_wrapper
      - pytorch


  concept:

    description: >
      OneAFNO 是 AFNO 模块的统一入口封装，通过字符串 style 在注册表中选择具体实现，
      并将构造参数透传给目标 AFNO 类。该模块为上层模型提供稳定接口，便于后续扩展不同 AFNO 变体。

    intuition: >
      它类似一个“算子路由器”：上层只需要声明想用哪种 AFNO 风格，不需要关心具体类名和导入细节。
      这种方式降低了耦合，便于在实验中快速切换实现。

    problem_it_solves:
      - 统一 AFNO 变体实例化入口
      - 通过注册表机制降低调用侧与实现侧耦合
      - 对未知 style 显式抛错，提高配置可诊断性
      - 便于后续新增 AFNO 实现并无缝接入


  theory:

    formula:

      registry_dispatch:
        expression: |
          f_{afno} = Registry[style](**kwargs)
          y = f_{afno}(x)

    variables:

      style:
        name: OperatorStyle
        description: 字符串键，用于检索 AFNO 实现

      Registry:
        name: AFNORegistry
        description: 从风格名称映射到具体 AFNO 类的字典

      x:
        name: InputTensor
        shape: [batch, H, W, C]
        description: 输入到 AFNO 模块的网格表示


  structure:

    architecture: registry_based_wrapper

    pipeline:

      - name: StyleValidation
        operation: check_style_in_registry

      - name: InstanceCreation
        operation: build_target_module_with_kwargs

      - name: ForwardDelegation
        operation: pass_input_to_selected_module


  interface:

    parameters:

      style:
        type: str
        description: 要实例化的 AFNO 实现名称

      kwargs:
        type: dict
        description: 透传给目标 AFNO 构造函数的参数

    inputs:

      x:
        type: GridEmbedding
        shape: [batch, H, W, C]
        dtype: float32
        description: AFNO 输入张量

    outputs:

      output:
        type: GridEmbedding
        shape: [batch, H, W, C]
        description: 目标 AFNO 变体的前向输出


  types:

    GridEmbedding:
      shape: [batch, H, W, C]
      description: 二维网格 embedding 表示


  implementation:

    framework: pytorch

    code: |

      from torch import nn
      from .fourcastnetafno import FourCastNetAFNO2D

      _AFNO_REGISTRY = {
          "FourCastNetAFNO2D": FourCastNetAFNO2D,
      }

      class OneAFNO(nn.Module):
          def __init__(self, style: str, **kwargs):
              super().__init__()

              if style not in _AFNO_REGISTRY:
                  raise NotImplementedError(f"Unknown style: {style}")

              self.afno = _AFNO_REGISTRY[style](**kwargs)

          def forward(self, x):
              return self.afno(x)


  skills:

    build_afno_dispatcher:

      description: 构建基于注册表的 AFNO 统一封装层

      inputs:
        - style
        - kwargs

      prompt_template: |

        构建 OneAFNO 模块。

        参数：
        style = {{style}}
        kwargs = {{kwargs}}

        要求：
        若 style 不在注册表中，必须抛出 NotImplementedError。


    diagnose_dispatcher:

      description: 检查 AFNO 分发层中的配置与注册问题

      checks:
        - unknown_style_key
        - missing_registry_entry_for_new_module
        - mismatched_kwargs_for_target_constructor


  knowledge:

    usage_patterns:

      modular_backbone:

        pipeline:
          - ConfigParse
          - OneAFNO(style, **kwargs)
          - ForwardCall

      experimental_switching:

        pipeline:
          - RegisterNewAFNO
          - SelectByStyle
          - BenchmarkComparison


    hot_models:

      - model: FourCastNetAFNO2D
        year: 2022
        role: 当前注册表中的默认 AFNO 变体
        architecture: spectral_operator


    best_practices:

      - 使用集中注册表维护风格名称，避免业务侧硬编码类导入。
      - 新增 AFNO 变体时优先增加单元测试验证 style 路由。
      - 保持 style 名称语义稳定，减少配置兼容问题。


    anti_patterns:

      - 在多个文件重复维护风格映射，导致注册不一致。
      - 捕获未知 style 异常后静默降级，掩盖配置错误。


    paper_references:

      - title: "Design Patterns: Elements of Reusable Object-Oriented Software"
        authors: Gamma et al.
        year: 1994


  graph:

    is_a:
      - NeuralNetworkComponent
      - FactoryWrapper

    part_of:
      - AFNOModuleSystem

    depends_on:
      - RegistryPattern
      - FourCastNetAFNO2D

    variants:
      - OneAttention
      - OneNode
      - OneEdge

    used_in_models:
      - Modular AFNO Backbones
      - Weather Forecasting Pipelines
      - Research Prototypes

    compatible_with:

      inputs:
        - GridEmbedding

      outputs:
        - GridEmbedding