# 蛋白配体对接资源检索任务

## 适用范围

**触发条件**：
- 需要获取 CrossDocked 数据集用于对接基准测试
- 需要获取 PDBbind 数据集用于打分函数训练/评估
- 需要获取 DeltaDock 或其他 AI 对接模型的权重文件
- 使用通用搜索引擎未找到专业资源时

**适用场景**：
- 对接任务中数据和模型权重的获取
- 专业生物信息学资源库的定向检索
- 资源获取失败时的回退策略规划

**不适用场景**：
- 仅需查询资源是否存在（不涉及下载）
- 资源已在本地可用时

## 输入

- 目标资源名称（如 CrossDocked、PDBbind、DeltaDock）
- 资源类型（数据集/模型权重/代码仓库）
- 任务需求描述

## 输出

- 资源的官方 URL 和访问方式
- 许可证信息
- 下载命令或脚本
- 资源完整性验证方法

## 操作步骤

### Step 1：专业平台定向检索
- **优先级 1：论文附属仓库**（GitHub/GitLab）
  - 查找论文中的 Code/Data Availability 部分
  - 检查论文 supplementary materials
- **优先级 2：专业数据平台**
  - PDBbind: http://www.pdbbind.org.cn/
  - CrossDocked: 通过论文作者或 GitHub 仓库
  - Zenodo: https://zenodo.org/（通用学术数据存储）
  - ModelScope: https://modelscope.cn/（AI 模型平台）
- **优先级 3：模型发布平台**
  - HuggingFace Models: https://huggingface.co/models
  - PyTorch Hub: https://pytorch.org/hub/
  - TIMM: https://github.com/rwightman/pytorch-image-models

### Step 2：资源获取渠道映射

#### CrossDocked 数据集
- **来源**：论文 "Comprehensive Dataset of Affinity Predicted Data for Protein-Ligand Pairs" (2020)
- **获取**：通过 GitHub 仓库或联系论文作者
- **格式**：CSV 文件（crossdocked_test.csv）+ 对接构象文件
- **许可证**：通常为 CC-BY-4.0 或学术使用许可

#### PDBbind 数据集
- **来源**：PDBbind 数据库（http://www.pdbbind.org.cn/）
- **获取**：注册后下载（需学术邮箱）
- **版本**：v2020（推荐）、v2021
- **格式**：PDB 文件 + 结合亲和力数据
- **许可证**：学术免费使用

#### DeltaDock 模型权重
- **来源**：论文 "DeltaDock: Fast and Accurate Protein-Ligand Docking with Delta Learning"
- **获取**：通过论文 GitHub 仓库或 Zenodo
- **格式**：PyTorch checkpoint (.pt 文件)
- **许可证**：MIT 或 Apache 2.0（需确认）

#### AutoDock Vina
- **来源**：Scripps Research Institute
- **获取**：https://vina.scripps.edu/ 或 conda 安装
- **格式**：可执行文件或 Python 包
- **许可证**：Apache 2.0

#### GNINA
- **来源**：GitHub 仓库 https://github.com/GNINA/gnina
- **获取**：conda install -c conda-forge gnina
- **格式**：可执行文件
- **许可证**：Apache 2.0

### Step 3：资源验证
- 验证 URL 可访问性
- 检查文件哈希（如提供）
- 确认许可证兼容性
- 小规模测试下载

### Step 4：回退策略
- 官方渠道不可用时：查找镜像或替代平台
- 学术邮箱不可用时：使用机构 VPN 或联系合作者
- 模型权重不可用时：使用经典工具（AutoDock Vina）替代

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| CrossDocked | GitHub/论文作者仓库 | [报告] | 需要追踪论文来源 |
| PDBbind | http://www.pdbbind.org.cn/ | [3] | 需学术邮箱注册 |
| DeltaDock | GitHub/Zenodo | [报告] | 需确认官方发布 |
| AutoDock Vina | https://vina.scripps.edu/ | [1] | 开源免费 |
| GNINA | conda-forge | [3] | 开源免费 |
| Zenodo | https://zenodo.org/ | [1] | 通用学术存储 |

## 边界与分流

- **通用搜索失败时**：不要继续用 Google/GitHub 搜索，直接转向专业平台
- **资源不存在时**：如实标记 BLOCKED 并提出最小补充方案（替代数据集/工具）
- **许可证不兼容时**：寻找替代资源或申请学术许可
- **下载速度慢时**：使用镜像站点或学术机构网络

## 质量检查

- URL 可访问（HTTP 200）
- 文件大小与预期一致
- 许可证明确且兼容
- 小规模测试通过

## 回退策略

- CrossDocked 不可用：使用 PDBbind 或 Binding MOAD 构建测试集
- DeltaDock 权重不可用：使用 AutoDock Vina 或 GNINA 替代
- PDBbind 需要注册：使用 PDB 直接下载结构 + 自行构建亲和力数据

## 资源召回建议

- 当需要执行数据准备时：召回 `bio-protein-ligand-docking-data-preparation`
- 当需要执行对接工作流时：召回 `bio-protein-ligand-docking-workflow`

## 证据来源

[1] Azam F, Almahmoud SA. "Open-Source Molecular Docking and AI-Augmented Structure-Based Drug Design." Int J Mol Sci, 2026, 27(7):3302. DOI: 10.3390/ijms27073302
[2] Suri K, et al. "Cross-docking and redocking reveal distinct determinants of success." RSC Adv, 2026. DOI: 10.1039/d6ra05440d
[3] Gaskin L, et al. "Enhanced Line Search Improves Robustness and Efficiency of Pose Sampling in Protein-Ligand Docking." J Chem Theory Comput, 2026, 22(17):9188-9198. DOI: 10.1021/acs.jctc.6c01110
