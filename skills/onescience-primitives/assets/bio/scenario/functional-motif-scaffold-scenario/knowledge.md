# 功能位点约束的蛋白骨架生成场景

## 适用范围

**适用场景**：
- 酶活性位点支架设计：围绕给定催化残基生成蛋白骨架
- 结合蛋白支架构建：为靶标蛋白设计结合界面
- 金属结合蛋白设计：生成配位几何约束的金属结合位点
- 治疗性蛋白设计：针对特定表位设计结合蛋白

**不适用场景**：
- 无明确功能基序的无条件蛋白生成
- 序列设计而非骨架生成任务
- 需要实验验证的最终功能确认

## 上层需求

用户需要从功能位点出发，生成满足以下条件的蛋白骨架：
1. 基序区域原子坐标与输入一致（基序RMSD≤0.6Å）
2. 骨架几何合理（无空间冲突）
3. 可被ProteinMPNN设计为可表达序列
4. 结构可通过AlphaFold2或ESMFold回折叠验证

## 方案概览

本场景采用RFdiffusion作为核心生成模型，配合ProteinMPNN序列设计和PyMOL结构验证。

### 工作流节点

1. **设计目标与约束定义** → `edge:workflow:functional-motif-constrained-backbone-generation`
2. **模型与条件特征准备** → `edge:workflow:functional-motif-constrained-backbone-generation`
3. **候选生成与序列采样** → `edge:workflow:functional-motif-constrained-backbone-generation`
4. **回折叠与设计筛选** → `edge:workflow:functional-motif-constrained-backbone-generation`

### 依赖资源

- **核心模型**：RFdiffusion（Base_ckpt.pt）
- **序列设计**：ProteinMPNN
- **结构验证**：PyMOL（可视化）、AlphaFold2/ESMFold（回折叠）
- **评估指标**：基序RMSD计算脚本

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 输入文件 | motif_5tpn.pdb | 包含功能基序的PDB文件 |
| 模型权重 | Base_ckpt.pt | RFdiffusion基础权重 |
| 目标长度 | 256残基 | 蛋白骨架总长度 |
| 固定残基 | [10, 25] | 基序在骨架中的位置索引 |
| 生成数量 | 64 | 候选结构数量 |
| 采样温度 | 0.2 | 控制采样多样性 |
| 随机种子 | 17 | 可复现性 |
| 筛选阈值 | 0.6Å | 基序RMSD上限 |

## 边界与分流

**硬约束**：
- 基序原子坐标必须与输入PDB完全一致
- 固定残基在生成过程中不得改变
- 骨架几何必须满足拉氏图允许区域

**降级策略**：
- 若基序RMSD>0.6Å，降低温度重试
- 若生成数量不足，扩大采样空间
- 若PyMOL不可用，跳过可视化验证但记录缺失

## 质量检查

1. 输入PDB格式验证（原子完整性、链标识）
2. 固定残基索引在目标长度范围内
3. 基序RMSD≤0.6Å（核心指标）
4. 骨架几何无空间冲突
5. ProteinMPNN序列恢复率>50%

## 回退策略

- 基序RMSD不达标 → 调整温度或增加生成数量
- 序列设计失败 → 检查骨架可设计性
- 回折叠失败 → 降低结构复杂度或缩短长度

## 资源召回建议

当任务涉及以下关键词时应召回本场景卡：
- 功能位点约束、基序支架、酶活性位点、结合蛋白
- RFdiffusion、motif scaffolding、backbone generation
- 基序RMSD、结构验证、序列设计

## 证据来源

[1] Watson JL, et al. De novo design of protein structure and function with RFdiffusion. Nature, 2023, 620:1089-1100. DOI: 10.1038/s41586-023-06415-8
[2] Baek M, et al. Robust deep learning-based protein sequence design using ProteinMPNN. Science, 2023, 380:49-56. DOI: 10.1126/science.add2187
