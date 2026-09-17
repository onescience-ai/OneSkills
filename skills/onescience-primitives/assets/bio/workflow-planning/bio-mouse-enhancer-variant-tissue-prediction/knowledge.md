# 小鼠增强子变异的组织特异调控预测

## 适用范围

**触发条件**：
- 需要预测小鼠增强子区域的非编码变异对组织特异性基因调控的影响
- 已有 mm10 参考基因组、增强子 BED 文件和变异 VCF 文件
- 需要在肝脏（UBERON:0002107）和大脑（UBERON:0000955）等组织中评估变异效应

**适用场景**：
- 小鼠增强子变异的功能注释
- 组织特异性调控元件的变异效应预测
- 非编码变异的跨组织比较分析
- 实验候选变异的优先级排序

**不适用场景**：
- 编码区变异的致病性预测（应使用 AlphaMissense 等工具）
- 人类基因组的变异效应预测（需使用 GRCh38 参考基因组）
- 无参考基因组的物种

## 输入

### 参考基因组文件
- **mm10_reference.fasta**：小鼠参考基因组 FASTA 文件
  - 格式要求：>=2-bit FASTA，支持 gzip 压缩
  - 染色体命名：chr1-chr19, chrX, chrY, chrM（UCSC 格式）
  - 碱基字符：仅允许 A/T/C/G/N
  - 获取路径：UCSC Genome Browser (https://genome.ucsc.edu/) 或 GRCm38.p6
  - 验证项：文件可读性、染色体计数（应含 21 条染色体）、MD5 完整性

### 增强子 BED 文件
- **mm10_enhancers.bed**：增强子区间文件
  - 格式：BED6（chrom/start/end/name/score/strand）
  - 坐标系统：0-based half-open [start, end)
  - 验证项：chrom 在参考范围内、start < end、strand 为 +/-/.、与 FASTA 染色体列表一致
  - 推荐来源：ENCODE、FANTOM5、Vista Enhancer Database

### 变异 VCF 文件
- **mm10_enhancer_variants.vcf**：增强子区域变异文件
  - 格式：VCF 4.3+
  - 必需字段：CHROM, POS, ID, REF, ALT
  - 验证项：POS > 0、REF 和 ALT 为 [ATCGN]+、变异位于增强子 BED 邻域内
  - 坐标系统：1-based inclusive

### 基因组坐标转换约定
| 格式 | 坐标系统 | 示例 |
|------|----------|------|
| BED | 0-based half-open | chr1:1000-2000 表示 [1000, 2000) |
| VCF | 1-based inclusive | chr1:1001 表示位置 1001 的变异 |
| GFF/GTF | 1-based inclusive | chr1:1000-2000 表示 [1000, 2000] |

## 输出

### 标准化增强子表
- 包含经过验证的增强子区间
- 附带坐标质控报告（MD5、染色体列表、变异-BED 邻域包含性检查）

### 组织分层轨迹预测
- UBERON 本体项映射（肝脏→UBERON:0002107，大脑→UBERON:0000955）
- 三种标准轨迹：ATAC、CAGE、RNA_SEQ
- 等位基因差异（参考 vs 替代）
- 方向一致性日志（正反向映射可复核）

### 组织特异排序
- 标准化效应值（per_track_robust_z）
- 轨迹内排名（rank）
- 实验候选列表（top N 变异）

### 适用边界报告
- 标准化公式和参数
- MAD=0 回退规则记录
- 背景样本量统计

## 流程节点

### Step 0：环境预检（preflight）
- **操作**：检测本地环境是否满足执行条件
- **检查项**：
  - JAX 版本 >= 0.4
  - CUDA/GPU 可用性
  - AlphaGenome checkpoint 存在性
  - organism 注释文件完整性
- **工具**：onescience-installer（preflight 模式）
- **质量门禁**：preflight_passed=true, execution_readiness=ready
- **失败处理**：
  - 缺少 JAX/GPU → 委托 onescience-runsite 申请计算节点
  - 缺少 checkpoint → 从 OneScience datasets 或 ModelScope 下载
  - 标记 BLOCKED 并提供恢复指南

### Step 1：输入规范化（s01）
- **操作**：验证并规范化输入文件
- **参数**：
  - FASTA 验证：染色体计数、碱基合法性、MD5
  - BED 验证：坐标有效性、链方向、与 FASTA 一致性
  - VCF 验证：字段完整性、REF/ALT 合法性、位置有效性
- **工具**：ReferenceGenomeVerifier, BedValidator, VcfValidator
- **质量门禁**：所有验证项 PASS
- **输出**：标准化增强子表、变异窗口、坐标质控报告

### Step 2：模型加载（s02）
- **操作**：加载 AlphaGenome 模型和 organism 配置
- **参数**：
  - checkpoint_path：Orbax 格式路径
  - organism_settings：MUS_MUSCULUS 配置
    - fasta_path：mm10 FASTA 路径
    - metadata_path：元数据文件路径
    - gtf_path：基因注释文件路径
    - pas_path：多聚腺苷酸化位点文件路径
    - splice_site_path：剪接位点文件路径
  - model_settings：num_splice_sites=512, splice_site_threshold=0.1
- **工具**：AlphaGenomeModel.create()
- **质量门禁**：模型加载成功，organism 配置完整
- **输出**：模型加载记录（checkpoint 版本、许可、参数规模）

### Step 3：组织条件预测（s03）
- **操作**：按组织本体项执行调控信号预测
- **参数**：
  - ontology_terms：[UBERON:0002107, UBERON:0000955]
  - requested_outputs：[ATAC, CAGE, RNA_SEQ]
  - interval：增强子区间（Interval 对象）
  - variant：变异对象（Variant 对象）
- **工具**：AlphaGenome predict_variant 接口
- **质量门禁**：
  - tissue_context 为 UBERON 本体项（非英文名）
  - requested_outputs 仅包含标准 3 种轨迹
  - 方向一致性日志完整
- **反向互补检查**：
  - 对 DNA 序列执行 reverse-complement
  - 重新预测并对比结果
  - 记录方向一致性
- **输出**：组织分层轨迹预测、等位基因差异、方向一致性日志

### Step 4：跨轨迹汇总（s04）
- **操作**：标准化、背景比对、候选筛选
- **参数**：
  - 标准化方法：per_track_robust_z
  - 背景变异集：mm10_matched_background.vcf
  - 效应阈值：2
  - 轨迹内秩阈值：0.95
  - 候选数量：15
  - 输出格式：csv
- **标准化公式**：
  ```
  z = (x - median) / MAD
  MAD = median(|x - median(x)|)
  ```
- **MAD=0 回退规则**：
  - 若 MAD = 0，使用 std 替代
  - 或标记为不可标准化
- **背景变异集匹配规则**：
  - 按染色体匹配
  - 按等位基因频率或基因组位置匹配
- **轨迹内秩阈值**：
  - 0.95 表示仅保留每个轨迹中效应排名前 5% 的变异
- **跨轨迹聚合策略**：
  - per_track 约束：原始值不跨轨迹相加
  - 聚合方式：max、mean 或加权组合
- **质量门禁**：
  - standardized_effects.csv 包含 z-score 字段
  - candidate_variants.csv 包含 rank 和组织标签
  - applicability_report.json 包含标准化公式和 MAD 回退记录
- **输出**：组织特异排序 CSV、效应汇总、适用边界报告

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 参考基因组版本 | mm10 (GRCm38) | [1] | 小鼠参考基因组 |
| 组织本体项（肝脏） | UBERON:0002107 | [3] | 肝脏组织标准本体 |
| 组织本体项（大脑） | UBERON:0000955 | [3] | 大脑组织标准本体 |
| 标准输出轨迹 | ATAC, CAGE, RNA_SEQ | [2] | AlphaGenome 标准轨迹 |
| 标准化方法 | per_track_robust_z | [4] | 鲁棒 z-score 标准化 |
| 轨迹内秩阈值 | 0.95 | [4] | 保留前 5% 变异 |
| 效应阈值 | 2 | [4] | 最小效应大小 |
| 模型框架 | JAX/Haiku | [1] | AlphaGenome 依赖 |
| 上下文长度 | 1,048,576 bp | [1] | AlphaGenome 窗口大小 |

## 边界与分流

### 环境限制
- **JAX GPU 不可用**：委托 onescience-runsite 申请 SLURM 计算节点
- **checkpoint 缺失**：从 OneScience datasets 目录下载
  - 路径：/public/share/sugonhpcapp01/onestore/onedatasets/AlphaGenome
  - 或从 ModelScope 下载
- **organism 注释文件缺失**：标记 BLOCKED 并提供下载指南

### 数据质量异常
- **FASTA 染色体计数异常**：检查是否使用了正确的参考基因组版本
- **VCF REF/ALT 非法字符**：过滤或修正变异记录
- **BED 坐标越界**：检查坐标系统是否一致（0-based vs 1-based）

### 标准化异常
- **MAD=0**：使用 std 替代或标记为不可标准化
- **背景变异集不足**：降低匹配严格度或使用全局背景
- **轨迹内秩阈值无候选**：降低阈值或增加候选数量

## 质量检查

### 输入验证
- [ ] mm10_reference.fasta 染色体计数 = 21
- [ ] mm10_reference.fasta 碱基字符仅含 ATCGN
- [ ] mm10_enhancers.bed 所有 start < end
- [ ] mm10_enhancers.bed strand 为 +/-/.
- [ ] mm10_enhancer_variants.vcf POS > 0
- [ ] mm10_enhancer_variants.vcf REF/ALT 为 [ATCGN]+
- [ ] 变异位于增强子 BED 邻域内

### 模型验证
- [ ] AlphaGenome checkpoint 加载成功
- [ ] organism_settings 包含所有必需字段
- [ ] JAX 版本 >= 0.4
- [ ] GPU 可用性确认

### 预测验证
- [ ] tissue_context 为 UBERON 本体项
- [ ] requested_outputs 为 [ATAC, CAGE, RNA_SEQ]
- [ ] 方向一致性日志完整
- [ ] 预测值在合理范围内

### 标准化验证
- [ ] per_track_robust_z 计算正确
- [ ] MAD=0 回退规则已执行
- [ ] 轨迹内秩计算正确
- [ ] 候选列表包含 top N 变异

## 回退策略

### 环境回退
- 本地环境不支持 → 申请远程计算节点
- checkpoint 缺失 → 使用公开可用的预训练权重
- GPU 内存不足 → 减小批次大小或使用 CPU 推理（性能下降）

### 数据回退
- 真实数据缺失 → 标记 BLOCKED（不使用合成数据）
- 部分文件缺失 → 仅处理可用文件并记录限制

### 标准化回退
- MAD=0 → 使用 std 或标记为不可标准化
- 背景变异集不足 → 使用全局背景或降低匹配严格度
- 轨迹内秩阈值无候选 → 降低阈值或增加候选数量

## 资源召回建议

**何时召回本卡片**：
- 用户提到"小鼠增强子变异"、"组织特异调控预测"、"AlphaGenome"
- 需要预测非编码变异对基因调控的影响
- 需要在多个组织中比较变异效应

**配套资源**：
- onescience-installer：环境安装和预检
- onescience-runsite：远程执行环境配置
- onescience-runtime：作业提交和执行管理
- onescience-primitives (mm10 相关)：参考基因组和注释文件

## 证据来源

[1] "AlphaGenome: a framework for integrated regulatory variant interpretation", Kwon et al., International Journal of Biological Sciences, 2026, DOI: 10.7150/ijbs.133555

[2] "CREsted: modeling genomic and synthetic cell-type-specific enhancers across tissues and species", Kempynck et al., Nature Methods, 2026, DOI: 10.1038/s41592-026-03057-2

[3] "An encyclopedia of human enhancer–gene regulatory interactions", Gschwind et al., Nature, 2026, DOI: 10.1038/s41586-026-10781-4

[4] "Benchmarking DNA foundation models for genomic and genetic tasks", Feng et al., Nature Communications, 2025, DOI: 10.1038/s41467-025-65823-8

[5] "Harnessing artificial intelligence for genomic variant prediction: advances, challenges, and future directions", Pakpahan et al., GigaScience, 2026, DOI: 10.1093/gigascience/giag004

[6] "Pre-training genomic language model with variants for better modeling functional genomics", Liu et al., npj Artificial Intelligence, 2026, DOI: 10.1038/s44387-026-00103-4

[7] "Nucleotide Transformer: building and evaluating robust foundation models for human genomics", Dalla-Torre et al., Nature Methods, 2024, DOI: 10.1038/s41592-024-02523-z
