# 蛋白配体对接数据准备任务

## 适用范围

**触发条件**：
- 需要获取蛋白质结构和配体库用于对接
- 需要对原始结构数据进行标准化预处理
- 需要从公开数据库下载 CrossDocked/PDBbind 数据集

**适用场景**：
- 对接任务的 s01（数据预处理）阶段
- 构建自定义对接测试集
- 准备 AI 对接模型的输入数据

**不适用场景**：
- 仅需查询已有数据而不需预处理
- 蛋白质结构预测（AlphaFold 等）

## 输入

- PDB ID 列表或蛋白质结构文件
- 化合物 SMILES 字符串或 SD 文件
- 数据集下载配置（CrossDocked CSV 路径、PDBbind 版本）

## 输出

- 标准化受体 PDB 文件（加氢、质子化、能量最小化）
- 标准化配体 MOL2/SDF 文件（3D 构象、合理质子化状态）
- 数据集 CSV 文件（蛋白-配体对列表）

## 操作步骤

### Step 1：蛋白质结构获取与清理
- 从 RCSB PDB 下载晶体结构
- 移除水分子、辅因子（保留关键辅因子）
- 修复缺失残基和原子
- 添加氢原子，分配质子化状态（pH 7.4）
- 工具：PDBFixer, MGLTools, ChimeraX

### Step 2：配体库准备
- 从 ZINC、ChEMBL 或自定义 SMILES 文件获取配体
- 生成 3D 构象（ETKDG 方法）
- 分配电荷和力场参数
- 质子化状态校正
- 工具：RDKit, Open Babel, Corina

### Step 3：数据集获取与格式化
- 下载 CrossDocked 数据集（crossdocked_test.csv）
- 或下载 PDBbind 数据集（v2020/v2021）
- 格式转换为对接工具所需格式
- 验证蛋白-配体对的配对正确性
- 工具：自定义脚本, Open Babel

### Step 4：质量检查
- 检查受体结构完整性（缺失残基 < 5%）
- 检查配体构象合理性（能量最小化后无立体冲突）
- 验证数据集大小和覆盖率

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 质子化 pH | 7.4 | [1] | 生理 pH 条件 |
| 力场 | AMBER/OPLS/UFF | [1] | 受体/配体力场选择 |
| 构象生成 | ETKDG v3 | [2] | RDKit 默认 3D 构象方法 |
| 缺失残基阈值 | < 5% | [1] | 受体结构质量标准 |
| 数据集版本 | CrossDocked / PDBbind v2020 | [报告] | 常用基准数据集 |

## 质量检查

- 受体 PDB 文件可被 PyMOL/ChimeraX 正常加载
- 配体 SDF 文件包含有效 3D 坐标
- 数据集 CSV 中蛋白-配体对一一对应
- 无重复条目

## 回退策略

- PDB 结构不可用时：使用 AlphaFold 预测结构
- CrossDocked 不可下载时：使用 PDBbind 或 Binding MOAD
- 配体库过大时：按类药性规则过滤（Lipinski's Rule of Five）

## 资源召回建议

- 当需要检索 CrossDocked/PDBbind 资源获取渠道时：召回 `bio-protein-ligand-docking-resource-retrieval`
- 当需要执行对接工作流时：召回 `bio-protein-ligand-docking-workflow`

## 证据来源

[1] Azam F, Almahmoud SA. "Open-Source Molecular Docking and AI-Augmented Structure-Based Drug Design." Int J Mol Sci, 2026, 27(7):3302. DOI: 10.3390/ijms27073302
[2] Yadav A, Murugan NA. "LigGen-a GEN-AI based ligand generation approach for de-novo drug design." Sci Rep, 2026, 16:20477. DOI: 10.1038/s41598-026-48239-2
