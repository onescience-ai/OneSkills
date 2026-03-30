component:
  meta:
    name: FourCastNetEmbedding
    中文名称: FourCastNet 二维面片嵌入层
    别名: 2D Patch Embedding, FourCastNet Patch Embedding
    version: 1.0
    领域: 深度学习/气象AI
    分类: 神经网络组件
    子类: 嵌入层/编码器
    作者: OneScience
    tags:
      - 气象AI
      - Patch Embedding
      - Vision Transformer
      - 全球天气预报

  concept:
    描述: >
      FourCastNet 二维面片嵌入层是将多变量全球气象场转换为 token 序列的入口模块，
      通过 2D 卷积将输入场按固定大小的 patch 划分并线性投影到高维嵌入空间，
      为后续 AFNO-Transformer 主干提供统一的 token 表示。
    直觉理解: >
      就像将一张全球天气地图切成许多小方块（patch），每个方块包含局部的多个气象变量信息，
      然后用一个"翻译器"把每个方块压缩成一个高维向量（token），
      这样 Transformer 就能像处理文字一样处理这些天气信息块。
    解决的问题:
      - 高分辨率全球场的维度压缩: 将 721×1440×20 的原始气象场压缩为可被 Transformer 高效处理的 token 序列，降低计算复杂度
      - 多变量局部特征提取: 通过 patch 内的卷积操作捕捉局部多变量耦合关系，为后续全局建模提供良好的局部表征
      - 空间结构保持: 保留原始场的二维空间拓扑关系，使 token 序列仍对应规则的二维网格，便于后续 AFNO 频域操作

  theory:
    核心公式:
      Patch划分与线性投影:
        表达式: "X_tokens = Flatten(Conv2D(X_input; kernel=p×p, stride=p)).transpose(1,2)"
        变量说明:
          X_input:
            名称: 输入气象场
            形状: "[B, C, H, W]"
            描述: "批次大小 B，通道数 C（气象变量数），纬度分辨率 H，经度分辨率 W。FourCastNet 中 C=20（包含地表与多个气压层的温度、风速、湿度等变量），H=721，W=1440，对应 0.25° 全球网格"
          p:
            名称: Patch 大小
            形状: 标量
            描述: "Patch 的边长，FourCastNet 中 p=8，即每个 patch 覆盖 8×8 个网格点"
          Conv2D:
            名称: 二维卷积投影
            形状: "[C, d, p, p]"
            描述: "卷积核将每个 p×p×C 的 patch 映射到 d 维嵌入向量，d=768 为 FourCastNet 的嵌入维度"
          X_tokens:
            名称: 输出 token 序列
            形状: "[B, N, d]"
            描述: "N = (H/p) × (W/p) 为 patch 数量，FourCastNet 中 N = 90×180 = 16200。每个 token 对应原始场中一个 8×8 的局部区域"

  structure:
    架构类型: 卷积嵌入网络
    计算流程:
      - "输入多变量气象场 X ∈ R^(B×C×H×W)"
      - "通过 2D 卷积（kernel_size=patch_size, stride=patch_size）将空间维度划分为不重叠的 patch"
      - "卷积输出形状为 (B, d, H/p, W/p)，其中 d 为嵌入维度"
      - "将空间维度展平：flatten(2) → (B, d, N)，其中 N=(H/p)×(W/p)"
      - "转置通道与序列维度：transpose(1,2) → (B, N, d)"
      - "输出 token 序列供后续 AFNO 层或位置编码模块使用"
    计算流程图: |
      输入气象场 [B, C=20, H=721, W=1440]
        ↓
      Conv2D(kernel=8×8, stride=8, out_channels=768)
        ↓
      卷积输出 [B, 768, 90, 180]
        ↓
      Flatten(dim=2) → [B, 768, 16200]
        ↓
      Transpose(1,2) → [B, 16200, 768]
        ↓
      输出 token 序列 [B, N=16200, d=768]

  interface:
    参数:
      img_size:
        类型: tuple[int, int]
        默认值: (720, 1440)
        描述: "输入气象场的空间分辨率 (纬度格点数, 经度格点数)，对应全球 0.25° 网格的 721×1440 规格（FourCastNet 实际使用 720×1440）"
      patch_size:
        类型: tuple[int, int]
        默认值: (8, 8)
        描述: "Patch 的空间大小 (纬度方向, 经度方向)，决定了每个 token 覆盖的网格点数量"
      in_chans:
        类型: int
        默认值: 19
        描述: "输入气象变量的通道数。FourCastNet 论文中使用 20 个预报变量（地表 5 个 + 多层上空变量），代码默认 19 可能对应不同配置"
      embed_dim:
        类型: int
        默认值: 768
        描述: "Patch 嵌入后的特征维度，即每个 token 的向量长度，与后续 AFNO 层的通道维度一致"
    输入:
      x:
        类型: Tensor
        形状: "[B, C, H, W]"
        描述: "批次气象场张量。B 为批次大小，C 为气象变量通道数（in_chans），H 和 W 为纬度和经度方向的空间分辨率，必须与 img_size 匹配"
    输出:
      tokens:
        类型: Tensor
        形状: "[B, N, D]"
        描述: "Patch token 序列。N = (H/Ph) × (W/Pw) 为 patch 数量，D 为嵌入维度（embed_dim）。每个 token 对应输入场中一个 patch 的高维表征"

  types:
    WeatherField:
      形状: "[B, C, H, W]"
      描述: "多变量气象场类型。C 维包含多个气象变量（如温度、风速、湿度等），H×W 为全球经纬网格"
    TokenSequence:
      形状: "[B, N, D]"
      描述: "Token 序列类型。N 为 token 数量，D 为特征维度，用于 Transformer 或 AFNO 处理"

  constraints:
    shape_constraints:
      - 规则: "H == img_size[0] and W == img_size[1]"
        描述: "输入场的空间分辨率必须与初始化时指定的 img_size 严格匹配"
      - 规则: "H % patch_size[0] == 0 and W % patch_size[1] == 0"
        描述: "输入场的空间维度必须能被 patch_size 整除，以保证完整的 patch 划分"
      - 规则: "C == in_chans"
        描述: "输入通道数必须与初始化时指定的 in_chans 一致"
    parameter_constraints:
      - 规则: "patch_size[0] > 0 and patch_size[1] > 0"
        描述: "Patch 大小必须为正整数"
      - 规则: "embed_dim > 0"
        描述: "嵌入维度必须为正整数"
    compatibility_rules:
      - 输入类型: WeatherField
        输出类型: TokenSequence
        描述: "将二维气象场转换为一维 token 序列，空间结构被隐式编码在 token 的排列顺序中"

  implementation:
    框架: pytorch
    示例代码: |
      import torch
      import torch.nn as nn

      class FourCastNetEmbedding(nn.Module):
          def __init__(self, img_size=(720, 1440), patch_size=(8, 8),
                       in_chans=19, embed_dim=768):
              super().__init__()
              num_patches = (img_size[1] // patch_size[1]) * (img_size[0] // patch_size[0])
              self.img_size = img_size
              self.patch_size = patch_size
              self.num_patches = num_patches
              self.proj = nn.Conv2d(in_chans, embed_dim,
                                   kernel_size=patch_size, stride=patch_size)

          def forward(self, x):
              B, C, H, W = x.shape
              assert H == self.img_size[0] and W == self.img_size[1], \
                  f"Input size ({H}*{W}) doesn't match model ({self.img_size[0]}*{self.img_size[1]})"
              x = self.proj(x).flatten(2).transpose(1, 2)
              return x

  usage_examples:
    - 标准 FourCastNet 配置（0.25° 全球网格，20 变量）:
        示例代码: |
          embedding = FourCastNetEmbedding(
              img_size=(720, 1440),
              patch_size=(8, 8),
              in_chans=20,
              embed_dim=768
          )
          x = torch.randn(2, 20, 720, 1440)  # 批次=2
          tokens = embedding(x)
          # tokens.shape: (2, 16200, 768)
          # 16200 = (720/8) * (1440/8) = 90 * 180

    - 更大 patch 配置（减少 token 数量）:
        示例代码: |
          embedding = FourCastNetEmbedding(
              img_size=(720, 1440),
              patch_size=(16, 16),
              in_chans=20,
              embed_dim=768
          )
          x = torch.randn(1, 20, 720, 1440)
          tokens = embedding(x)
          # tokens.shape: (1, 4050, 768)
          # 4050 = (720/16) * (1440/16) = 45 * 90

  knowledge:
    应用说明: >
      FourCastNetEmbedding 属于 Vision Transformer (ViT) 风格的 Patch Embedding 模块，
      在气象 AI 建模中扮演"输入编码器"角色。该组件将高分辨率全球气象场转换为适合
      Transformer 处理的 token 序列，是连接物理空间与特征空间的桥梁。
      在领域建模范式中，Patch Embedding 是 2D 通道堆叠策略的核心组件，
      通过将多变量、多层的气象场扁平化为统一通道，并进一步压缩为 token 表示，
      使得模型能够在有限计算资源下处理全球尺度的高分辨率数据。
      该模块解决了传统卷积网络在全球场景下感受野受限的问题，
      为后续的全局依赖建模（如 AFNO 频域混合、自注意力机制）提供了基础。
    热点模型:
      - 模型: FourCastNet
        年份: 2022
        场景: 全球高分辨率（0.25°）中期天气预报，预测未来 1 周内的 20 个大气变量
        方案: >
          使用 8×8 patch 将 721×1440×20 的全球场划分为 16200 个 token，
          每个 token 通过 2D 卷积投影到 768 维嵌入空间。
          嵌入后的 token 序列保持二维网格拓扑（90×180），
          直接送入 AFNO 层进行频域全局混合，复杂度为 O(N log N)。
          该设计使 FourCastNet 能够在单步前向中捕捉全球尺度的长程依赖，
          同时保持计算效率。
        作用: 将原始气象场压缩为高维 token 表示，降低后续 Transformer 的计算复杂度
        创新: 首次在全球 0.25° 分辨率上应用 ViT 风格 Patch Embedding，为 AFNO 频域操作提供规则的二维 token 网格
      - 模型: Pangu-Weather
        年份: 2023
        场景: 全球 0.25° 分辨率中期天气预报，采用 3D 体建模策略
        方案: >
          上空部分使用 2×4×4 的 3D patch（层×经度×纬度），
          地表使用 4×4 的 2D patch，分别嵌入后在层维拼接形成统一 3D 体。
          与 FourCastNet 的纯 2D patch 不同，Pangu 显式建模垂直维度，
          通过 3D 窗口注意力捕捉层间耦合关系。
        作用: 将多层气象场转换为 3D token 体，支持垂直与水平方向的联合建模
        创新: 扩展 Patch Embedding 到 3D 空间，并结合 Earth-specific positional bias 处理球面几何
      - 模型: FuXi
        年份: 2023
        场景: 全球 0.25° 分辨率 15 天中长期预报，采用级联模型结构
        方案: >
          使用 Cube Embedding 模块，通过 3D 卷积（时间×空间）同时处理两个连续时间步的输入，
          将 [2, 70, 721, 1440] 的时空张量嵌入为 [C, 180, 360] 的特征图。
          该设计在嵌入阶段即融合时间信息，为后续 Swin Transformer 提供时间感知的空间特征。
        作用: 时空联合嵌入，在输入层即建模时间演化信息
        创新: 将 Patch Embedding 扩展到时空域，通过 3D 卷积在嵌入阶段捕捉时间连续性
    最佳实践:
      - 选择 patch_size 时需平衡计算效率与空间分辨率：较小的 patch（如 4×4）保留更多细节但增加 token 数量，较大的 patch（如 16×16）降低计算量但可能丢失小尺度信息
      - 对于全球气象场，patch_size 应确保能整除输入分辨率，避免边界处理问题
      - embed_dim 通常设置为 512、768 或 1024，需与后续 Transformer 层的隐藏维度保持一致 [基于通用知识补充]
      - 在多 GPU 训练时，可通过增大 batch size 提高 GPU 利用率，因为 Patch Embedding 的卷积操作高度并行化 [基于通用知识补充]
      - 对于不同分辨率的输入，建议重新训练 Patch Embedding 层而非插值，以保持最优性能 [基于通用知识补充]
    常见错误:
      - 输入分辨率与 img_size 不匹配会导致运行时错误，需在数据预处理阶段确保一致性
      - 忘记将输入从 [B, H, W, C] 转换为 [B, C, H, W] 格式（PyTorch 约定）
      - patch_size 无法整除输入分辨率时会导致信息丢失或维度错误 [基于通用知识补充]
      - 在推理时改变 batch size 不会影响模型行为，但改变空间分辨率会导致错误 [基于通用知识补充]
    论文参考:
      - 标题: "FourCastNet: A Global Data-driven High-resolution Weather Model using Adaptive Fourier Neural Operators"
        作者: Pathak et al.
        年份: 2022
        摘要: 提出在全球 0.25° 分辨率上使用 AFNO + ViT 骨干进行天气预报，首次在 DL 框架中高精度预报近地面风速和降水等小尺度敏感变量

  graph:
    类型关系:
      - 神经网络层
      - 嵌入层
      - 编码器组件
    所属结构:
      - FourCastNet 模型
      - AFNO-Transformer 架构
      - Vision Transformer 系列
    依赖组件:
      - Conv2d (PyTorch 基础卷积层)
      - 位置编码模块 (可选，FourCastNet 中使用)
    变体组件:
      - PanguEmbedding3D (三维体嵌入)
      - FuxiCubeEmbedding (时空立方体嵌入)
      - GraphCast Grid Embedding (图节点嵌入)
      - FengWu 多模态嵌入
    使用模型:
      - FourCastNet
      - 基于 ViT 的气象预报模型
    类型兼容:
      输入:
        - WeatherField
      输出:
        - TokenSequence
