component:

  meta:
    name: OneSample
    alias: SamplerFactoryRouter
    version: 1.0
    domain: architecture_design
    category: module_registry
    subcategory: dynamic_router
    author: OneScience
    tags:
      - router
      - factory_pattern
      - sampling_registry
      - neural_operator

  concept:

    description: >
      `OneSample` 是一个全局的中央路由工厂类，通过集中管理字典 `_SAMPLER_REGISTRY` 统一包装并导出了
      整个 Pangu-Weather、FuXi、Xihe 等不同气象大模型（或者图形空间结构）中采用的空间分辨率降温/升尺度组件（采样器）。
      用户或网络配置文件只需依靠一个字符串 `style`（例如 "PanguDownSample2D" 或 "FuxiUpSample"）就能盲载入所需的下/上采样架构逻辑。

    intuition: >
      在模块式的网络架构实验室中，不同的实验往往涉及置换网格采样的策略（例如尝试把盘古模型的 PixelShuffle 上采样更换为伏羲大模型的反卷积上采样来对比效果差异）。
      通过建立这样一个门面类，可以把强耦合的高级类引用彻底解耦成配置列表中的一项纯字符串参数，大大降低了改写成本以及系统框架集成的难度。

    problem_it_solves:
      - 提供一站式反转、抽象多子系统间的超分、降分解构器调用差异痛点。
      - 防止直接修改顶级配置架构引发的复杂类树状冲突引发系统崩溃。
      - 从统一接驳端保障传参（`**kwargs`）对所有被注册变体的透明化代理渗透能力。

  theory:

    formula:
      operator_mapping:
        expression: |
          \mathcal{S}_{select} = \Omega(\text{style}) 
          \text{Output} = \mathcal{S}_{select}(\mathbf{X}_{in}; \text{kwargs})

    variables:
      \Omega:
        name: FactorRegistry
        description: 映射整个可用采样方法的工厂注册表静态映射列表字典

      \text{style}:
        name: StrategyKey
        description: 代表特定模型物理场变换方法的关键字标识符

  structure:

    architecture: registry_factory_pattern

    pipeline:
      - name: KeywordValidation
        operation: "Check if `style` is registered in `_SAMPLER_REGISTRY`"
      - name: LazyInstantiation
        operation: "Initialize targeting instance: `_SAMPLER_REGISTRY[style](**kwargs)`"
      - name: ParameterProxy
        operation: "Call `forward(...)` to pass through all data transparently."

  interface:

    parameters:

      style:
        type: str
        description: 指定降维度或者提升采样物理层的具体实现指代代码

      kwargs:
        type: dict
        description: 基于所选模型采样器的任意必要参数群（如 `in_dim`, `out_chans` 或者 `input_resolution` 设定组合）

    inputs:
      args:
        type: Any
        description: 代理传输进去的特定张量参数数据块组合

    outputs:
      result:
        type: Any
        description: 返回由被投射委托物理模型最终进行完成缩放计算后送出的形变张量块结果

  implementation:

    framework: pytorch

    code: |
      from torch import nn
      
      from .pangudownsample2d import PanguDownSample2D
      from .panguupsample2d import PanguUpSample2D
      from .pangudownsample3d import PanguDownSample3D
      from .panguupsample3d import PanguUpSample3D
      from .SpatialGraphDownsample import SpatialGraphDownsample
      from .SpatialGraphUpsample import SpatialGraphUpsample
      from .fuxidownsample import FuxiDownSample
      from .fuxiupsample import FuxiUpSample
      from .xiheupsample import XiheUpSample
      
      _SAMPLER_REGISTRY = {
          "PanguDownSample2D": PanguDownSample2D,
          "PanguDownSample3D": PanguDownSample3D,
          "PanguUpSample2D": PanguUpSample2D,
          "PanguUpSample3D": PanguUpSample3D,
          "SpatialGraphDownsample": SpatialGraphDownsample,
          "SpatialGraphUpsample": SpatialGraphUpsample,
          "FuxiUpSample": FuxiUpSample,
          "FuxiDownSample": FuxiDownSample,
          "XiheUpSample":XiheUpSample,
      }
      
      class OneSample(nn.Module):
          """OneSample module for sampling operations."""
         
          def __init__(self, style: str, **kwargs):
              super().__init__()
      
              if style not in _SAMPLER_REGISTRY:
                  raise NotImplementedError(f"Unknown style: {style}")
              
              self.Sampler = _SAMPLER_REGISTRY[style](**kwargs)
              
          def forward(self, *args, **kwargs):
              """
              前向传播。
              """
              return self.Sampler(*args, **kwargs)
      

  skills:

    build_onesample:

      description: 构建支持物理约束的三维/二维降维或插值组件，整合上下文环境与特征通道

      inputs:
        - input_resolution
        - output_resolution
        - in_dim
        - out_dim

      prompt_template: |

        构建名为 OneSample 的气象特征采样模块。

        参数：
        输入分辨率 = {{{input_resolution}}}
        输出分辨率 = {{{output_resolution}}}
        特征维度 = {{{in_dim}}}
        预期输出维度 = {{{out_dim}}}

        要求：
        必须严格遵守该网络结构的物理特征（例如三维气压层分离、拓扑点云近邻不损失等）恒定映射规律。


    diagnose_tensor_shape:

      description: 调试在不同尺度缩放或维数跳转（如 .permute 或 .reshape 等多级重组）时出现的维度不匹配错误

      checks:
        - shape_mismatch_at_boundaries
        - incorrect_permute_strides
        - loss_of_physical_meaning (例如跨气压层或跨时间维的污染混合)


  knowledge:

    usage_patterns:

      spatial_scaling_framework:
        description: 控制多尺度空间特征提取的标准管线
        pipeline:
          - Extract_Macro_Features (利用DownSample提取低频气候抽象)
          - Message_Passing (中心GNN或Transformer处理)
          - Interpolate_Back (利用UpSample恢复至高频物理网格)
          
      multiscale_processor:
        pipeline:
          - Encoder_Block
          - DownSample_Layer
          - Decoder_Block
          - UpSample_Layer


    hot_models:

      - model: Pangu-Weather
        year: 2023
        role: 提供基于地球表面的 3D Patch Merging 的空间降维/升维范式
        architecture: 3D Earth-Specific Transformer

      - model: GraphCast
        year: 2023
        role: 提供基于 Mesh 的不规则点云抽象以及边重构拓扑网络
        architecture: Hierarchical Graph Neural Network

      - model: FuXi
        year: 2023
        role: 提供基于经典可变形卷积和群归一化的级联采样结构
        architecture: Cascaded Swin-Transformer + CNN 


    best_practices:

      - 运用 _SAMPLER_REGISTRY 工厂字典实现对具体模型的解耦，便于调用。
      - 必须保证上采样输出与同层级下采样输出维度与分辨率完全匹配以备特征融合。
      - 所有的池化步幅和卷积核需要匹配地球环面展开特性（极点、赤道），处理由于180°与360°分辨率的不整除造成的尺寸零头。


    anti_patterns:

      - 硬编码网络实例到采样控制流中，导致对新的诸如 Graph 点云数据扩展极度困难。
      - 不考虑任何物理约束的简单 AdaptiveAvgPool2d 会让复杂地理特征严重失真。
      - 忽略对多层级气压、高度、地表层的数据异构型差异盲目共用池化算子。


    paper_references:

      - title: "Pangu-Weather: A 3D High-Resolution Model for Fast and Accurate Global Weather Forecast"
        authors: Bi et al.
        year: 2023

      - title: "GraphCast: Learning skillful medium-range global weather forecasting"
        authors: Lam et al.
        year: 2023

      - title: "FuXi: A cascade machine learning forecasting system for 15-day global weather forecast"
        authors: Chen et al.
        year: 2023

  graph:
    is_a:
      - FactoryModule
      - Dispatcher
    part_of:
      - StructuralAPI
      - SpatialResolutionManager
    depends_on:
      - PanguDownSample2D
      - FuxiDownSample
      - SpatialGraphDownsample
    compatible_with:
      - YAML/JSON Configuration parsers