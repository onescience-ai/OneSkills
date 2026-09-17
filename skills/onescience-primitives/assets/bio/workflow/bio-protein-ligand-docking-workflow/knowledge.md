# 蛋白质-配体对接标准工作流

## 适用范围

**触发条件**：
- 执行蛋白质-配体对接任务时需要规划标准步骤序列
- 需要理解对接流程中各步骤的输入输出依赖关系
- 需要按 workflow 定义拆解对接任务

**适用场景**：
- 基于结构的虚拟筛选流程规划
- 对接任务的步骤拆解和执行顺序确定
- 对接流程中各阶段的质量控制

**不适用场景**：
- 非对接类任务（如分子动力学、同源建模）
- 无需工作流规划的简单单步对接

## 输入

- 任务描述中的 workflow 定义字段
- 蛋白质结构文件（PDB/mmCIF）
- 配体结构文件或化合物库
- 对接参数配置

## 输出

- 标准化的步骤序列（s01-s04 或等效步骤）
- 每步的输入输出契约定义
- 步骤间依赖关系图

## 流程节点

### Step 1：数据预处理（s01）
- **操作**：下载和标准化蛋白质-配体数据
- **输入**：PDB ID 或结构文件、化合物 SMILES/SD 文件
- **输出**：标准化的受体 PDB 文件、配体 MOL2 文件、数据集 CSV
- **依赖**：无前置依赖
- **工具**：Open Babel, RDKit, PDBFixer
- **质量门禁**：结构完整性检查通过，缺失原子修复

### Step 2：模型加载与配置（s02）
- **操作**：加载对接引擎和预训练模型权重
- **输入**：对接工具路径、模型权重文件（如 DeltaDock .pt）
- **输出**：就绪的对接引擎实例
- **依赖**：s01 完成
- **工具**：PyTorch, 对接引擎 API
- **质量门禁**：模型加载成功，GPU 可用性确认

### Step 3：口袋定义与采样（s03）
- **操作**：定义结合口袋并执行姿态采样
- **输入**：受体结构、配体库、口袋参数
- **输出**：采样姿态集合（PDB/MOL2）、初步打分
- **依赖**：s01 + s02 完成
- **工具**：AutoDock Vina, GNINA, DiffDock
- **质量门禁**：采样收敛性检查，输出姿态数 ≥ 100

### Step 4：筛选与几何修正（s04）
- **操作**：对采样结果进行打分排序和几何修正
- **输入**：采样姿态集合、打分参数
- **输出**：最终排序结果、几何修正后的有效姿态
- **依赖**：s03 完成
- **工具**：PoseBusters, PLIP, 打分函数
- **质量门禁**：PoseBusters 通过率 > 80%，富集因子 EF@1% > 5

### 依赖关系图

```
s01 (数据预处理)
  ↓
s02 (模型加载) ← 依赖 s01 的标准化数据
  ↓
s03 (口袋定义与采样) ← 依赖 s01 的受体/配体 + s02 的引擎
  ↓
s04 (筛选与修正) ← 依赖 s03 的采样结果
```

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 步骤数 | 4 (s01-s04) | [1] | 标准对接工作流步骤 |
| 数据预处理 | 质子化+加氢+能量最小化 | [1] | 受体/配体准备 |
| 模型权重 | DeltaDock .pt 或等效 | [报告] | 需要官方发布源 |
| 口袋大小 | 20-30 Å³ | [1] | 网格盒子尺寸 |
| 采样穷举度 | 8-32 | [1] | 影响结果质量 |
| 打分策略 | 共识打分（多函数组合） | [2] | 提升鲁棒性 |
| 几何修正 | PoseBusters + MD relaxation | [3] | 物理有效性验证 |

## 边界与分流

- **数据不可用时**：启动回退分支，使用公开 PDB 结构或替代数据集
- **模型权重缺失时**：标记 BLOCKED 并提出最小补充方案
- **计算资源不足时**：降低采样穷举度或使用 GPU 加速
- **跨对接场景**：可能需要更宽松的 RMSD 阈值（<4 Å）

## 质量检查

- 每步输入输出契约检查
- 步骤间依赖关系完整性验证
- 最终结果的 RMSD 和打分收敛性检查
- PoseBusters 物理有效性验证

## 回退策略

- 默认数据不可用时：使用 PDBbind 或 CrossDocked 公开数据集
- 默认模型不可用时：使用 AutoDock Vina 等经典工具替代
- 默认流程失败时：尝试替代对接引擎或降低参数精度

## 资源召回建议

- 当需要执行数据准备时：召回 `bio-protein-ligand-docking-data-preparation`
- 当需要执行几何修正时：召回 `bio-protein-ligand-docking-geometric-refinement`
- 当需要检索数据/模型资源时：召回 `bio-protein-ligand-docking-resource-retrieval`

## 证据来源

[1] Azam F, Almahmoud SA. "Open-Source Molecular Docking and AI-Augmented Structure-Based Drug Design: Current Workflows, Challenges, and Opportunities." Int J Mol Sci, 2026, 27(7):3302. DOI: 10.3390/ijms27073302
[2] Agha H, et al. "Data driven selection of consensus docking pipelines for structure based hit identification." npj Drug Discov, 2026, 3:37. DOI: 10.1038/s44386-026-00063-4
[3] Suri K, et al. "Cross-docking and redocking reveal distinct determinants of success." RSC Adv, 2026. DOI: 10.1039/d6ra05440d
