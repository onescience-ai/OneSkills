# 蛋白配体对接几何修正任务

## 适用范围

**触发条件**：
- 对接采样产生物理不合理的姿态
- 需要验证蛋白-配体复合物的几何有效性
- 需要对 AI 对接模型（DiffDock 等）的输出进行后处理

**适用场景**：
- 对接结果的后处理和质量控制
- 扩散模型对接输出的物理有效性修正
- 跨对接（cross-docking）场景的姿态优化

**不适用场景**：
- 对接采样本身（那是 Step 3 的职责）
- 蛋白质结构的几何优化（那是结构准备的职责）

## 输入

- 对接采样输出的姿态集合（PDB/MOL2 格式）
- 受体蛋白质结构
- 几何修正参数配置

## 输出

- 几何修正后的有效姿态集合
- PoseBusters 验证报告
- 修正统计（修正率、失败率）

## 操作步骤

### Step 1：立体冲突检测
- 检测蛋白-配体间的原子碰撞（clash）
- 计算 clash score（冲突原子对数/总原子数）
- 标记严重冲突（距离 < 0.5 Å 的原子对）
- 工具：PoseBusters, PyMOL, UCSF Chimera

### Step 2：键长键角校正
- 校正配体的异常键长（超出标准值 ± 0.3 Å）
- 校正异常键角（超出标准值 ± 20°）
- 保持手性中心构型
- 工具：Open Babel, RDKit, MMFF94 force field

### Step 3：能量最小化与 MD Relaxation
- 对修正后的复合物进行短时 MD relaxation（100-500 ps）
- 使用约束力场（位置约束蛋白，放松配体）
- 收集能量最低构象
- 工具：OpenMM, GROMACS, AMBER

### Step 4：PoseBusters 验证
- 运行 PoseBusters 检查套件
- 检查键长、键角、二面角、平面性、手性、立体冲突
- 生成验证报告（通过/失败/警告）
- 工具：PoseBusters Python 包

### Step 5：相互作用验证
- 检查关键蛋白-配体相互作用（氢键、盐桥、π-π 堆积）
- 与参考晶体结构的相互作用模式对比
- 工具：PLIP, ProBis, Arpeggio

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Clash score | < 0.1 | [1] | 冲突原子对比例 |
| 键长容差 | ± 0.3 Å | [2] | 相对于标准值的偏差 |
| 键角容差 | ± 20° | [2] | 相对于标准值的偏差 |
| MD relaxation | 100-500 ps | [1] | 短时弛豫消除紧张构象 |
| PoseBusters 通过率 | > 80% | [3] | 质量门禁标准 |
| RMSD 阈值 | < 2 Å (redock), < 4 Å (cross-dock) | [3] | 姿态质量判定 |

## 边界与分流

- **扩散模型输出**：AI 对接模型（DiffDock）常产生物理不合理的姿态，需要更强的几何修正 [1]
- **经典对接输出**：Vina/GNINA 输出通常几何质量较好，但仍需验证 [3]
- **跨对接场景**：由于蛋白构象差异，RMSD 阈值应放宽至 < 4 Å [3]
- **无法修正的姿态**：直接丢弃，标记为对接失败

## 质量检查

- PoseBusters 所有检查项通过
- 无严重立体冲突（clash score < 0.1）
- 关键蛋白-配体相互作用保留
- 能量收敛（MD 最终能量 < 初始能量）

## 回退策略

- MD relaxation 失败时：仅执行几何修正（键长键角校正）
- PoseBusters 通过率过低时：降低冲突检测阈值或仅修正严重冲突
- 相互作用丢失时：回退到未修正的原始姿态

## 资源召回建议

- 当需要理解对接工作流整体流程时：召回 `bio-protein-ligand-docking-workflow`
- 当需要数据准备时：召回 `bio-protein-ligand-docking-data-preparation`

## 证据来源

[1] Broster JH, et al. "Teaching diffusion models physics: reinforcement learning for physically valid diffusion-based docking." Chem Sci, 2026. DOI: 10.1039/d6sc02655a
[2] Sim J, Lee J. "BA-Pred and RMSD-Pred: Integrated Graph Neural Network Models for Accurate Protein-Ligand Binding Affinity and Binding Pose Prediction." J Chem Inf Model, 2026, 66(7):3480-3495. DOI: 10.1021/acs.jcim.5c02591
[3] Gaskin L, et al. "Enhanced Line Search Improves Robustness and Efficiency of Pose Sampling in Protein-Ligand Docking." J Chem Theory Comput, 2026, 22(17):9188-9198. DOI: 10.1021/acs.jctc.6c01110
