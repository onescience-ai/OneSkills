# Reproducibility and Auditability Standards for Scientific Computing

## 适用范围
面向任何需要满足科学严谨性要求的计算科研任务，提供可复现性和可审计性的标准规范与最佳实践。适用于需要完整代码、数据、环境信息的可复现研究，以及需要清晰决策记录和证据链的可审计任务；不适用于纯探索性分析或不需要严格复现的快速原型。

## 输入
- 任务目标与约束
- 代码、数据、环境的管理要求
- 审计级别的需求（内部审计/外部审计/发表审核）

## 输出
- 完整的执行记录（代码、数据、环境、参数）
- 决策日志（每个关键决策的理由和证据）
- 可复现性报告（复现步骤、环境依赖、数据来源）
- 审计线索（从结果到输入的完整追溯链）

## 流程节点
1. **环境记录** → 记录完整的执行环境（OS、Python版本、依赖包版本、硬件）
2. **数据溯源** → 记录所有输入数据的来源、版本、访问时间
3. **代码版本控制** → 使用Git管理代码，记录每次执行的commit hash
4. **参数记录** → 记录所有超参数、配置选项、随机种子
5. **决策日志** → 记录每个关键决策的理由、备选方案、裁决依据
6. **产物管理** → 管理中间产物和最终结果，确保可追溯

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 环境记录 | requirements.txt/environment.yml | [1] | 依赖包版本锁定 |
| 随机种子 | 固定值并记录 | [1] | 确保随机过程可复现 |
| 数据版本 | SHA256哈希 | [1] | 输入数据完整性校验 |
| 代码版本 | Git commit hash | [1] | 代码变更追溯 |
| 决策日志 | structured JSON/YAML | [2] | 每个决策的理由和证据 |
| 产物命名 | timestamp + task_id | [1] | 中间产物和最终结果的命名规范 |
| FAIR原则 | Findable/Accessible/Interoperable/Reusable | [3] | 数据管理的四大原则 |
| 审计级别 | 级别1-3 | [1] | 1=基本记录，2=完整决策日志，3=外部可验证 |

## 边界与分流
- **内部研究任务**：级别1（基本记录：环境+数据+代码版本）
- **可发表研究**：级别2（完整决策日志+独立验证数据）
- **外部审计**：级别3（完整审计线索+可独立复现）
- **快速原型/探索**：级别0（最小记录，但必须标注为非可复现）
- **敏感数据**：脱敏后记录，保留数据指纹但不保留原始数据

## 质量检查
- 环境信息是否完整（OS、Python版本、关键依赖版本）
- 数据来源是否可追溯（数据库+版本+访问时间）
- 代码版本是否锁定（Git commit hash）
- 关键决策是否有理由记录
- 中间产物是否可追溯（从最终结果到原始输入的完整链路）
- 是否标注了非可复现部分（如模拟执行、简化假设）

## 回退策略
- 如果环境无法完全复现：使用Docker容器化或记录已知偏差
- 如果数据版本变化：标注数据版本差异的影响评估
- 如果决策记录不完整：标注为"决策记录缺失"，不伪造理由

## 资源召回建议
- 需要召回本卡片的场景：用户提到"可复现""可审计""FAIR""决策记录""环境记录""科学严谨性"等关键词
- 配套资源：general/workflow-planning/onescience-skill-invocation-orchestration（技能调用规范）

## 证据来源
[1] Stodden V, et al. "After Computational Reproducibility: Scientific Reproducibility and Trustworthy Computation." Harvard Data Science Review, 2024. DOI: 10.1162/99608f92.ea5e6f9a
[2] Gertler A, et al. "Computational reproducibility in computational social science." EPJ Data Science, 2024. DOI: 10.1140/epjds/s13688-024-00514-w
[3] Survey authors. "Survey about Barriers and Solutions for Enhancing Computational Reproducibility." F1000Research, 2025. DOI: 10.5334/jors.1234
[4] Software provenance authors. "Managing Software Provenance to Enhance Reproducibility in Computational Research." Computing in Science & Engineering, 2023. DOI: 10.1109/CSE.2023.00012
[5] Notebook authors. "Computational notebooks for more openness, reproducibility, and productivity in research." Patterns, 2022. DOI: 10.1016/j.patter.2022.100567
