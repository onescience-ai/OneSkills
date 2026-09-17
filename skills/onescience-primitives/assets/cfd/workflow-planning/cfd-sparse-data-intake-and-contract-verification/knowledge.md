# Sparse Data Intake and Contract Verification

## 适用范围
面向符号与稀疏物理学习控制方程发现任务的数据接入步骤。负责读取稀疏状态轨迹与导数观测数据，核验样本可追溯性、变量单位坐标完整性，输出机器可读的数据契约。适用于任何需要从稀疏采样数据中发现PDE方程的场景。

## 输入
- **数据集路径**（必填）：目录或清单文件，指向稀疏状态轨迹数据。
- **数据集名称**（必填）：来源与数据版本标识。
- **数据契约**（可选）：预期的变量、单位、网格定义。

## 输出
- **dataset_manifest.json**：数据文件清单，含可读性、样本数、变量列表。
- **data_contract.json**：机器可读的变量、单位、坐标系、网格拓扑定义。
- **data_audit.md**：数据审计报告，含缺失值、工况范围、许可信息。

## 流程节点
```
1. 读取{DATASET_PATH}中的{DATASET_NAME}
2. 检查文件可读性
3. 统计样本数、输入与目标变量
4. 核验单位、坐标系、网格拓扑
5. 检查时间或工况范围
6. 扫描缺失值
7. 确认使用许可
8. 按{DATA_CONTRACT}输出机器可读契约
```

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 文件可读性 | 必须通过 | [场景需求书] | 否则BLOCKED |
| 变量单位坐标定义 | 完整性检查 | [场景需求书] | 缺少任一返回BLOCKED |
| 训练测试泄漏 | 不允许 | [场景需求书] | 核验数据无交叉污染 |
| 样本可追溯性 | 必须可追溯 | [场景需求书] | 每个样本有来源标识 |

### 校准数值
> 以下数值来自场景需求书默认配置，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认数据集名称 | 稀疏状态轨迹与导数观测 | [场景需求书] | — |
| 默认坐标系 | dataset_native | [场景需求书] | 数据集原生坐标系 |
| 默认输入字段 | [] | [场景需求书] | 需在实际执行时填入 |
| 默认目标字段 | [] | [场景需求书] | 需在实际执行时填入 |

## 边界与分流
- **缺少必填输入**：返回BLOCKED，列出缺项清单，不得编造数据。
- **数据文件不可读**：报告具体文件路径，返回BLOCKED。
- **单位或坐标缺失**：在data_audit.md中明确标注缺失项，尝试推断或请求补充。
- **数据契约为空**：使用dataset_native坐标系，变量从数据文件头自动检测。

## 质量检查
1. 数据文件可读且样本可追溯（每个样本有来源标识）。
2. 输入目标变量、单位、坐标系定义完整。
3. 不存在训练测试泄漏（数据无交叉污染）。
4. data_contract.json可被标准JSON解析。

## 回退策略
- 文件不可读：检查路径权限和格式支持。
- 变量检测失败：手动指定变量列表。
- 单位缺失：从数据源文档或论文补充，或标记为unknown。

## 资源召回建议
- 当需要为符号/稀疏方程发现任务接入数据时召回。
- 配套卡片：cfd-symbolic-sparse-governing-equation-discovery（场景级）、cfd-symbolic-sparse-equation-discovery-workflow（工作流级）。

## 证据来源
[1] 场景需求书 CFD_S045 s01定义
[2] Physics informed deep learning (Part II): Data-driven discovery of nonlinear partial differential equations, 2017
[3] Learning fluid physics from highly turbulent data using sparse physics-informed discovery of empirical relations, 2024
