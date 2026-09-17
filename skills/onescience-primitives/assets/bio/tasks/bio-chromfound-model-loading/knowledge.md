# ChromFound模型加载任务

## 适用范围

**触发条件**：
- 任务需要使用ChromFound预训练模型进行scATAC-seq分析
- 需要加载chromfound.pt权重文件
- 需要生成细胞嵌入表征用于下游分析

**适用场景**：
- scATAC-seq数据的细胞表征学习
- 细胞类型注释和聚类分析
- 跨数据集的迁移学习
- 调控元件功能预测

**不适用场景**：
- 无GPU环境（ChromFound需要CUDA 12.1+支持）
- 内存不足（模型需要较大显存）
- 无网络连接（需要下载预训练权重）

## 输入

- **数据格式**：H5AD（AnnData）格式
- **必需字段**：
  - `X`：peak × cell 稀疏计数矩阵
  - `obs`：细胞元数据，必须包含 `cell_type` 列
  - `var`：特征元数据，必须包含：
    - `#Chromosome`：染色体索引（整数）
    - `hg38_Start`：0-based 起始基因组坐标
    - `hg38_End`：0-based 结束基因组坐标（exclusive）
- **预训练权重文件**：
  - `model.pt`：模型权重文件
  - `chromfd_pretrain.yaml`：模型配置文件
  - `chromosome_vocab.yaml`：染色体索引映射文件

## 输出

- **细胞嵌入表征**：低维向量（默认32维），存储于指定输出路径
- **嵌入元数据**：包含细胞类型、批次等信息的H5AD文件
- **模型配置**：使用的预训练模型参数摘要

## 流程节点

### Step 1：环境配置
- **操作**：创建conda环境并安装依赖
- **命令**：
  ```bash
  conda env create -f environment.yml
  conda activate chromfound
  pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu121
  pip install mamba-ssm==2.2.4
  pip install flash-attn==2.7.2.post1 --no-build-isolation
  ```
- **质量门禁**：环境创建成功，依赖安装无错误

### Step 2：下载预训练权重
- **操作**：从官方来源下载权重文件
- **下载源**：
  1. HuggingFace: https://huggingface.co/YifengJiao/ChromFound
  2. Google Drive: https://drive.google.com/drive/folders/1wSq9gPwnUmSiw3obz1mjyX2ZiXS8sWbf
- **文件列表**：
  - `model.pt`
  - `chromfd_pretrain.yaml`
  - `chromosome_vocab.yaml`
- **放置路径**：`src/checkpoints/`
- **质量门禁**：所有文件下载成功，文件大小合理

### Step 3：加载模型
- **操作**：初始化ChromFound模型并加载权重
- **代码示例**：
  ```python
  python -m src/cell_embedding \
      --data_path <input_h5ad> \
      --output_path <output_dir> \
      --pretrain_checkpoint_path src/checkpoints \
      --pretrain_model_file model.pt \
      --pretrain_config_file chromfd_pretrain.yaml \
      --batch_size 16 \
      --cell_type_col celltype
  ```
- **质量门禁**：模型加载成功，无权重缺失错误

### Step 4：生成细胞嵌入
- **操作**：使用加载的模型生成细胞表征
- **参数**：
  - `batch_size`：默认16，根据GPU显存调整
  - `cell_type_col`：细胞类型列名（如celltype, cell_type）
- **输出**：嵌入表征矩阵（n_cells × embedding_dim）
- **质量门禁**：输出维度正确，无NaN值

### Step 5：保存结果
- **操作**：将嵌入表征保存为H5AD格式
- **内容**：
  - `X`：嵌入表征矩阵
  - `obs`：原始细胞元数据 + 嵌入信息
  - `uns`：模型配置和训练参数
- **质量门禁**：文件可正常加载，数据完整

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 官方仓库 | https://github.com/SAIS-LifeScience/ChromFound | [1] | 源代码和文档 |
| 预训练权重 | HuggingFace: YifengJiao/ChromFound | [1] | 模型权重下载 |
| Python版本 | 3.10+ | [1] | 系统要求 |
| CUDA版本 | 12.1+ | [1] | GPU支持要求 |
| PyTorch版本 | 2.2.2 | [1] | 深度学习框架 |
| mamba-ssm版本 | 2.2.4 | [1] | 状态空间模型 |
| flash-attn版本 | 2.7.2.post1 | [1] | 注意力加速 |
| 默认batch_size | 16 | [1] | 推理批大小 |
| 输出维度 | 32 | [1] | 细胞嵌入维度 |

## 边界与分流

- **无GPU环境**：标记BLOCKED，说明需要CUDA 12.1+支持
- **权重下载失败**：尝试备选下载源（Google Drive），或标记BLOCKED
- **内存不足**：减小batch_size，或使用更小的模型配置
- **数据格式不匹配**：检查var中的染色体坐标信息是否完整

## 质量检查

- 验证点1：conda环境创建成功，所有依赖安装无错误
- 验证点2：预训练权重文件完整（model.pt, chromfd_pretrain.yaml, chromosome_vocab.yaml）
- 验证点3：模型加载成功，权重无缺失
- 验证点4：输出嵌入表征维度正确，无NaN值
- 验证点5：输出H5AD文件可正常加载

## 回退策略

- **首选**：从HuggingFace下载权重
- **备选1**：从Google Drive下载权重
- **备选2**：使用通用VAE从头训练（需降低预期性能）
- **最终方案**：标记BLOCKED，说明无法加载模型的原因

## 资源召回建议

- **召回场景**：当任务需要使用ChromFound模型但权重不可用时
- **配套资源**：
  - scATAC-seq数据获取任务（提供输入数据）
  - TF-IDF归一化预处理（数据需要正确预处理）
  - 细胞类型注释评估（评估嵌入质量）

## 证据来源

[1] Jiao, Y. et al. "ChromFound: Towards A Universal Foundation Model for Single-Cell Chromatin Accessibility Data". arXiv:2505.12638, 2025
