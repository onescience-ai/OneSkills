# AlphaGenome 深度学习模型配置与接口

## 适用范围

**触发条件**：
- 需要加载和配置 AlphaGenome 模型进行非编码变异效应预测
- 需要设置小鼠 (MUS_MUSCULUS) 物种的 organism_settings
- 需要使用 predict_variant 接口进行组织特异的调控信号预测

**适用场景**：
- 小鼠增强子变异的组织特异调控预测
- 跨模态（表达、剪接、染色质可及性、TF 结合）变异效应评分
- 基于 1 Mb 上下文的长程调控元件影响评估

**不适用场景**：
- 蛋白质结构预测（应使用 AlphaFold）
- 编码区变异的致病性预测（应使用 AlphaMissense）
- 无 GPU 环境的轻量级推理（AlphaGenome 需要 JAX GPU）

## 输入

| 输入 | 格式 | 说明 |
|------|------|------|
| DNA 序列 | 1 Mb 窗口，ATCGN 字符 | 以变异位点为中心的参考和替代序列 |
| 物种标识 | "HUMAN" 或 "MUS_MUSCULUS" | 决定使用的参考基因组和注释文件 |
| 变异信息 | 位置 + REF + ALT | 标准基因组坐标 |
| requested_outputs | 轨迹类型列表 | 如 [ATAC, CAGE, RNA_SEQ] |

## 输出

| 输出 | 格式 | 说明 |
|------|------|------|
| 基因组轨迹预测 | NumPy 数组 | 每 bp 或 bin 的信号值 |
| 变异效应评分 | VariantOutput 对象 | 含轨迹差异和元数据 |
| 跨模态热图 | 多轨迹 delta 值 | 变异对各模态的影响 |

## 流程节点

### Step 1：环境准备
- **操作**：安装 JAX、Haiku、Orbax 等依赖
- **参数**：jax>=0.4、dm-haiku、orbax-checkpoint、CUDA 12+
- **工具**：pip/conda 安装
- **质量门禁**：`python -c "import jax; print(jax.devices())"` 显示 GPU 设备

### Step 2：模型加载
- **操作**：调用 AlphaGenomeModel.create() 加载 checkpoint
- **参数**：checkpoint_path（Orbax 格式）、organism_settings、model_settings
- **工具**：AlphaGenome API
- **质量门禁**：模型参数加载成功、organism 注释文件路径有效

### Step 3：构造输入窗口
- **操作**：以变异位点为中心提取 1 Mb 参考序列和替代序列
- **参数**：窗口大小=1,048,576 bp、坐标体系对齐
- **工具**：FASTA 索引查询
- **质量门禁**：序列长度=1 Mb、无 N 碱基过多（<10%）

### Step 4：执行预测
- **操作**：对参考和替代序列分别调用 predict_variant
- **参数**：requested_outputs、organism_terms（UBERON 本体项）
- **工具**：AlphaGenome predict_variant 接口
- **质量门禁**：输出轨迹维度匹配、无 NaN 值

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 输入序列长度 | 1,048,576 bp (1 Mb) | [1] | 覆盖 99% 已验证增强子-基因对 |
| 人类轨迹数 | 5,930 | [1] | 跨 11 种模态 |
| 小鼠轨迹数 | 1,128 | [1] | 跨 11 种模态 |
| 输出分辨率 | 1 bp（大部分轨迹） | [1] | 剪接位点和表达轨迹 |
| 接触图分辨率 | 2,048 bp | [1] | 二维嵌入 |
| 框架 | JAX + Haiku | [1] | U-Net 风格骨干架构 |
| 训练设备 | 8× TPU v3 或等效 GPU | [1] | 序列并行 |
| 推理速度 | <1 s/变异（H100 GPU） | [1] | 蒸馏后的学生模型 |
| 物种支持 | HUMAN, MUS_MUSCULUS | [1] | 人类和小鼠基因组 |
| 剪接输出类型 | splice sites, usage, junctions | [1] | 三种剪接相关模态 |
| 表达输出类型 | RNA-seq, CAGE, PRO-cap | [1] | 三种表达相关模态 |
| 染色质输出类型 | DNase, ATAC, ChIP-seq (组蛋白) | [1] | 染色质状态模态 |
| TF 结合输出 | 转录因子 ChIP-seq | [1] | TF binding modality |
| 接触图输出 | Hi-C, Micro-C | [1] | 三维基因组架构 |

## MUS_MUSCULUS organism_settings 配置

```python
organism_settings = {
    "organism": "MUS_MUSCULUS",
    "fasta_path": "reference/MUS_MUSCULUS/mm10.fa",
    "metadata_path": "reference/MUS_MUSCULUS/metadata.json",
    "gtf_path": "reference/MUS_MUSCULUS/gencode.vM25.annotation.gtf.gz",
    "pas_path": "reference/MUS_MUSCULUS/pas_sites.bed",
    "splice_site_path": "reference/MUS_MUSCULUS/splice_sites.bed"
}
```

- 目录结构：`reference/MUS_MUSCULUS/` 下包含所有注释文件
- FASTA 为 mm10 参考基因组
- GTF 为 GENCODE 小鼠基因注释
- PAS 和 splice_site 为预处理的剪接和多聚腺苷酸化位点注释

## predict_variant 接口契约

```python
# 输入
variant = Variant(
    chrom="chr1",
    pos=1000000,
    ref="A",
    alt="G"
)
interval = Interval(
    chrom="chr1",
    start=1000000 - 524288,  # 1 Mb 窗口中心对齐
    end=1000000 + 524288
)
requested_outputs = ["ATAC", "CAGE", "RNA_SEQ"]

# 调用
output = model.predict_variant(
    interval=interval,
    variant=variant,
    requested_outputs=requested_outputs,
    organism_settings=organism_settings
)

# 输出
# output.predicted_traces: Dict[str, np.ndarray]  # 各轨迹的预测值
# output.variant_effect: VariantEffect  # delta_score 和方向
```

## 边界与分流

- **JAX GPU 不可用**：标记 BLOCKED，申请 SLURM 计算节点或配置 CUDA 环境
- **Checkpoint 缺失**：从 OneScience datasets 目录或 ModelScope 下载
- **序列含过多 N**：扩展窗口或跳过该区域，记录在质量报告中
- **organism_settings 文件不全**：逐文件检查并报告缺失项

## 质量检查

| 检查项 | 阈值 | 失败处理 |
|--------|------|----------|
| JAX GPU 可用 | ≥1 GPU 设备 | 标记 BLOCKED |
| Checkpoint 加载 | 参数加载无错误 | 重新下载 checkpoint |
| 序列长度 | =1,048,576 bp | 调整窗口边界 |
| 输出轨迹维度 | 与 requested_outputs 匹配 | 检查请求的轨迹类型 |
| NaN 值 | =0 | 检查输入序列质量 |

## 回退策略

- 本地 GPU 不可用 → 委托 onescience-runsite 申请 SLURM GPU 节点
- Checkpoint 下载失败 → 使用 OneScience datasets 公共路径
- 模型加载超时 → 检查内存并减少 batch size

## 资源召回建议

- 当任务需要 AlphaGenome 模型进行变异效应预测时召回本卡
- 配套资源：mm10 数据验证卡（bio-mm10-reference-data-validation）、UBERON 映射卡（bio-uberon-tissue-mapping-prediction）

## 证据来源

[1] "Advancing regulatory variant effect prediction with AlphaGenome", Avsec et al., Nature, 2026, DOI: 10.1038/s41586-025-10014-0
[2] "Predicting non-coding variant effects with AlphaGenome", Murphy et al., Cell Research, 2026, DOI: 10.1038/s41422-026-01249-1
[3] "The AlphaGenome deep learning model predicts effects of non-coding variants", Gankin & Beltrao, Nature Structural & Molecular Biology, 2026, DOI: 10.1038/s41594-026-01763-1
