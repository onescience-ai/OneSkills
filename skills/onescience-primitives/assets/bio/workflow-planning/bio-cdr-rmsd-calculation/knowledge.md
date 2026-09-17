# CDR-RMSD计算方法

## 适用范围
适用于评估抗体CDR环结构预测质量的场景，包括：
- 生成抗体CDR构象验证
- 结构预测模型性能评估
- 抗体设计质量控制
- 模型间结构比较

不适用场景：
- 非CDR区域的结构比较
- 序列相似性评估（需使用其他指标）

## 输入
- **结构文件**：PDB格式抗体结构（预测结构和参考结构）
- **CDR定义**：CDR区域的残基编号（基于IMGT或其他编号方案）
- **比对参数**：比对算法选择、权重设置

## 输出
- **RMSD值**：各CDR环的RMSD值（单位：Å）
- **统计指标**：平均RMSD、标准差、异常值标记
- **比对结果**：结构比对后的坐标和变换矩阵

## 流程节点
1. 结构预处理 → 2. CDR区域提取 → 3. 结构比对 → 4. RMSD计算 → 5. 结果验证
   - 步骤1：加载PDB结构，提取CDR区域原子坐标
   - 步骤2：根据编号方案确定CDR残基范围
   - 步骤3：使用Kabsch或US-align算法进行结构比对
   - 步骤4：计算比对后原子坐标的RMSD
   - 步骤5：验证结果合理性，标记异常值

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| alignment_algorithm | Kabsch | [1] | 最小二乘结构比对算法 |
| alignment_algorithm | US-align | [2] | 通用结构比对工具 |
| rmsd_threshold | 2.0Å | [1] | 通常认为<2.0Å为高质量预测 |
| outlier_threshold | 3.0Å | [1] | 超过此值视为异常预测 |
| atom_selection | CA/CB | [1] | 选择α碳或β碳原子进行计算 |

## 边界与分流
- **缺失原子**：跳过缺失残基，使用可用原子计算
- **多构象结构**：分别计算各构象的RMSD
- **链不匹配**：按链分别比对，保持链标识

## 质量检查
- 验证比对质量（TM-score>0.5）
- 检查RMSD值合理性（通常0-5Å范围）
- 确认CDR区域定义一致

## 回退策略
- 比对失败时：尝试不同比对算法或参数
- RMSD异常时：检查结构质量和CDR定义
- 工具不可用时：使用PyMOL或BioPython实现

## 资源召回建议
- 当任务涉及抗体结构验证时召回
- 当需要评估CDR预测质量时召回
- 配套资源：ABlooper、IgFold、ImmuneBuilder

## 证据来源
[1] Abanades B, et al. ABlooper: fast accurate antibody CDR loop structure prediction with accuracy estimation. Bioinformatics. 2022;38(7):1877-1880. DOI: 10.1093/bioinformatics/btac016
[2] Ruffolo JA, et al. Fast, accurate antibody structure prediction from deep learning on massive set of natural antibodies. Nature Communications. 2023;14:2075. DOI: 10.1038/s41467-023-38063-x