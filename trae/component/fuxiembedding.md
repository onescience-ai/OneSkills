component:
  meta:
    name: FuxiEmbedding
    中文名称: FuXi三维面片嵌入层
    别名: 空间-时间Cube Embedding, 3D Patch Embedding
    version: 1.0
    领域: 深度学习/气象AI
    分类: 神经网络组件
    子类: 嵌入层/编码器
    作者: OneScience
    tags:
      - 气象AI
      - 3D卷积
      - 时空降维
      - 特征编码

  concept:
    描述: >
      FuxiEmbedding是FuXi模型的三维面片嵌入模块,使用3D卷积将(时间步,纬度,经度)三维气象场划分为不重叠的Patch并投影到嵌入空间,
      是FuXi模型编码器的入口层。与Pangu-Weather将气压层和地表变量分开处理不同,FuXi将多帧气象场沿时间轴堆叠后统一做三维Patch划分。
    直觉理解: >
      就像把一段视频(时间+空间)切成小立方体块,每个立方体包含了一小段时间和一小块空间的信息,然后把这些立方体压缩成更紧凑的特征向量。
      时间维度通常设为与输入帧数相同以完全合并时间信息,空间维度则通过4×4的patch实现降采样。
    解决的问题:
      - 高维输入降维: 将2×70×721×1440的高维多变量全球格点场压缩到可处理的特征空间(1536×180×360),降低后续U-Transformer的计算与内存开销
      - 时空特征融合: 通过3D卷积同时在时间和空间维度上提取局部相关性,将前后两个时间步的信息有效融合
      - 冗余消除: 减少输入冗余,使模型能在可接受成本下进行训练与推理

  theory:
    核心公式:
      三维卷积降维:
        表达式: Z = Conv3D(X; kernel=(Pt,Ph,Pw), stride=(Pt,Ph,Pw)) → LayerNorm(Z)
        变量说明:
          X:
            名称: 输入气象场
            形状: [B, C_in, T, H, W]
            描述: 批次大小B,输入通道C_in(变量数),时间步T,纬度H,经度W。FuXi中为[B,70,2,721,1440]
          Pt:
            名称: 时间维patch大小
            形状: 标量
            描述: 时间维度的patch尺寸,通常设为T以完全合并时间步,FuXi中为2
          Ph:
            名称: 纬度patch大小
            形状: 标量
            描述: 纬度方向的patch尺寸,FuXi中为4
          Pw:
            名称: 经度patch大小
            形状: 标量
            描述: 经度方向的patch尺寸,FuXi中为4
          Z:
            名称: 嵌入特征
            形状: [B, C_out, T//Pt, H//Ph, W//Pw]
            描述: 输出嵌入维度C_out,空间分辨率降低。FuXi中为[B,1536,1,180,360]

  structure:
    架构类型: 3D卷积网络
    计算流程:
      - 输入多帧气象场 X: [B, C_in, T, H, W]
      - 应用3D卷积(kernel=stride=(Pt,Ph,Pw))进行时空降维
      - 输出特征 Z: [B, C_out, T//Pt, H//Ph, W//Pw]
      - 应用LayerNorm归一化提升训练稳定性
      - 输出归一化后的嵌入特征
    计算流程图: |
      输入 [B,70,2,721,1440]
           ↓
      Conv3D(kernel=(2,4,4), stride=(2,4,4), out_channels=1536)
           ↓
      特征 [B,1536,1,180,360]
           ↓
      LayerNorm
           ↓
      输出 [B,1536,1,180,360]

  interface:
    参数:
      img_size:
        类型: tuple[int, int, int]
        默认值: (2, 721, 1440)
        描述: 输入数据的空间尺寸(T, lat, lon),其中T为时间步数(通常为2,对应当前时刻与前一时刻)
      patch_size:
        类型: tuple[int, int, int]
        默认值: (2, 4, 4)
        描述: 3D Patch大小(Pt, Plat, Plon),时间维度通常设为与T相同以合并时间步
      in_chans:
        类型: int
        默认值: 70
        描述: 输入气象变量通道数,FuXi中为70(5个变量×13层+5个地表变量)
      embed_dim:
        类型: int
        默认值: 1536
        描述: Patch嵌入维度,即输出特征的通道数
      norm_layer:
        类型: nn.Module或None
        默认值: nn.LayerNorm
        描述: 嵌入后的归一化层类型,为None时跳过归一化
    输入:
      x:
        类型: WeatherField5D
        形状: [B, C, T, lat, lon]
        描述: 五维气象场张量,其中C=in_chans,T=img_size[0]。FuXi中为[B,70,2,721,1440]
    输出:
      embedded:
        类型: EmbeddedFeature5D
        形状: [B, embed_dim, nT, nLat, nLon]
        描述: 嵌入后的特征张量,其中nT=T//Pt, nLat=lat//Plat, nLon=lon//Plon。FuXi中为[B,1536,1,180,360]

  types:
    WeatherField5D:
      形状: [B, C, T, H, W]
      描述: 五维气象场,批次×变量通道×时间步×纬度×经度
    EmbeddedFeature5D:
      形状: [B, D, nT, nH, nW]
      描述: 嵌入后的五维特征,批次×嵌入维度×时间patch数×纬度patch数×经度patch数

  constraints:
    shape_constraints:
      - 规则: T == img_size[0] and lat == img_size[1] and lon == img_size[2]
        描述: 输入张量的时空维度必须与配置的img_size完全匹配
      - 规则: img_size[0] % patch_size[0] == 0
        描述: 时间维度必须能被时间patch大小整除
      - 规则: img_size[1] % patch_size[1] == 0
        描述: 纬度维度必须能被纬度patch大小整除
      - 规则: img_size[2] % patch_size[2] == 0
        描述: 经度维度必须能被经度patch大小整除
    parameter_constraints:
      - 规则: in_chans > 0 and embed_dim > 0
        描述: 输入通道数和嵌入维度必须为正整数
      - 规则: all(p > 0 for p in patch_size)
        描述: patch_size的所有维度必须为正整数
    compatibility_rules:
      - 输入类型: WeatherField5D
        输出类型: EmbeddedFeature5D
        描述: 将五维气象场转换为五维嵌入特征,空间分辨率降低但特征维度增加

  implementation:
    框架: pytorch
    示例代码: |
      import torch
      from torch import nn

      class FuxiEmbedding(nn.Module):
          def __init__(self, img_size=(2, 721, 1440), patch_size=(2, 4, 4),
                       in_chans=70, embed_dim=1536, norm_layer=nn.LayerNorm):
              super().__init__()
              patches_resolution = [img_size[0] // patch_size[0],
                                    img_size[1] // patch_size[1],
                                    img_size[2] // patch_size[2]]

              self.img_size = img_size
              self.patches_resolution = patches_resolution
              self.embed_dim = embed_dim
              self.proj = nn.Conv3d(in_chans, embed_dim,
                                    kernel_size=patch_size, stride=patch_size)
              if norm_layer is not None:
                  self.norm = norm_layer(embed_dim)
              else:
                  self.norm = None

          def forward(self, x: torch.Tensor):
              B, C, T, Lat, Lon = x.shape
              assert T == self.img_size[0] and Lat == self.img_size[1] and Lon == self.img_size[2]
              x = self.proj(x).reshape(B, self.embed_dim, -1).transpose(1, 2)
              if self.norm is not None:
                  x = self.norm(x)
              x = x.transpose(1, 2).reshape(B, self.embed_dim, *self.patches_resolution)
              return x

  usage_examples:
    - 典型FuXi配置：2帧输入，70个气象变量，patch_size=(2,4,4)，时间维度完全合并
      示例代码: |
        embedding = FuxiEmbedding(
            img_size=(2, 721, 1440),
            patch_size=(2, 4, 4),
            in_chans=70,
            embed_dim=1536,
        )
        x = torch.randn(2, 70, 2, 721, 1440)  # (B, C, T, lat, lon)
        out = embedding(x)
        # out.shape: torch.Size([2, 1536, 1, 180, 360])
        # nT = 2 // 2 = 1, nLat = 721 // 4 = 180, nLon = 1440 // 4 = 360

  knowledge:
    应用说明: >
      FuxiEmbedding属于2D通道堆叠策略下的嵌入模块。在气象AI建模中,嵌入层负责将高维多变量气象场转换为紧凑的特征表示,
      是连接原始数据与深度网络主干的桥梁。该模块通过3D卷积同时处理时间和空间维度,实现时空特征的联合编码。
      核心问题是如何在保持关键物理结构的前提下进行高效降维,创新点在于使用3D卷积统一处理多帧时空数据。
    热点模型:
      - 模型: FuXi
        年份: 2023
        场景: 全球中期天气预报(15天),需要处理高分辨率(0.25°)多变量气象场
        方案: 使用kernel和stride均为(2,4,4)的3D卷积,将2×70×721×1440的输入压缩为1536×1×180×360,时间维完全合并,空间分辨率降低16倍,通道数升至1536维
        作用: 作为U-Transformer主干的入口层,大幅降低计算复杂度,使后续48层Swin Transformer V2块能在可接受成本下训练
        创新: 采用3D卷积统一处理时空维度,相比分离处理时间和空间,能更好地捕捉时空局部相关性;时间patch设为2完全合并两帧信息
      - 模型: Pangu-Weather
        年份: 2023
        场景: 全球中期天气预报,需要显式建模垂直层间关系
        方案: 使用2×4×4的3D patch embedding处理上空13层气象数据,将(13,1440,721,5)压缩为(7,360,181,C),垂直维也参与patch划分
        作用: 将气压层、经纬度三个空间维度统一为3D体表示,为后续3D Earth-Specific Transformer提供输入
        创新: 将垂直层视为与水平维等价的空间维,通过3D patch embedding构建统一体表示,支持3D窗口注意力同时建模垂直与水平邻域
    最佳实践:
      - 时间patch大小通常设为输入时间步数,以完全合并时间信息,避免时间维度的冗余表示
      - 空间patch大小需权衡降维效率与信息保留,4×4是常见选择,可将0.25°分辨率降至1°左右
      - 嵌入维度(embed_dim)应足够大以容纳压缩后的信息,通常设为1024-2048之间
      - 在3D卷积后添加LayerNorm可显著提升训练稳定性,特别是在大模型中
      - kernel_size和stride保持一致可实现无重叠的patch划分,避免信息冗余 [基于通用知识补充]
    常见错误:
      - 输入尺寸不能被patch_size整除会导致运行时错误,需在数据预处理阶段确保尺寸匹配
      - 忘记添加归一化层可能导致训练不稳定,特别是在深层网络中
      - embed_dim设置过小会造成信息瓶颈,过大则增加计算成本 [基于通用知识补充]
    论文参考:
      - 标题: Accurate medium-range global weather forecasting with 3D neural networks
        作者: Lei Chen et al.
        年份: 2023
        摘要: FuXi模型使用3D卷积嵌入层处理多帧气象场,实现15天全球天气预报

  graph:
    类型关系:
      - 神经网络层
      - 嵌入层
      - 编码器组件
    所属结构:
      - FuXi模型
      - U-Transformer编码器
    依赖组件:
      - Conv3d
      - LayerNorm
    变体组件:
      - PanguEmbedding3D (Pangu-Weather的3D体嵌入)
      - PatchEmbed2D (标准2D patch embedding)
      - CubeEmbedding (通用时空cube embedding)
    使用模型:
      - FuXi
    类型兼容:
      输入:
        - WeatherField5D
      输出:
        - EmbeddedFeature5D


