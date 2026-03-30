component:
  meta:
    name: FourCastNetFuser
    中文名称: FourCastNet 特征融合模块
    别名: AFNO-Transformer Block, FourCastNet Block
    version: 1.0
    领域: 深度学习/气象AI
    分类: 神经网络组件
    子类: 特征融合层/Transformer Block
    作者: OneScience
    tags:
      - 气象AI
      - AFNO
      - Transformer
      - 频域混合
      - 全球天气预报

  concept:
    描述: >
      FourCastNetFuser 是 FourCastNet 模型的核心 Transformer Block，使用 AFNO（Adaptive Fourier Neural Operator）
      替代传统自注意力机制进行空间混合，结合 MLP 进行通道混合，通过"频域全局卷积 + 通道变换"的方式高效建模
      全球高分辨率气象场的长程空间依赖与多变量耦合关系。
    直觉理解: >
      可以把它想象成一个"频谱分析仪 + 特征提炼器"的组合：先将气象场转换到频率域，在频域中用共享的神经网络
      对不同尺度的波动模式进行加权和稀疏化（就像调音台调节不同频段的音量），然后转回空间域；接着用 MLP
      对每个位置的多变量特征进行非线性提炼。这种设计让模型能以 O(N log N) 的复杂度捕捉全球范围的大气相互作用。
    解决的问题:
      - 高分辨率全局依赖建模: 在 0.25° 分辨率（721×1440 网格）上，传统自注意力的 O(N²) 复杂度难以承受，
        而标准卷积需要极深的网络才能覆盖全球感受野。AFNO 通过频域操作实现 O(N log N) 的全局混合。
      - 多尺度结构捕捉: 大气场包含从行星尺度（数千公里）到中小尺度（数十公里）的多尺度结构，频域表示
        天然适合建模这种多尺度特性，软阈值稀疏化能自适应地保留重要频率、抑制噪声。
      - 计算效率与可扩展性: 相比全局自注意力，AFNO 在保持全局视野的同时大幅降低计算成本，使得在有限
        GPU 资源下训练和推理高分辨率全球模型成为可能。

  theory:
    核心公式:
      AFNO空间混合:
        表达式: |
          Z = DFT(X)
          Z̃ = S_λ(MLP(Z))
          Y = IDFT(Z̃) + X
        变量说明:
          X:
            名称: 输入token网格
            形状: [B, H, W, C]
            描述: B为批次大小，H×W为patch网格尺寸（如90×180），C为嵌入维度（如768）
          Z:
            名称: 频域表示
            形状: [B, H, W, C]
            描述: 对空间维度H×W进行2D离散傅里叶变换后的复数张量
          MLP:
            名称: 频域共享MLP
            形状: 权重为块对角矩阵
            描述: 在所有频率点共享的两层感知机，用于频域特征变换
          S_λ:
            名称: 软阈值函数
            形状: 逐元素操作
            描述: S_λ(x) = sign(x)·max(|x|-λ, 0)，用于频域稀疏化，λ为阈值参数
          Y:
            名称: 输出特征
            形状: [B, H, W, C]
            描述: 逆傅里叶变换回空间域后与输入残差相加的结果

      MLP通道混合:
        表达式: |
          MLP(x) = W₂·GELU(W₁·x + b₁) + b₂
        变量说明:
          x:
            名称: 输入token特征
            形状: [*, C]
            描述: 逐token处理，C为输入通道数
          W₁:
            名称: 第一层权重
            形状: [C, mlp_ratio×C]
            描述: 扩展层权重，mlp_ratio通常为4
          W₂:
            名称: 第二层权重
            形状: [mlp_ratio×C, C]
            描述: 压缩层权重，将隐层映射回原始维度

  structure:
    架构类型: Transformer Block（AFNO变体）
    计算流程:
      - 输入归一化（LayerNorm）
      - AFNO频域空间混合（2D DFT → 频域MLP → 软阈值 → 2D IDFT）
      - 第一次残差连接（可选双残差模式）
      - 输入归一化（LayerNorm）
      - MLP通道混合（线性扩展 → GELU → 线性压缩）
      - DropPath随机深度正则化
      - 第二次残差连接
    计算流程图: |
      输入 x [B,H,W,C]
        ↓
      LayerNorm → x_norm1
        ↓
      AFNO频域混合:
        2D DFT(x_norm1) → Z [频域]
        → 共享MLP(Z) → Z'
        → 软阈值S_λ(Z') → Z̃ [稀疏化]
        → 2D IDFT(Z̃) → x_afno
        ↓
      [双残差模式] x_afno + x → x_skip1
        ↓
      LayerNorm(x_skip1) → x_norm2
        ↓
      MLP通道混合:
        Linear(4C) → GELU → Linear(C) → x_mlp
        ↓
      DropPath(x_mlp)
        ↓
      x_mlp + x_skip1 → 输出 [B,H,W,C]

  interface:
    参数:
      dim:
        类型: int
        默认值: 768
        描述: 输入token的通道数（嵌入维度），对应气象场patch嵌入后的特征维度
      mlp_ratio:
        类型: float
        默认值: 4.0
        描述: MLP隐层相对于dim的扩展倍数，控制通道混合的容量
      drop:
        类型: float
        默认值: 0.0
        描述: MLP的Dropout比例，用于正则化
      drop_path:
        类型: float
        默认值: 0.0
        描述: Stochastic Depth的比例，随机丢弃整个残差分支以正则化深层网络
      act_layer:
        类型: nn.Module
        默认值: nn.GELU
        描述: MLP的激活函数类型
      norm_layer:
        类型: nn.Module
        默认值: nn.LayerNorm
        描述: 归一化层类型
      double_skip:
        类型: bool
        默认值: true
        描述: 是否启用双残差连接，True时AFNO输出先与输入相加再送入MLP，有助于深层网络梯度传播
      num_blocks:
        类型: int
        默认值: 8
        描述: 传递给AFNO的通道分块数，控制频域MLP的块对角结构
      sparsity_threshold:
        类型: float
        默认值: 0.01
        描述: 软阈值参数λ，控制频域稀疏化程度，抑制不重要频率
      hard_thresholding_fraction:
        类型: float
        默认值: 1.0
        描述: 频率保留比例，1.0表示保留所有频率，<1.0则硬截断高频部分
    输入:
      x:
        类型: Tensor
        形状: [B, H, W, C]
        描述: 输入token网格，B为批次，H×W为patch网格尺寸（如90×180对应720×1440原始网格按8×8划分），C为嵌入维度
    输出:
      out:
        类型: Tensor
        形状: [B, H, W, C]
        描述: 输出token网格，形状与输入完全一致，经过频域空间混合和通道混合后的特征表示

  types:
    TokenGrid:
      形状: [B, H, W, C]
      描述: Patch token网格，B为批次大小，H×W为空间patch网格尺寸，C为嵌入通道数。在FourCastNet中，原始721×1440气象场按8×8 patch划分后得到约90×180的token网格

  constraints:
    shape_constraints:
      - 规则: H和W必须适合进行2D FFT
        描述: AFNO层使用2D离散傅里叶变换，要求空间维度H和W能够高效进行FFT运算
      - 规则: C % num_blocks == 0
        描述: 嵌入维度C必须能被通道分块数num_blocks整除，以支持块对角MLP结构
    parameter_constraints:
      - 规则: 0 <= drop <= 1
        描述: Dropout比例必须在0到1之间
      - 规则: 0 <= drop_path <= 1
        描述: DropPath比例必须在0到1之间
      - 规则: mlp_ratio > 0
        描述: MLP扩展比例必须为正数
      - 规则: sparsity_threshold >= 0
        描述: 软阈值参数必须非负
    compatibility_rules:
      - 输入类型: TokenGrid
        输出类型: TokenGrid
        描述: 输入输出形状完全一致，支持堆叠多层FourCastNetFuser构建深层网络

  implementation:
    框架: pytorch
    示例代码: |
      import torch
      import torch.nn as nn
      from onescience.modules.afno.oneafno import OneAFNO
      from onescience.modules.fc.onefc import OneFC

      class FourCastNetFuser(nn.Module):
          def __init__(self, dim=768, mlp_ratio=4., drop=0., drop_path=0.,
                       act_layer=nn.GELU, norm_layer=nn.LayerNorm,
                       double_skip=True, num_blocks=8,
                       sparsity_threshold=0.01, hard_thresholding_fraction=1.0):
              super().__init__()
              self.norm1 = norm_layer(dim)
              self.filter = OneAFNO(style="FourCastNetAFNO2D")
              self.drop_path = DropPath(drop_path) if drop_path > 0. else nn.Identity()
              self.norm2 = norm_layer(dim)
              self.mlp = OneFC(style="FourCastNetFC")
              self.double_skip = double_skip

          def forward(self, x):
              # x: [B, H, W, C]
              residual = x
              x = self.norm1(x)
              x = self.filter(x)  # AFNO频域混合

              if self.double_skip:
                  x = x + residual
                  residual = x

              x = self.norm2(x)
              x = self.mlp(x)  # MLP通道混合
              x = self.drop_path(x)
              x = x + residual
              return x

  usage_examples:
    - 标准FourCastNet Block配置（双残差模式）:
        示例代码: |
          # 典型配置：768维嵌入，4倍MLP扩展，启用双残差
          block = FourCastNetFuser(
              dim=768,
              mlp_ratio=4.0,
              double_skip=True,
              num_blocks=8,
              sparsity_threshold=0.01,
              hard_thresholding_fraction=1.0
          )
          x = torch.randn(2, 90, 180, 768)  # [B, H, W, C]
          out = block(x)  # [2, 90, 180, 768]

    - 堆叠多层构建深层网络:
        示例代码: |
          # FourCastNet主干：12层AFNO-Transformer Block
          backbone = nn.Sequential(*[
              FourCastNetFuser(dim=768, mlp_ratio=4.0, drop_path=0.1*i/12)
              for i in range(12)
          ])
          x = torch.randn(4, 90, 180, 768)
          features = backbone(x)

    - 单残差模式（关闭double_skip）:
        示例代码: |
          # 关闭双残差，使用标准Transformer残差连接
          block = FourCastNetFuser(
              dim=768,
              mlp_ratio=4.0,
              double_skip=False
          )
          x = torch.randn(2, 90, 180, 768)
          out = block(x)

  knowledge:
    应用说明: >
      FourCastNetFuser 属于 Transformer 范式下的特征融合模块，在气象AI建模中扮演主干网络（Backbone）的核心角色。
      该组件通过 AFNO 频域操作替代传统自注意力机制，解决了全球高分辨率气象场建模中的计算复杂度瓶颈问题。
      在领域建模流程中，FourCastNetFuser 位于"特征提取与演化"环节，负责从 patch embedding 后的 token 序列中
      提取多尺度空间依赖和多变量耦合特征，为后续的时间演化预测提供高质量的潜在表示。其核心创新在于将
      Fourier Neural Operator 的思想引入 Transformer 架构，实现了 O(N log N) 复杂度的全局感受野建模。

    热点模型:
      - 模型: FourCastNet
        年份: 2022
        场景: 全球中期天气预报，需要在0.25°高分辨率（721×1440网格）上预测未来1周的20个大气变量
        方案: >
          使用12层堆叠的FourCastNetFuser作为主干网络。输入经8×8 patch划分和线性嵌入后得到90×180×768的token网格，
          每层FourCastNetFuser先通过AFNO在频域进行全局空间混合（捕捉从行星尺度到中尺度的大气波动），再通过MLP
          进行通道混合（建模多变量耦合）。采用双残差连接和LayerNorm增强深层网络的训练稳定性。最终通过线性解码器
          将token映射回原始分辨率的多变量预报场。
        作用: >
          作为时空演化算子的核心，FourCastNetFuser负责学习大气动力学的隐式表示，将当前时刻的全球场映射到6小时后的状态。
          其频域操作天然适合捕捉大气中的波动模式（如Rossby波、重力波），软阈值稀疏化能自适应保留重要尺度、抑制噪声。
        创新: >
          首次在全球天气预报中将AFNO作为Transformer的空间混合器，相比标准自注意力降低4个数量级的计算成本，
          使得在单节点GPU上训练和推理0.25°分辨率模型成为可能。实验表明，在前3天预报中ACC和RMSE可与ECMWF IFS相当，
          且推理速度快5个数量级，支持100-1000成员的大规模集合预报。

      - 模型: ClimaX（气候基础模型）
        年份: 2023
        场景: 跨分辨率、跨变量的通用气候预测任务，包括天气预报、气候降尺度、极端事件检测等
        方案: >
          ClimaX借鉴FourCastNet的AFNO-Transformer架构，但采用预训练-微调范式。在预训练阶段使用多个气候数据集
          （ERA5、CMIP6等）训练通用的大气表示，主干网络同样使用堆叠的AFNO Block进行特征提取。通过变量token化
          和位置编码支持不同分辨率和变量组合的输入。
        作用: >
          FourCastNetFuser类型的AFNO Block在ClimaX中作为通用特征提取器，学习跨数据集、跨任务的共享大气动力学表示。
          频域操作的尺度不变性使其能够处理从粗分辨率气候模拟到高分辨率再分析数据的多样化输入。
        创新: >
          将AFNO-Transformer从单任务预报扩展到多任务基础模型，证明了频域混合机制在气候科学中的通用性和可迁移性。
          通过在大规模异构数据上预训练，AFNO Block学到的表示能够迁移到下游任务，显著降低特定任务的数据需求。

    最佳实践:
      - 双残差连接（double_skip=True）在深层网络（>8层）中能显著改善梯度流动和训练稳定性，建议默认启用
      - 软阈值参数sparsity_threshold建议设置在0.01-0.05之间，过大会丢失重要频率信息，过小则稀疏化效果不明显
      - 对于不同分辨率的输入，需确保patch划分后的H×W维度适合FFT运算，优选2的幂次或高度可分解的尺寸
      - 在多步自回归预报任务中，建议使用两步微调策略（先训练单步，再训练两步）以增强长时间稳定性
      - DropPath比例建议随层深度线性增加（如第i层设为0.1*i/总层数），在深层网络中提供有效正则化
      - 对于极高分辨率输入（>1440×720），可考虑增大patch_size或使用层次化下采样以控制token数量

    常见错误:
      - 忘记对输入进行LayerNorm导致训练不稳定，AFNO对输入分布敏感，必须在频域操作前归一化
      - 将double_skip设为False但未相应调整学习率或层数，可能导致深层网络梯度消失
      - 在小batch size下使用过大的drop_path比例，导致训练方差过大、收敛困难
      - 未考虑FFT的周期性边界条件，对于全球经度方向天然周期，但纬度方向需注意极区处理
      - 在自回归推理中未固定随机种子，导致ensemble成员间差异过大或不可复现

    论文参考:
      - 标题: "FourCastNet: A Global Data-driven High-resolution Weather Model using Adaptive Fourier Neural Operators"
        作者: Pathak et al.
        年份: 2022
        摘要: >
          提出FourCastNet模型，使用AFNO替代自注意力构建全球天气预报系统。在0.25°分辨率ERA5数据上训练，
          实现与ECMWF IFS相当的预报技能，推理速度提升5个数量级。支持大规模集合预报和极端事件预测。

  graph:
    类型关系:
      - Transformer Block
      - 特征融合层
      - 神经网络层
    所属结构:
      - FourCastNet主干网络
      - AFNO-Transformer架构
      - Vision Transformer变体
    依赖组件:
      - OneAFNO（AFNO频域混合层）
      - OneFC（MLP通道混合层）
      - LayerNorm（归一化层）
      - DropPath（随机深度正则化）
    变体组件:
      - 标准Transformer Block（使用自注意力）
      - Swin Transformer Block（使用窗口注意力）
      - FNO Block（纯Fourier Neural Operator）
    使用模型:
      - FourCastNet
      - ClimaX
      - Aurora（微软气象基础模型）
      - Pangu-Weather变体
    类型兼容:
      输入:
        - TokenGrid
      输出:
        - TokenGrid
