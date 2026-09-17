# 抗体生成模型

## 适用范围
适用于需要生成抗体CDR环和骨架结构的场景，包括：
- CDR环与抗体骨架联合生成
- 抗体从头设计
- 结构预测和优化
- 治疗性抗体开发

不适用场景：
- 序列设计而非结构生成（使用语言模型）
- 非抗体蛋白质设计

## 输入
- **抗原结构**：PDB格式抗原结构或表位信息
- **抗体模板**：可选的抗体骨架结构
- **生成参数**：CDR类型、长度约束、多样性要求

## 输出
- **抗体结构**：生成的抗体3D结构（PDB格式）
- **CDR构象**：各CDR环的构象信息
- **质量指标**：置信度分数、结构合理性评估

## 流程节点
1. 输入准备 → 2. 模型加载 → 3. 推理生成 → 4. 后处理 → 5. 质量验证
   - 步骤1：准备抗原结构和抗体模板
   - 步骤2：加载预训练模型权重
   - 步骤3：执行模型推理生成抗体结构
   - 步骤4：优化结构，修复立体冲突
   - 步骤5：验证结构质量和合理性

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| model_type | AbODE/IgFold/ImmuneBuilder | [1] | 不同模型适用不同场景 |
| cdr_types | CDR-H1/H2/H3/L1/L2/L3 | [1] | 指定需要生成的CDR类型 |
| confidence_threshold | 0.7 | [1] | 置信度阈值，低于此值需人工审核 |
| device | GPU/CPU | [1] | 计算设备选择 |

## 边界与分流
- **GPU内存不足**：降低批次大小或使用CPU
- **模型加载失败**：检查权重文件和依赖库版本
- **生成质量差**：调整参数或尝试其他模型

## 质量检查
- 验证结构完整性（所有原子已生成）
- 检查立体冲突和能量合理性
- 确认CDR区域定义正确

## 回退策略
- 模型不可用时：使用其他生成模型
- 生成失败时：使用模板-based方法
- 质量不达标时：迭代优化或人工调整

## 资源召回建议
- 当任务涉及抗体结构生成时召回
- 当需要CDR环和骨架联合设计时召回
- 配套资源：ANARCD编号、SAbDab数据库、CDR-RMSD验证

## 证据来源
[1] Meng F, et al. A comprehensive overview of recent advances in generative models for antibodies. Computational and Structural Biotechnology Journal. 2024;22:1687-1699. DOI: 10.1016/j.csbj.2024.06.016
[2] Norman RA, et al. Computational approaches to therapeutic antibody design: established methods and emerging trends. Briefings in Bioinformatics. 2019;21(5):1549-1562. DOI: 10.1093/bib/bbz095