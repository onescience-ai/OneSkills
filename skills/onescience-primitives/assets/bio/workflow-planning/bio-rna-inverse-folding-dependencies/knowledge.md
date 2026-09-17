# RNA反向设计工具依赖安装工作流

## 适用范围
**触发条件**：
- 需要安装gRNAde、RiboDiffusion、R3Design等RNA反向设计工具
- 需要配置Python环境运行RNA设计代码
- 需要检查依赖版本兼容性

**适用场景**：
- RNA三维反向设计任务
- 基于深度学习的RNA序列设计
- 需要特定版本PyTorch和PyG的研究项目

**不适用场景**：
- 仅需二级结构设计的任务
- 非Python环境的任务

## 输入
- 目标RNA设计工具（gRNAde/RiboDiffusion/R3Design）
- 系统环境信息（操作系统、Python版本）
- 硬件信息（GPU型号、显存大小）

## 输出
- 可运行的Python环境
- 依赖安装验证结果
- 版本兼容性报告

## 流程节点

### Step 1：环境检查
- **操作**：检查当前Python环境和硬件配置
- **参数**：Python版本、CUDA版本、GPU显存
- **工具**：python --version, nvidia-smi
- **质量门禁**：Python≥3.8, CUDA≥11.0

### Step 2：conda环境创建
- **操作**：创建独立的conda环境
- **参数**：环境名称、Python版本
- **工具**：conda create, conda activate
- **质量门禁**：环境创建成功

### Step 3：核心依赖安装
- **操作**：安装PyTorch、PyG等核心依赖
- **参数**：PyTorch≥1.12, PyG≥2.0, Biopython≥1.79
- **工具**：pip, conda
- **质量门禁**：import torch, import torch_geometric成功

### Step 4：工具特定依赖安装
- **操作**：安装RNA设计工具的特定依赖
- **参数**：requirements.txt中的依赖
- **工具**：pip install -r requirements.txt
- **质量门禁**：所有依赖安装成功

### Step 5：环境验证
- **操作**：运行验证脚本确认环境就绪
- **参数**：验证脚本输出
- **工具**：python -c 'import torch; import torch_geometric'
- **质量门禁**：验证脚本无错误输出

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Python版本 | ≥3.8 | [1] | 兼容性要求 |
| PyTorch版本 | ≥1.12 | [1] | 深度学习框架 |
| PyG版本 | ≥2.0 | [1] | 图神经网络库 |
| Biopython版本 | ≥1.79 | [2] | 生物信息学工具 |
| CUDA版本 | ≥11.0 | [1] | GPU加速支持 |
| NumPy版本 | ≥1.21 | [1] | 数值计算库 |
| SciPy版本 | ≥1.7 | [1] | 科学计算库 |

## 边界与分流
- **依赖冲突**：使用conda环境隔离或虚拟环境
- **版本不兼容**：降级或升级特定依赖
- **安装失败**：检查网络连接或使用镜像源

## 质量检查
- 验证`python -c 'import torch; print(torch.cuda.is_available())'`输出True
- 验证`python -c 'import torch_geometric'`无错误
- 验证`python -c 'import Bio'`无错误

## 回退策略
- 使用Docker容器预配置环境
- 联系工具开发者获取环境配置指南
- 使用在线Colab笔记本运行

## 资源召回建议
- 当需要安装RNA设计工具时召回本卡片
- 配合`bio-rna-inverse-folding-gRNAde-weights`使用
- 配合`bio-rna-pdb-parsing-validation`使用

## 证据来源
[1] "RiboDiffusion: tertiary structure-based RNA inverse folding with generative diffusion models", Bioinformatics, 2024, DOI: 10.1093/bioinformatics/btae259
[2] "R3Design: deep tertiary structure-based RNA sequence design and beyond", Briefings in Bioinformatics, 2024, DOI: 10.1093/bib/bbae682