# AlphaGenome模型配置与推理

## 适用范围
- 触发条件：需要使用AlphaGenome模型进行调控变异效应预测
- 适用场景：BRCA1调控变异多轨迹预测、表观基因组效应评估、变异功能注释
- 不适用场景：非AlphaGenome模型、非人类基因组、非调控变异预测

## 输入
- AlphaGenome模型checkpoint路径（orbax格式权重目录）
- 变异对象列表（chr/pos/ref/alt）
- 目标基因组区间（interval）
- 请求的输出轨迹类型列表

## 输出
- VariantOutput对象，包含各轨迹预测值
- 预测结果数据结构（轨迹名称、数值、单位）
- 模型加载日志（checkpoint路径、organism、device信息）

## 流程节点

### 步骤1：构建OrganismSettings
- **操作**：配置HOMO_SAPIENS的文件路径
- **参数**：FASTA、GTF、PAS、splice-site文件路径
- **工具**：AlphaGenome SDK
- **质量门禁**：所有路径指向真实存在的文件

### 步骤2：加载AlphaGenome模型
- **操作**：调用AlphaGenomeModel.create()
- **参数**：checkpoint_path、organism_settings、model_settings、device
- **工具**：AlphaGenomeModel.create()
- **质量门禁**：模型实例创建成功，无加载错误

### 步骤3：构建Variant对象
- **操作**：为每个变异创建Variant对象
- **参数**：chr（染色体）、pos（1-based坐标）、ref（参考等位基因）、alt（替代等位基因）
- **工具**：AlphaGenome Variant类
- **质量门禁**：Variant对象包含完整的chr/pos/ref/alt信息

### 步骤4：调用predict_variant
- **操作**：对每个变异执行预测
- **参数**：Variant对象、interval、requested_outputs轨迹列表
- **工具**：AlphaGenomeModel.predict_variant()
- **质量门禁**：返回VariantOutput对象，无NaN/Inf值

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型权重标识 | alphagenome-all-folds | [AlphaGenome文档] | 预训练模型权重 |
| 生物体 | HOMO_SAPIENS | [AlphaGenome文档] | 人类基因组 |
| 上下文长度 | 1048576 (1Mb) | [AlphaGenome文档] | 默认最大上下文 |
| 输出轨迹 | ATAC/CAGE/RNA_SEQ/DNASE/CHIP_TF/CHIP_HISTONE/SPLICE_SITES | [AlphaGenome源码] | 7种标准轨迹 |
| 设备 | GPU/CPU | [JAX文档] | 计算设备选择 |

## 边界与分流
- **模型加载失败**：检查checkpoint路径和organism_settings配置
- **显存不足**：切换到CPU设备或减小batch_size
- **轨迹类型不支持**：从requested_outputs中移除不支持的类型
- **预测结果异常**：检查输入变异坐标和参考等位基因

## 质量检查
- 确认模型加载日志包含checkpoint路径、organism、device信息
- 验证predict_variant返回值中各轨迹shape正确
- 检查预测值为有限值（非NaN/Inf）
- 确认输出轨迹包含全部7种类型

## 回退策略
- 模型加载失败时检查文件权限和依赖库版本
- GPU显存不足时切换到CPU模式
- 预测超时时增加超时时间或分批处理

## 资源召回建议
- 何时应召回本卡片：使用AlphaGenome模型进行变异预测、配置OrganismSettings、调用predict_variant方法
- 配套资源：AlphaGenome checkpoint文件、GRCh38参考基因组、GTF注释文件

## 证据来源
[1] Advancing regulatory variant effect prediction with AlphaGenome, DeepMind, Nature, 2026, DOI: 10.1038/s41586-026-08849-4
[2] AlphaGenome: a framework for integrated regulatory variant interpretation, International Journal of Biological Sciences, 2026
[3] Benchmarking DNA foundation models for genomic and genetic tasks, Nature Communications, 2025, DOI: 10.1038/s41467-025-56619-0
[4] Harnessing artificial intelligence for genomic variant prediction, GigaScience, 2026, DOI: 10.1093/gigascience/giad119