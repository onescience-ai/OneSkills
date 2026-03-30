component:

  meta:
    name: OneFourier
    alias: FourierLayerRouter
    version: 1.0
    domain: architecture_design
    category: module_registry
    subcategory: dynamic_router
    author: OneScience
    tags:
      - router
      - factory_pattern
      - fourier_registry
      - neural_operator

  concept:

    description: >
      `OneFourier` 是整个 `fourier` 物理算子模块家族的总路由中心。由于傅里叶神经算子派系林立 
      (包含 FNO，Factorized FNO，Geo-FNO，Group-FNO 及 Multi-Wavelet 等)，不同的物理 PDEs 和网格几何
      往往需要切换不同的神经算子作为核心处理器。通过维护 `_FOURIER_REGISTRY` 注册表，`OneFourier` 
      实现了算子调用的彻底解耦——外部模型只需传入一个代表算子名称的字符串标识（`style`），即可动态载入底层张量操作逻辑。

    intuition: >
      这类似于一个万能的工具箱插座设计（Factory Router）。在自动化架构搜索引擎（AutoML）中，或
      直接读取由 YAML 解析出的超参数字典构建模型时，硬编码某一种具体的 FNO 会使代码极化且难以扩展。
      配置此工厂类后，切换 `GSpectralConv2d` (用于旋转对称系统) 和 `FFNOSpectralConv2d` (针对高计算效率) 
      仅仅是更改配置文件里的一个 key 那么简单。

    problem_it_solves:
      - 硬编码类引入带来的强耦合性和文件间高频合并冲突。
      - 提供可被配置文件 (YAML/JSON) 直接反序列化和执行的高层接口。
      - 充当安全屏障，对不存在的、拼写错误的算子请求抛出严格 `NotImplementedError`。

  theory:

    formula:

      operator_mapping:
        expression: |
          \mathcal{F}_{select} = \Omega(\text{style}) 
          \text{Output} = \mathcal{F}_{select}(\mathbf{X}_{in}; \theta)

    variables:
      \Omega:
        name: FactoryRegistry
        description: 映射整个可用基层的工厂注册表字典 `_FOURIER_REGISTRY`
      
      \text{style}:
        name: LayerStyleKey
        description: 对应具体层级的选择键值（如 `"FNOSpectralConv3d"`）

  structure:

    architecture: registry_factory_pattern

    pipeline:
      - name: KeywordEvaluation
        operation: "Check if `style` in `_FOURIER_REGISTRY`"
      - name: DynamicInstantiation
        operation: "Init `_FOURIER_REGISTRY[style](**kwargs)`"
      - name: ForwardProxy
        operation: "Proxy inputs via `self.fourier_layer(*args, **kwargs)`"

  interface:

    parameters:

      style:
        type: str
        description: 精确映射到所需傅里叶算子类的字符串键。
      
      kwargs:
        type: dict
        description: 传递给目标层的所有必要参数 (如 `in_channels`, `modes1`, 等)

    inputs:
      args:
        type: Any
        description: 代理转发到目标前向传播的物理场或其他输入张量

    outputs:
      result:
        type: Tensor
        description: 由目标频域物理算子返回的处理结果

  implementation:

    framework: pytorch

    code: |
      import torch
      from torch import nn
      
      from .fno_layers import SpectralConv1d as FNOSpectralConv1d
      from .fno_layers import SpectralConv2d as FNOSpectralConv2d
      from .fno_layers import SpectralConv3d as FNOSpectralConv3d
      
      from .ffno_layers import SpectralConv1d as FFNOSpectralConv1d
      from .ffno_layers import SpectralConv2d as FFNOSpectralConv2d
      from .ffno_layers import SpectralConv3d as FFNOSpectralConv3d
      
      from .geo_spectral import GeoSpectralConv2d, GeoSpectralConv3d
      from .group_spectral import GSpectralConv2d, GSpectralConv3d
      
      from .WaveletFourierKernel import WaveletFourierKernel1D, WaveletFourierKernel2D, WaveletFourierKernel3D
      from .WaveletSpatialKernel import WaveletSpatialKernel2D, WaveletSpatialKernel3D
      from .MultiWaveletTransform import MultiWaveletTransform1D, MultiWaveletTransform2D, MultiWaveletTransform3D
      # 构建统一的注册表
      _FOURIER_REGISTRY = {
          "FNOSpectralConv1d": FNOSpectralConv1d,
          "FNOSpectralConv2d": FNOSpectralConv2d,
          "FNOSpectralConv3d": FNOSpectralConv3d,
          "FFNOSpectralConv1d": FFNOSpectralConv1d,
          "FFNOSpectralConv2d": FFNOSpectralConv2d,
          "FFNOSpectralConv3d": FFNOSpectralConv3d,
          "GeoSpectralConv2d": GeoSpectralConv2d,
          "GeoSpectralConv3d": GeoSpectralConv3d,
          "GSpectralConv2d": GSpectralConv2d,
          "GSpectralConv3d": GSpectralConv3d,
          "WaveletFourierKernel1D": WaveletFourierKernel1D,
          "WaveletFourierKernel2D": WaveletFourierKernel2D,
          "WaveletFourierKernel3D": WaveletFourierKernel3D,
          "WaveletSpatialKernel2D": WaveletSpatialKernel2D,
          "WaveletSpatialKernel3D": WaveletSpatialKernel3D,
          "MultiWaveletTransform1D": MultiWaveletTransform1D,
          "MultiWaveletTransform2D": MultiWaveletTransform2D,
          "MultiWaveletTransform3D": MultiWaveletTransform3D,
      }
      
      class OneFourier(nn.Module):
          def __init__(self, style: str, **kwargs):
              super().__init__()
      
              if style not in _FOURIER_REGISTRY:
                  raise NotImplementedError(
                      f"Unknown style: '{style}'. Available options are: {list(_FOURIER_REGISTRY.keys())}"
                  )
              
              # 实例化具体的傅里叶层
              self.fourier_layer = _FOURIER_REGISTRY[style](**kwargs)
      
          def forward(self, *args, **kwargs):
              """
              前向传播。
              """
              return self.fourier_layer(*args, **kwargs)

  skills:

    build_fourier_router:
      description: 构建支持基于字典或枚举的神经算子控制门与路由分发器
      inputs:
        - style
        - kwargs
      prompt_template: |
        创建 OneFourier 工厂级模块：
        核心参数：算子风格（style={{style}}）
        要求：利用 _FOURIER_REGISTRY 返回准确的算子初始化类，遇到不在表内的类型必须严厉报错。

    diagnose_fourier_router:
      description: 排查在反射与载入子模型时发生的解耦分离问题
      checks:
        - unregistered_operator_fallback
        - kwarg_schema_mismatch
        - infinite_recursion_on_dispatch

  knowledge:

    usage_patterns:
      automated_hyperparameter_sweep:
        pipeline:
          - Load Search Space (e.g., style=["FNOSpectralConv2d", "FFNOSpectralConv2d", "GSpectralConv2d"])
          - Traverse and instantiate directly via OneFourier(style=type, modes=16, ...)

    hot_models:
      - model: Auto-PyTorch / AutoML
        year: 2021
        role: 推崇在深度学习管线内通过统一字典进行层分发的实验控制哲学
        architecture: Model Registry
      - model: MMCV
        year: 2018
        role: 全面利用 Registry 模式进行组件即插即用的前沿框架
        architecture: Registry API

    best_practices:
      - 字典化参数传递：确保不同类型的 FNO 参数可以在超参数管理体系中标准化。
      - 添加新算子时，必须且唯一必须修改 _FOURIER_REGISTRY 字典进行注册。

    anti_patterns:
      - 在 OneFourier 的 orward 中增加额外的定制逻辑。路由层的职责应保持绝对单一。
      - 抑制 NotImplementedError 进行“默认”层回退，这会在科学计算实验中掩盖严重的配置拼写错误。

    paper_references:
      - title: "Neural Architecture Search: A Survey"
        authors: Elsken et al.
        year: 2019
      - title: "Design Patterns: Elements of Reusable Object-Oriented Software"
        authors: Gamma et al.
        year: 1994


  graph:
    is_a:
      - FactoryModule
      - Dispatcher
    part_of:
      - StructuralAPI
    depends_on:
      - FNOSpectralConv
      - FFNOSpectralConv
      - GeoSpectralConv
      - GSpectralConv
      - WaveletFourierKernel
      - WaveletSpatialKernel
      - MultiWaveletTransform
    compatible_with:
      - YAML/JSON Configuration parsers