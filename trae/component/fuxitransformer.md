component:
  meta:
    name: FuxiTransformer
    中文名称: FuXi Transformer 主干模块
    别名: U-Transformer, FuXi 核心处理模块
    version: 1.0
    领域: 深度学习/气象AI
    分类: 神经网络组件
    子类: Transformer 主干网络
    作者: OneScience
    tags:
      - 气象AI
      - Swin Transformer V2
      - U-Net 结构
      - 多尺度建模
      - 全球天气预报

  concept:
    描述: >
      FuxiTransformer 是 FuXi 模型的核心 Transformer 处理模块，采用"下采样 → Swin Transformer V2 → 上采样"的 U 形结构。
      在低分辨率特征图上进行深层注意力计算以降低计算量，并通过跳跃连接将下采样前的特征与注意力输出拼接后恢复原始分辨率。
    直觉理解: >
      就像用望远镜观察天气系统：先将视野缩小（下采样）以看到更大范围的天气模式，在这个"缩小版"上进行深度分析（Swin Transformer），
      然后再放大回原始分辨率（上采样），同时保留之前记录的细节信息（跳跃连接），从而既能捕捉大尺度结构又不丢失局地细节。
    解决的问题:
      - 计算效率问题: 直接在高分辨率特征图（如 180×360）上进行全局注意力计算成本过高，通过下采样到 90×180 可将计算量降低约 75%
      - 多尺度建模问题: 大气场同时包含行星尺度、天气尺度和中尺度结构，单一分辨率难以兼顾，U-Net 结构通过多尺度路径捕捉不同尺度特征
      - 信息丢失问题: 纯下采样会丢失局地细节，通过跳跃连接保留高分辨率特征，避免上采样时细节模糊

  theory:
    核心公式:
      Scaled_Cosine_Attention:
        表达式: "Attention(Q, K, V) = (cos(Q, K) / τ + B) V"
        变量说明:
          Q:
            名称: 查询矩阵
            形状: "[N_tokens, d_k]"
            描述: 从输入特征线性映射得到的查询向量，N_tokens 为窗口内 token 数量
          K:
            名称: 键矩阵
            形状: "[N_tokens, d_k]"
            描述: 从输入特征线性映射得到的键向量
          V:
            名称: 值矩阵
            形状: "[N_tokens, d_v]"
            描述: 从输入特征线性映射得到的值向量
          "cos(Q, K)":
            名称: 余弦相似度
            形状: "[N_tokens, N_tokens]"
            描述: Q 和 K 之间的余弦相似度矩阵，天然归一化，避免注意力值极端化
          τ:
            名称: 可学习温度标量
            形状: 标量
            描述: 可学习的缩放参数，不同头与层之间不共享，用于控制注意力分布的锐度
          B:
            名称: 相对位置偏置
            形状: "[N_tokens, N_tokens]"
            描述: 基于 log-spaced coordinates 构建的相对位置编码，捕捉空间邻近关系

  structure:
    架构类型: U-Net 式 Transformer 模块
    计算流程:
      - "输入特征 x: (B, embed_dim, lat, lon)，其中 lat, lon 为下采样前的原始分辨率"
      - "下采样 (Down Block): 通过 FuxiDownSample 将空间分辨率降低一半，得到 (B, embed_dim, lat/2, lon/2)"
      - "保存跳跃连接 (shortcut): 将下采样后的特征保存用于后续拼接"
      - "零填充 (ZeroPad): 对特征进行填充使其能被窗口大小整除"
      - "维度转换: 从 (B, C, H, W) 转为 (B, H, W, C) 以适配 Swin Transformer 输入格式"
      - "Swin Transformer V2 处理: 通过 depth 层 Swin V2 块进行窗口化自注意力计算，捕捉局部与跨块相关性"
      - "维度恢复: 从 (B, H, W, C) 转回 (B, C, H, W)"
      - "裁剪 (Crop): 移除之前添加的填充，恢复到下采样后的原始尺寸"
      - "特征拼接: 将 Transformer 输出与 shortcut 在通道维拼接，得到 (B, 2*embed_dim, lat/2, lon/2)"
      - "上采样 (Up Block): 通过 FuxiUpSample 恢复到原始分辨率，输出 (B, embed_dim, lat, lon)"
    计算流程图: |
      输入 x: (B, C, lat, lon)
        ↓
      [Down Block] 下采样
        → (B, C, lat/2, lon/2)
        ↓
      保存 shortcut ←┐
        ↓            │
      [ZeroPad] 填充 │
        ↓            │
      (B, C, pad_lat, pad_lon)
        ↓            │
      维度转换       │
        ↓            │
      [Swin V2 × depth] 窗口注意力
        ↓            │
      维度恢复       │
        ↓            │
      [Crop] 裁剪    │
        ↓            │
      (B, C, lat/2, lon/2)
        ↓            │
      [Concat] ←─────┘
        ↓
      (B, 2C, lat/2, lon/2)
        ↓
      [Up Block] 上采样
        ↓
      输出: (B, C, lat, lon)

  interface:
    参数:
      embed_dim:
        类型: int
        默认值: 1536
        描述: 输入特征的通道数，对应 FuXi 论文中经过 Cube Embedding 后的特征维度
      num_groups:
        类型: "int 或 tuple[int, int]"
        默认值: 32
        描述: GroupNorm 的分组数，用于 Down/Up Block 中的归一化层，传入单个 int 时自动扩展为 2 元组
      input_resolution:
        类型: "tuple[int, int]"
        默认值: "(90, 180)"
        描述: 下采样后的特征图分辨率 (lat, lon)，即 SwinTransformerV2Stage 的输入分辨率，对应论文中从 180×360 下采样到 90×180
      num_heads:
        类型: int
        默认值: 8
        描述: Swin Transformer 的多头注意力头数，控制注意力机制的并行度和表达能力
      window_size:
        类型: "int 或 tuple[int, int]"
        默认值: 7
        描述: 窗口注意力的窗口大小，传入单个 int 时自动扩展为 2 元组，限制注意力计算在局部窗口内以降低复杂度
      depth:
        类型: int
        默认值: 48
        描述: SwinTransformerV2Stage 的 Block 层数，对应 FuXi 论文中的 48 层 Swin Transformer V2 块堆叠
    输入:
      x:
        类型: torch.Tensor
        形状: "[B, embed_dim, lat, lon]"
        描述: 输入特征张量，其中 B 为批次大小，embed_dim 为通道数（默认 1536），lat 和 lon 为下采样前的空间分辨率（约为 input_resolution 的 2 倍，如 180×360）
    输出:
      output:
        类型: torch.Tensor
        形状: "[B, embed_dim, lat, lon]"
        描述: 输出特征张量，分辨率与通道数均与输入保持一致，经过多尺度 Transformer 处理后的高层特征表示

  types:
    FeatureMap:
      形状: "[B, C, H, W]"
      描述: 四维特征图张量，B 为批次大小，C 为通道数，H 和 W 为空间维度（纬度和经度方向的格点数）
    WindowTokens:
      形状: "[B, H, W, C]"
      描述: Swin Transformer 输入格式的特征张量，空间维度在前，通道维度在后，便于窗口划分和注意力计算

  constraints:
    shape_constraints:
      - 规则: "input_resolution[0] + padding_top + padding_bottom 能被 window_size[0] 整除"
        描述: 填充后的纬度方向尺寸必须能被窗口大小整除，以支持窗口划分
      - 规则: "input_resolution[1] + padding_left + padding_right 能被 window_size[1] 整除"
        描述: 填充后的经度方向尺寸必须能被窗口大小整除，以支持窗口划分
      - 规则: "输入 x 的 lat 约为 input_resolution[0] * 2"
        描述: 输入特征的空间分辨率应约为 input_resolution 的 2 倍，因为 Down Block 会进行 2 倍下采样
      - 规则: "输入 x 的 lon 约为 input_resolution[1] * 2"
        描述: 输入特征的经度分辨率应约为 input_resolution 的 2 倍
    parameter_constraints:
      - 规则: "embed_dim > 0 且 embed_dim % num_heads == 0"
        描述: 通道数必须为正数且能被注意力头数整除，以便每个头分配相等的维度
      - 规则: "num_heads > 0"
        描述: 注意力头数必须为正整数
      - 规则: "depth > 0"
        描述: Transformer 层数必须为正整数
      - 规则: "window_size > 0"
        描述: 窗口大小必须为正整数
    compatibility_rules:
      - 输入类型: FeatureMap
        输出类型: FeatureMap
        描述: 输入和输出均为标准的四维特征图，形状保持一致，可无缝对接前后模块

  implementation:
    框架: pytorch
    示例代码: |
      import torch
      from torch import nn
      from timm.models.swin_transformer_v2 import SwinTransformerV2Stage
      from onescience.modules.sample.onesample import OneSample
      from onescience.modules.func_utils.fuxi_utils import get_pad2d

      class FuxiTransformer(nn.Module):
          def __init__(self, embed_dim=1536, num_groups=32,
                       input_resolution=(90, 180), num_heads=8,
                       window_size=7, depth=48):
              super().__init__()
              num_groups = to_2tuple(num_groups)
              window_size = to_2tuple(window_size)
              padding = get_pad2d(input_resolution, window_size)
              self.padding = padding
              self.pad = nn.ZeroPad2d(padding)

              # 计算填充后的分辨率
              padding_left, padding_right, padding_top, padding_bottom = padding
              input_resolution = list(input_resolution)
              input_resolution[0] += padding_top + padding_bottom
              input_resolution[1] += padding_left + padding_right

              # 下采样、Transformer、上采样
              self.down = OneSample(style="FuxiDownSample", in_chans=embed_dim,
                                   out_chans=embed_dim, num_groups=num_groups[0])
              self.layer = SwinTransformerV2Stage(embed_dim, embed_dim,
                                                 input_resolution, depth,
                                                 num_heads, window_size)
              self.up = OneSample(style="FuxiUpSample", in_chans=embed_dim*2,
                                 out_chans=embed_dim, num_groups=num_groups[0])

          def forward(self, x):
              # 下采样
              x = self.down(x)
              shortcut = x

              # 填充
              x = self.pad(x)
              _, _, pad_lat, pad_lon = x.shape

              # Swin Transformer (需要 BHWC 格式)
              x = x.permute(0, 2, 3, 1)
              x = self.layer(x)
              x = x.permute(0, 3, 1, 2)

              # 裁剪
              padding_left, padding_right, padding_top, padding_bottom = self.padding
              x = x[:, :, padding_top:pad_lat-padding_bottom,
                    padding_left:pad_lon-padding_right]

              # 拼接与上采样
              x = torch.cat([shortcut, x], dim=1)
              x = self.up(x)
              return x

  usage_examples:
    - 典型 FuXi 配置，原始输入分辨率 (180, 360)，下采样后 (90, 180)，depth=48 对应论文中的深层 Swin Transformer 堆叠:
        示例代码: |
          transformer = FuxiTransformer(
              embed_dim=1536,
              num_groups=32,
              input_resolution=(90, 180),
              num_heads=8,
              window_size=7,
              depth=48,
          )
          x = torch.randn(2, 1536, 180, 360)  # (B, C, lat, lon)
          out = transformer(x)
          # out.shape: torch.Size([2, 1536, 180, 360])

  knowledge:
    应用说明: >
      FuxiTransformer 属于 Swin Transformer 范式与 U-Net 式多尺度建模范式的结合体。
      在气象 AI 建模中，Swin Transformer 范式通过窗口化自注意力和 shifted-window 机制在局部块内高效计算注意力，
      通过层次化结构支持高分辨率输入。U-Net 式下采样/上采样范式通过下采样压缩空间分辨率，在低分辨率特征图上进行大感受野建模，
      再通过上采样恢复原始分辨率，并通过跳跃连接融合细节。该组件在全球中期天气预报任务中的核心作用是：
      在合理计算开销下对高维天气场进行多尺度建模，同时捕捉局地与大尺度结构。
    热点模型:
      - 模型: FuXi
        年份: 2023
        场景: 全球中期天气预报（0-15天），需要在高分辨率（0.25°）网格上捕捉多尺度大气结构
        方案: >
          采用 U-Transformer 主干，由 48 层 Swin Transformer V2 块堆叠构成。使用 Down Block 将特征从 C×180×360 下采样至 C×90×180，
          在低分辨率上进行深层 Swin V2 注意力计算，然后通过 Up Block 上采样回 C×180×360，并使用 skip 连接保留高分辨率细节。
          Swin V2 块使用 scaled cosine attention 替代普通点积注意力，使用 log-spaced coordinates 构建相对位置编码，
          采用残差后归一化（post-normalization）代替 V1 的 pre-norm，提升训练稳定性。
        作用: >
          作为 FuXi 模型的核心主干网络，负责从 Cube Embedding 输出的压缩特征中提取多尺度空间模式，
          捕捉大气场的局部相关性与跨区域依赖关系，为后续输出层提供高层语义特征。
        创新: >
          将 Swin Transformer V2 的改进（scaled cosine attention、post-norm、log-spaced 相对位置编码）与 U-Net 多尺度结构结合，
          形成 U-Transformer 架构。通过窗口化注意力将复杂度控制在 O(N·W²)，使得在 180×360 高分辨率网格上进行 48 层深度 Transformer 计算成为可能。
          相比 FourCastNet 的 AFNO 和 Pangu 的 3D 体注意力，该方案在计算效率与表达能力之间取得更好平衡。
      - 模型: Pangu-Weather
        年份: 2023
        场景: 全球中期天气预报，需要同时建模垂直层间关系和水平空间结构
        方案: >
          采用 3D Earth-specific Transformer (3DEST)，将 Swin 风格窗口注意力扩展到 3D 空间体（层×经度×纬度）。
          使用 U-Net 式编码-解码结构，前两层保持分辨率，后 6 层下采样到一半分辨率，解码时对称上采样，
          并在第二编码层与第七解码层之间建立跳跃连接。引入 Earth-specific positional bias，
          将绝对气压层与纬度编码进偏置索引，并显式区分经度周期性与纬度非周期性。
        作用: >
          作为 Pangu-Weather 的主干网络，在 3D 体表示（8×360×181×C）上进行多尺度特征提取，
          同时建模垂直层间耦合和水平空间依赖，为全球天气场的时间演化提供动力学表征。
        创新: >
          首次将 Swin Transformer 扩展到 3D 体并结合 Earth-specific positional bias，使注意力结构与三维地球场自然对齐。
          通过在 3D 窗口内计算注意力，显式建模垂直层间关系，优于将层作为通道的 2D 方案。
          U-Net 式多尺度结构在 3D 空间体上的应用，使模型能在有限计算预算下捕捉从局地到行星尺度的大气结构。
    最佳实践:
      - 窗口大小选择：window_size 应根据 input_resolution 选择，通常为 7 或其因数，确保填充后的分辨率能被窗口大小整除，避免过多填充导致的计算浪费
      - 深度与容量平衡：depth=48 适用于全球中期预报任务，对于更简单任务可适当减少层数（如 24 或 32）以降低计算成本
      - 跳跃连接的重要性：shortcut 连接对保留高分辨率细节至关重要，移除会导致上采样后的特征模糊，影响局地天气系统的预报精度
      - 填充策略：使用 ZeroPad 而非其他填充方式（如反射填充），因为气象场在边界处通常不具有镜像对称性，零填充对周期性边界条件更友好
      - 与 Cube Embedding 配合：该模块通常接在 Cube Embedding 之后，输入分辨率应与 Cube Embedding 的输出分辨率匹配（如 180×360）
      - 多尺度特征融合：通过 Down-Transformer-Up 结构，模型能在低分辨率上捕捉大尺度模式，同时通过跳跃连接保留高分辨率细节，这对捕捉多尺度大气过程至关重要
    常见错误:
      - 分辨率不匹配：输入 x 的空间分辨率必须约为 input_resolution 的 2 倍，否则 Down Block 后的尺寸与 input_resolution 不符，导致 Swin Transformer 输入形状错误
      - 忘记维度转换：Swin Transformer 要求输入格式为 (B, H, W, C)，而 PyTorch 卷积层通常使用 (B, C, H, W)，必须在 Transformer 前后进行 permute 操作
      - 窗口大小设置不当：如果 window_size 过大或 input_resolution 不是其倍数，会导致过多填充，浪费计算资源；如果过小，则限制了注意力的感受野
      - 忽略填充与裁剪：必须在 Transformer 前进行填充以满足窗口整除要求，并在 Transformer 后裁剪回原始尺寸，否则会导致特征图尺寸不匹配
      - embed_dim 不能被 num_heads 整除：会导致多头注意力无法均匀分配维度，引发运行时错误
      - 跳跃连接通道数错误：拼接后的通道数为 2*embed_dim，Up Block 的 in_chans 必须设置为 embed_dim*2，否则会出现形状不匹配
    论文参考:
      - 标题: "FuXi: A cascade machine learning forecasting system for 15-day global weather forecast"
        作者: Chen et al.
        年份: 2023
        摘要: >
          提出 FuXi 级联机器学习天气预报系统，使用 U-Transformer 主干（基于 Swin Transformer V2）
          在 0.25° 分辨率上实现 15 天全球天气预报，通过三个针对不同时间窗（0-5天、5-10天、10-15天）
          微调的模型级联，减少长时效迭代误差累积。
      - 标题: "Swin Transformer V2: Scaling Up Capacity and Resolution"
        作者: Liu et al.
        年份: 2022
        摘要: >
          提出 Swin Transformer V2，通过 scaled cosine attention、post-normalization 和 log-spaced 相对位置编码
          解决原始 Swin Transformer 在大规模、高分辨率场景下的训练不稳定问题，支持更大模型容量和更高输入分辨率。

  graph:
    类型关系:
      - Transformer 主干网络
      - 多尺度特征提取器
      - U-Net 式编码-解码器
    所属结构:
      - FuXi 模型主干
      - U-Transformer 架构
    依赖组件:
      - SwinTransformerV2Stage (来自 timm 库)
      - FuxiDownSample (下采样模块)
      - FuxiUpSample (上采样模块)
      - ZeroPad2d (填充层)
    变体组件:
      - Pangu 3D Earth-specific Transformer (3DEST)
      - 标准 Swin Transformer V2
      - U-Net with Transformer blocks
    使用模型:
      - FuXi (全球中期天气预报)
      - FuXi-Short (0-5天预报)
      - FuXi-Medium (5-10天预报)
      - FuXi-Long (10-15天预报)
    类型兼容:
      输入:
        - FeatureMap
      输出:
        - FeatureMap
