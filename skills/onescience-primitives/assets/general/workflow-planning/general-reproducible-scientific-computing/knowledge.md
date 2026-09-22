# 可复现科学研究计算规范

## 适用范围
本卡片规范科学研究计算任务的可复现性、可审计性和科学严谨性标准，适用于任何领域（材料科学、生物信息、气候、CFD等）的科研任务执行。任务要求"完成一项可复现、可审计的研究任务"时必须遵循本规范。

## 输入
- 研究目标：明确的研究问题和假设
- 数据来源：公开数据库、实验数据或模拟数据
- 计算环境：软件版本、依赖库、硬件配置

## 输出
- 可复现的研究成果：代码、数据、环境配置
- 可审计的决策记录：每步决策的依据和证据
- 科学严谨的验证结果：与独立数据源的对比

## 流程节点

### 1. 数据管理
- **操作**：按FAIR原则管理研究数据
- **参数**：数据元数据、版本控制、访问策略
- **工具**：Git、DVC、Zenodo
- **质量门禁**：数据可查找、可访问、可互操作、可重用

### 2. 代码管理
- **操作**：使用版本控制管理代码
- **参数**：代码仓库、提交记录、分支策略
- **工具**：Git、GitHub/GitLab
- **质量门禁**：代码可追溯、可审查

### 3. 环境管理
- **操作**：记录计算环境配置
- **参数**：软件版本、依赖库、容器配置
- **工具**：Docker、Conda、requirements.txt
- **质量门禁**：环境可重复配置

### 4. 决策记录
- **操作**：记录每步决策的依据和证据
- **参数**：决策日志、参数选择理由、备选方案
- **工具**：Markdown日志、Jupyter Notebook
- **质量门禁**：决策可追溯、可解释

## 关键参数

### 通用判据（方法层）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| FAIR原则 | Findable, Accessible, Interoperable, Reusable | [1] | 数据管理标准 |
| 版本控制 | Git + 语义版本号 | [2] | 代码和数据版本管理 |
| 环境记录 | Docker + Conda | [2] | 计算环境可重复 |
| 决策日志 | 结构化Markdown | [2] | 决策可追溯 |
| 数据验证 | 独立数据源对比 | [1] | 结果可验证 |

### 校准数值（多孔材料体系）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据格式 | CIF + JSON | [1] | 标准材料数据格式 |
| 代码仓库 | GitHub公开仓库 | [2] | 代码可访问 |
| 环境配置 | Docker镜像 + Conda环境 | [2] | 环境可重复 |
| 验证数据 | Materials Project + 实验文献 | [1] | 独立验证来源 |

## 边界与分流
- **缺少实验数据**：使用高保真计算作为替代验证，但需明确标注
- **计算资源限制**：记录资源约束和简化决策，提供完整版本的执行路径
- **数据敏感性**：使用分布式研究系统或合成数据替代

## 质量检查
- **可复现性**：他人可使用提供的代码、数据和环境重复研究
- **可审计性**：每步决策有明确依据和证据
- **科学严谨性**：使用独立数据源验证结果

## 回退策略
- 若无法满足可复现性要求，可尝试：(1) 提供详细执行说明；(2) 使用在线笔记本（如Binder）；(3) 报告局限性

## 资源召回建议
- 当任务要求"可复现、可审计的研究任务"时召回本卡片
- 配套资源：具体领域技能（如onescience-trainer、onescience-data-analyzer）

## 证据来源
[1] Scalable Infrastructure Supporting Reproducible Nationwide Healthcare Data Analysis toward FAIR Stewardship, Scientific Data, 2023, DOI: 10.1038/s41597-023-02580-7
[2] Reproducible research policies and software/data management in scientific computing journals, Frontiers in Computer Science, 2025, DOI: 10.3389/fcomp.2024.1491823
[3] Reproducible Research Publication Workflow: A Canonical Workflow Framework and FAIR Digital Object Approach, Data Intelligence, 2022, DOI: 10.1162/dint_a_00133