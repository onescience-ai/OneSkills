component:
  meta:
    name: FuxiFC
    中文名称: FuXi全连接输出层
    别名: FuXi Output Layer, FuXi Fully Connected Layer
    version: 1.0
    领域: 深度学习/气象
    分类: 神经网络组件
    子类: 输出层/解码器
    作者: OneScience
    tags:
      - 气象AI
      - 全连接层
      - 输出映射
      - FuXi

  concept:
    描述: >
      FuxiFC是FuXi气象预报模型的输出层，负责将U-Transformer主干网络提取的高维特征映射为70个气象变量的预测值。
    直觉理解: >
      就像翻译官将内部语言转换为外部可理解的形式，FuxiFC将模型学到的抽象特征"翻译"成具体的温度、风速、湿度等气象变量预测值。
    解决的问题:
      - 特征到变量的映射: 将U-Transformer输出的1536维抽象特征空间映射到70维物理变量空间
      - 维度适配: 确保输出维度与ERA5数据格式(70个变量)完全匹配，便于后续插值恢复到原始分辨率

  theory:
    核心公式:
      线性变换:
        表达式: Y = X * W + b
        变量说明:
          X:
            名称: 输入特征
            形状: [B, Lat, Lon, 1536]
            描述: U-Transformer主干网络输出的高维特征张量，B为批次大小，Lat和Lon为降采样后的空间维度(180×360)，1536为特征通道数
          W:
            名称: 权重矩阵
            形状: [1536, 1120]
            描述: 可学习的线性变换权重，将1536维特征映射到1120维(70变量×4×4空间块)
          b:
            名称: 偏置向量
            形状: [1120]
            描述: 可学习的偏置项
          Y:
            名称: 输出预测
            形状: [B, Lat, Lon, 1120]
            描述: 映射后的输出，需reshape为[B, 70, 180, 360]后通过双线性插值恢复到[B, 70, 721, 1440]

  structure:
    架构类型: 全连接层(线性映射)
    计算流程:
      - 接收U-Transformer输出的特征张量 [B, Lat, Lon, C=1536]
      - 通过全连接层进行线性变换，输出 [B, Lat, Lon, 70×4×4=1120]
      - Reshape为 [B, 70, 180, 360]
      - 双线性插值恢复到原始ERA5分辨率 [B, 70, 721, 1440]
    计算流程图: |
      U-Transformer特征 [B,180,360,1536]
              ↓
      全连接层(Linear 1536→1120)
              ↓
      输出特征 [B,180,360,1120]
              ↓
      Reshape [B,70,180,360]
              ↓
      双线性插值 ↑4x
              ↓
      最终预测 [B,70,721,1440]

  interface:
    参数:
      in_channels:
        类型: int
        默认值: 1536
        描述: 输入特征通道数，对应U-Transformer主干网络的输出维度
      out_channels:
        类型: int
        默认值: 1120
        描述: 输出通道数，等于70个气象变量×4×4(空间降采样因子)
    输入:
      x:
        类型: torch.Tensor
        形状: [B, Lat, Lon, C]
        描述: U-Transformer输出的特征张量，其中B为批次大小，Lat=180、Lon=360为降采样后的空间维度，C=1536为特征通道数
    输出:
      output:
        类型: torch.Tensor
        形状: [B, Lat, Lon, 1120]
        描述: 映射后的输出张量，包含70个气象变量在180×360网格上的预测，需后续reshape和插值处理

  types:
    FeatureTensor:
      形状: [B, 180, 360, 1536]
      描述: U-Transformer主干网络输出的高维特征表示，编码了全球大气状态的抽象信息
    OutputTensor:
      形状: [B, 180, 360, 1120]
      描述: 全连接层输出，包含70个气象变量的预测值(需reshape为[B,70,180,360])
    FinalPrediction:
      形状: [B, 70, 721, 1440]
      描述: 经过reshape和双线性插值后的最终预测场，70个变量在0.25°分辨率(721×1440)经纬网格上的预测

  constraints:
    shape_constraints:
      - 规则: in_channels == 1536
        描述: 输入通道数必须与U-Transformer输出维度匹配
      - 规则: out_channels == 70 * 4 * 4
        描述: 输出通道数必须等于变量数乘以空间降采样因子的平方
      - 规则: Lat == 180 && Lon == 360
        描述: 输入空间维度必须为180×360(对应721×1440经过4×4降采样)
    parameter_constraints:
      - 规则: in_channels > 0 && out_channels > 0
        描述: 通道数必须为正整数
    compatibility_rules:
      - 输入类型: FeatureTensor
        输出类型: OutputTensor
        描述: 输入必须是U-Transformer输出的特征张量，输出需配合reshape和插值操作

  implementation:
    框架: pytorch
    示例代码: |
      import torch
      from torch import nn

      class FuxiFC(nn.Module):
          def __init__(self, in_channels=1536, out_channels=70*4*4):
              super().__init__()
              self.fc = nn.Linear(in_channels, out_channels)

          def forward(self, x: torch.Tensor):
              # x: [B, Lat, Lon, C] = [B, 180, 360, 1536]
              x = self.fc(x)  # [B, 180, 360, 1120]
              return x

  usage_examples:
    - 场景: FuXi模型标准输出层配置
      示例代码: |
        # 创建FuxiFC输出层
        output_layer = FuxiFC(in_channels=1536, out_channels=70*4*4)

        # U-Transformer输出特征
        features = torch.randn(2, 180, 360, 1536)

        # 映射到气象变量
        output = output_layer(features)  # [2, 180, 360, 1120]

        # Reshape为变量维度
        output = output.reshape(2, 70, 180, 360)

        # 双线性插值恢复到原始分辨率
        output = F.interpolate(output, size=(721, 1440), mode='bilinear')
        # 最终输出: [2, 70, 721, 1440]

  knowledge:
    应用说明: >
      FuxiFC属于气象AI模型中的输出解码模块，在全球中期天气预报的端到端建模流程中扮演"特征-变量映射"角色。
      该模块将深度学习模型学到的抽象特征空间转换为物理可解释的气象变量空间，是连接数据驱动学习与物理预报需求的关键桥梁。
      在FuXi的级联架构中，该输出层在Short/Medium/Long三个时间窗模型中共享相同设计，确保不同预报时效段输出格式的一致性。
    热点模型:
      - 模型: FuXi
        年份: 2023
        场景: 全球15天中期天气预报，需将U-Transformer学到的1536维特征映射为70个ERA5变量
        方案: 使用单层全连接层(1536→1120)进行线性映射，输出经reshape为[70,180,360]后通过双线性插值恢复到0.25°分辨率(721×1440)
        作用: 将抽象特征解码为物理变量，支持级联架构中三个时间窗模型的统一输出格式
        创新: 采用简洁的单层FC设计，避免过度复杂化，配合空间插值实现高效的特征-变量映射
      - 模型: Pangu-Weather
        年份: 2023
        场景: 全球中期天气预报，需从3DEST输出的3D体特征恢复到原始分辨率的多变量场
        方案: 使用Patch Recovery模块，通过线性层将patch特征映射回原始空间分辨率，分别处理上空(13层×5变量)和地表(4变量)
        作用: 将3D patch embedding的逆操作，恢复空间细节
        创新: 针对3D体建模设计专门的patch恢复机制，区分上空与地表的不同处理路径
    最佳实践:
      - 保持输出层简洁，使用单层线性映射避免过拟合，将复杂建模能力留给主干网络
      - 输出通道数设计需考虑后续reshape和插值操作，确保维度匹配(70变量×4×4空间块=1120)
      - 配合双线性插值恢复空间分辨率时，应在较低分辨率(180×360)进行特征映射以降低计算成本
      - 在级联架构中，各时间窗模型应共享相同的输出层设计，确保输出格式一致性
    常见错误:
      - 输出通道数设置错误，导致reshape时维度不匹配(必须为70×4×4=1120)
      - 忘记在全连接层后进行reshape操作，直接将[B,Lat,Lon,1120]当作最终输出
      - 插值模式选择不当，使用最近邻插值导致空间不连续
      - 输入特征维度与in_channels不匹配，导致线性层计算错误
    论文参考:
      - 标题: FuXi: A cascade machine learning forecasting system for 15-day global weather forecast
        作者: Lei Chen et al.
        年份: 2023
        摘要: 提出级联ML架构用于15天全球天气预报，使用U-Transformer主干+简洁FC输出层，在0-9天预报上优于ECMWF EM

  graph:
    类型关系:
      - 神经网络层
      - 线性映射层
      - 输出解码器
    所属结构:
      - FuXi模型
      - U-Transformer解码路径
      - 级联预报系统(Short/Medium/Long)
    依赖组件:
      - U-Transformer主干网络
      - 双线性插值模块
      - Reshape操作
    变体组件:
      - Pangu Patch Recovery(3D体恢复)
      - FourCastNet输出层(AFNO后的FC)
      - GraphCast Mesh2Grid解码器(GNN图到网格映射)
    使用模型:
      - FuXi
      - FuXi-Short
      - FuXi-Medium
      - FuXi-Long
    类型兼容:
      输入:
        - FeatureTensor
      输出:
        - OutputTensor
