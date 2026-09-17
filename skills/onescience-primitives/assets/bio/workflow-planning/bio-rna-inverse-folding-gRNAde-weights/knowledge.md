# gRNAde模型权重获取与验证工作流

## 适用范围
**触发条件**：
- 需要加载gRNAde模型权重进行RNA三维反向设计
- 需要获取gRNAde模型的官方发布渠道和版本信息
- 需要检查gRNAde模型的许可证说明

**适用场景**：
- RNA三维结构反向设计任务
- 基于几何深度学习的RNA序列设计
- 需要预训练模型权重的研究项目

**不适用场景**：
- 仅需二级结构设计的任务
- 非RNA分子的设计任务

## 输入
- 目标RNA三维结构（PDB格式）
- 模型权重文件路径（grnade.pt）
- Python环境（PyTorch、PyG等依赖）

## 输出
- 可用的gRNAde模型权重文件
- 模型版本信息
- 许可证说明文档

## 流程节点

### Step 1：官方渠道检索
- **操作**：在GitHub等平台搜索gRNAde官方仓库
- **参数**：搜索关键词="gRNAde RNA inverse folding GitHub"
- **工具**：Web浏览器、GitHub搜索
- **质量门禁**：确认仓库为官方发布渠道

### Step 2：版本信息确认
- **操作**：检查仓库中的版本发布信息
- **参数**：版本号、发布日期、更新日志
- **工具**：GitHub Releases页面
- **质量门禁**：确认版本与论文一致

### Step 3：许可证检查
- **操作**：阅读仓库中的LICENSE文件
- **参数**：许可证类型（MIT、Apache等）
- **工具**：文本编辑器
- **质量门禁**：确认许可证允许学术使用

### Step 4：权重下载与验证
- **操作**：下载模型权重文件并验证完整性
- **参数**：文件大小、MD5校验和
- **工具**：wget/curl、md5sum
- **质量门禁**：文件可被PyTorch成功加载

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型框架 | PyTorch | [1] | gRNAde基于PyTorch实现 |
| 图神经网络 | PyG (PyTorch Geometric) | [1] | 用于处理分子图结构 |
| 权重格式 | .pt (PyTorch checkpoint) | [1] | 标准PyTorch模型保存格式 |
| 许可证 | 学术使用 | [2] | 需确认具体许可证类型 |
| 依赖版本 | PyTorch≥1.12, PyG≥2.0 | [1] | 兼容性要求 |

## 边界与分流
- **权重不可用**：联系论文作者或使用替代模型（如RiboDiffusion）
- **版本不匹配**：使用兼容版本或重新训练模型
- **许可证限制**：寻找替代模型或申请使用许可

## 质量检查
- 验证权重文件可被`torch.load()`成功加载
- 检查模型输出维度与论文描述一致
- 确认许可证允许预期使用场景

## 回退策略
- 使用RiboDiffusion等替代模型
- 联系论文作者获取权重
- 基于公开数据集重新训练模型

## 资源召回建议
- 当需要RNA三维反向设计时召回本卡片
- 配合`bio-rna-inverse-folding-dependencies`使用
- 配合`bio-rna-pdb-parsing-validation`使用

## 证据来源
[1] "RiboDiffusion: tertiary structure-based RNA inverse folding with generative diffusion models", Bioinformatics, 2024, DOI: 10.1093/bioinformatics/btae259
[2] "R3Design: deep tertiary structure-based RNA sequence design and beyond", Briefings in Bioinformatics, 2024, DOI: 10.1093/bib/bbae682