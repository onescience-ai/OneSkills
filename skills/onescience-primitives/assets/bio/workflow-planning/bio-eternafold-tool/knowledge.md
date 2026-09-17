# EternaFold工具使用工作流

## 适用范围
**触发条件**：
- 需要预测RNA三维结构以验证设计序列
- 需要计算设计序列与目标结构的RMSD/TM-score
- 需要评估RNA设计质量

**适用场景**：
- RNA三维反向设计的质量评估
- RNA结构预测验证
- 设计序列的结构一致性检查

**不适用场景**：
- 仅需二级结构预测的任务
- 蛋白质结构预测任务

## 输入
- RNA序列（设计序列或天然序列）
- 目标结构（PDB格式，可选）
- 预测参数配置

## 输出
- 预测的RNA三维结构（PDB格式）
- 结构质量评估指标（RMSD、TM-score、LDDT）
- 预测置信度分数

## 流程节点

### Step 1：输入准备
- **操作**：准备RNA序列和目标结构文件
- **参数**：序列格式（FASTA）、结构格式（PDB）
- **工具**：文本编辑器、文件转换工具
- **质量门禁**：输入文件格式正确

### Step 2：模型加载
- **操作**：加载EternaFold预训练模型
- **参数**：模型路径、配置文件
- **工具**：Python脚本、模型加载器
- **质量门禁**：模型加载成功

### Step 3：结构预测
- **操作**：执行RNA结构预测
- **参数**：预测参数、计算资源
- **工具**：EternaFold预测脚本
- **质量门禁**：预测完成无错误

### Step 4：结果验证
- **操作**：验证预测结构质量
- **参数**：RMSD、TM-score、LDDT
- **工具**：结构比较工具（如US-align）
- **质量门禁**：质量指标达到阈值

### Step 5：结果输出
- **操作**：保存预测结构和评估报告
- **参数**：输出格式、文件命名
- **工具**：文件写入工具
- **质量门禁**：输出文件完整

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 输入格式 | PDB, FASTA | [1] | 标准格式 |
| 输出格式 | PDB | [1] | 标准结构文件 |
| RMSD阈值 | <5 Å | [1] | 结构相似性指标 |
| TM-score阈值 | >0.5 | [1] | 全局结构相似性 |
| LDDT阈值 | >0.7 | [1] | 局部距离差异 |
| 计算时间 | ~0.14 s | [2] | 单结构预测时间 |

## 边界与分流
- **预测失败**：检查输入格式或降低参数复杂度
- **质量不达标**：调整预测参数或使用其他工具
- **计算资源不足**：使用云计算或降级到二级结构预测

## 质量检查
- 验证预测结构可被Pymol/Mol*可视化
- 验证RMSD、TM-score等指标在合理范围
- 验证预测置信度分数

## 回退策略
- 使用其他RNA结构预测工具（如RhoFold+）
- 使用二级结构预测作为替代
- 联系工具开发者获取技术支持

## 资源召回建议
- 当需要验证RNA设计序列结构时召回本卡片
- 配合`bio-rna-inverse-folding-gRNAde-weights`使用
- 配合`bio-rna-sequence-recovery-evaluation`使用

## 证据来源
[1] "RiboDiffusion: tertiary structure-based RNA inverse folding with generative diffusion models", Bioinformatics, 2024, DOI: 10.1093/bioinformatics/btae259
[2] "R3Design: deep tertiary structure-based RNA sequence design and beyond", Briefings in Bioinformatics, 2024, DOI: 10.1093/bib/bbae682