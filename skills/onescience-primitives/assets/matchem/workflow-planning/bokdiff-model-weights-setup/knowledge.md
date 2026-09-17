# BoKDiff 模型权重获取与设置

## 适用范围
- 触发条件：执行基于BoKDiff的靶标特异性三维分子生成任务时
- 适用场景：需要下载、配置或验证BoKDiff/DecompDiff模型权重
- 不适用场景：其他扩散模型（如EDM、GeoDiff）的权重管理

## 输入
- 目标蛋白口袋PDB文件（包含结合位点原子坐标）
- Python环境（推荐3.8+）
- GPU显存（推荐≥8GB，论文使用RTX 3090）

## 输出
- 可加载的模型检查点文件（.ckpt格式）
- 模型权重路径配置

## 流程节点

### 1. 获取BoKDiff代码仓库
- 操作：克隆GitHub仓库
- 命令：`git clone https://github.com/khodabandeh-ali/BoKDiff.git`
- 质量门禁：确认仓库包含sampling/、training/、evaluation/目录

### 2. 获取DecompDiff基础权重
- 操作：下载DecompDiff预训练检查点
- 来源：DecompDiff原始仓库（Guan et al. 2024）
- 格式：PyTorch Lightning检查点（.ckpt）
- 模型大小：约500万参数
- 质量门禁：检查点可被`torch.load()`成功加载

### 3. 权重配置与验证
- 操作：将检查点放置在指定目录，更新配置文件路径
- 验证命令：`python -c "import torch; ckpt = torch.load('bokdiff.ckpt'); print(ckpt.keys())"`
- 质量门禁：检查点包含model_state_dict、optimizer_state_dict等标准字段

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 基础模型 | DecompDiff | [论文1] | BoKDiff基于DecompDiff构建 |
| 检查点格式 | .ckpt | [论文1] | PyTorch Lightning标准格式 |
| 模型参数量 | ~5M | [论文1] | 轻量级扩散模型 |
| 训练Epoch | 1000 | [论文1] | 微调训练轮次 |
| 学习率 | 1×10⁻⁶ | [论文1] | Best-of-K对齐微调 |
| Batch Size | 128 | [论文1] | 训练批次大小 |

## 边界与分流
- **权重版本不匹配**：BoKDiff权重必须与DecompDiff代码版本对应，版本不匹配会导致加载失败
- **GPU显存不足**：模型本身轻量，但推理时需批量生成K个候选，显存需求随K增大
- **离线环境**：需提前下载权重文件，配置本地路径

## 质量检查
- 验证检查点文件大小（通常50-200MB）
- 检查模型结构与代码定义一致
- 测试推理：输入蛋白口袋，验证可生成分子

## 回退策略
- 如GitHub无法访问：使用镜像源（如gitee）或联系作者获取权重
- 如权重损坏：重新下载或使用DecompDiff原始权重作为替代

## 资源召回建议
- 何时召回：执行BoKDiff/DecompDiff相关任务时
- 配套资源：rdkit-molecular-dependency、protein-pocket-pdb-format

## 证据来源
[1] Khodabandeh Yalabadi A, Yazdani-Jahromi M, Garibay OO. BoKDiff: best-of-K diffusion alignment for target-specific 3D molecule generation. Bioinformatics Advances. 2025;5(1):vbaf137. DOI: 10.1093/bioadv/vbaf137
[2] Wang Y, Ma Y, Chang YH, et al. Diffusion Models at the Drug Discovery Frontier: A Review on Generating Small Molecules Versus Therapeutic Peptides. Biology. 2025;14(12):1665. DOI: 10.3390/biology14121665
