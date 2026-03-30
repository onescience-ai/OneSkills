component:

  meta:
    name: OneEdge
    alias: EdgeFactory
    version: 1.0
    domain: deep_learning
    category: graph_neural_network
    subcategory: module_dispatcher
    author: OneScience
    license: Apache-2.0
    tags:
      - edge
      - registry
      - factory_pattern
      - gnn
      - wrapper


  concept:

    description: >
      OneEdge 提供统一的边更新模块调用接口，通过 style 参数从注册表中实例化具体边更新实现。
      前向过程采用透传方式，将输入参数原样传递给被选中的边更新器。

    intuition: >
      该模块将“边更新策略选择”从训练主干中解耦出来，像插件系统一样根据配置切换实现，
      方便在不同图网络结构中复用和扩展。

    problem_it_solves:
      - 统一边更新组件实例化入口
      - 通过注册表简化风格切换与实验管理
      - 对未知 style 提供明确错误提示
      - 保持调用签名灵活（*args, **kwargs）以适配不同实现


  theory:

    formula:

      edge_dispatch:
        expression: |
          f_{edge} = Registry[style](**kwargs)
          y = f_{edge}(*args, **kwargs)

    variables:

      style:
        name: EdgeStyle
        description: 用于选择边更新器的风格名称

      Registry:
        name: EdgeRegistry
        description: 风格名称到边更新类的映射

      args:
        name: ForwardArgs
        description: 传递给具体边更新器的输入参数


  structure:

    architecture: registry_based_wrapper

    pipeline:

      - name: StyleCheck
        operation: validate_style_exists

      - name: UpdaterBuild
        operation: instantiate_registered_edge_module

      - name: ArgumentPassthrough
        operation: delegate_forward_call


  interface:

    parameters:

      style:
        type: str
        description: 边更新实现名称

      kwargs:
        type: dict
        description: 实例化边更新实现所需参数

    inputs:

      args:
        type: tuple
        description: 前向透传参数（通常包含 efeat, nfeat, graph）

      kwargs:
        type: dict
        description: 前向透传关键字参数

    outputs:

      output:
        type: TensorOrTuple
        description: 具体边更新实现返回结果


  types:

    TensorOrTuple:
      description: 由具体边更新实现定义的返回结构


  implementation:

    framework: pytorch

    code: |

      import torch
      import torch.nn as nn

      from .mesh_edge_block import MeshEdgeBlock

      _EDGE_REGISTRY = {
          "MeshEdgeBlock": MeshEdgeBlock,
      }

      class OneEdge(nn.Module):
          def __init__(self, style: str, **kwargs):
              super().__init__()
              if style not in _EDGE_REGISTRY:
                  raise NotImplementedError(
                      f"Unknown edge style: '{style}'. Available: {list(_EDGE_REGISTRY.keys())}"
                  )

              self.edge_updater = _EDGE_REGISTRY[style](**kwargs)

          def forward(self, *args, **kwargs):
              return self.edge_updater(*args, **kwargs)


  skills:

    build_edge_dispatcher:

      description: 构建统一边更新模块分发器

      inputs:
        - style
        - kwargs

      prompt_template: |

        构建 OneEdge 模块。

        参数：
        style = {{style}}
        kwargs = {{kwargs}}

        要求：
        采用注册表方式路由到对应边更新实现，并在未知 style 时抛错。


    diagnose_edge_dispatcher:

      description: 分析边更新分发层的配置和扩展问题

      checks:
        - unknown_edge_style
        - missing_registry_for_new_edge_module
        - argument_passthrough_mismatch


  knowledge:

    usage_patterns:

      gnn_modular_design:

        pipeline:
          - ConfigureStyle
          - InstantiateOneEdge
          - ForwardPassthrough

      edge_strategy_ablation:

        pipeline:
          - RegisterMultipleEdgeBlocks
          - SwitchStyleFromConfig
          - CompareMetrics


    hot_models:

      - model: MeshEdgeBlock
        year: 2023
        role: 当前默认边更新实现
        architecture: residual_edge_mlp


    best_practices:

      - 保持注册表键名与配置文件中的 style 完全一致。
      - 新增边更新实现后同步更新注册表和可用列表提示。
      - 在 forward 透传层保留最小逻辑，避免引入额外副作用。


    anti_patterns:

      - 使用硬编码 if-else 链替代注册表，扩展成本高。
      - 捕获 NotImplementedError 后默认回退某实现，导致实验结果不透明。


    paper_references:

      - title: "Design Patterns: Elements of Reusable Object-Oriented Software"
        authors: Gamma et al.
        year: 1994


  graph:

    is_a:
      - NeuralNetworkComponent
      - FactoryWrapper

    part_of:
      - EdgeModuleSystem
      - GraphNeuralNetworkBackbone

    depends_on:
      - RegistryPattern
      - MeshEdgeBlock

    variants:
      - OneNode
      - OneProcessor
      - OneAFNO

    used_in_models:
      - GraphCast Pipelines
      - MeshGraph Workflows
      - Modular GNN Systems

    compatible_with:

      inputs:
        - EdgeEmbedding
        - NodeEmbedding
        - GraphStructure

      outputs:
        - TensorOrTuple