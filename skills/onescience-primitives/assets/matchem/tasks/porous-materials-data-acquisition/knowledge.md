# 多孔材料数据获取任务

## 适用范围

当需要从公开数据库获取真实多孔材料（MOF、沸石、多孔碳、COF 等）数据用于基础模型训练或验证时，本卡提供数据库选型、API 接口使用、数据格式转换和质量检查的标准化流程。适用于标注数据为零或极少的冷启动场景。

## 输入

- 目标材料类型（MOF / 沸石 / 多孔碳 / COF / 通用多孔材料）
- 目标性质（吸附容量、带隙、孔径、比表面积、稳定性等）
- 数据量需求（样本数量级）
- 计算资源约束（本地存储、API 速率限制）

## 输出

- 标准化数据集（CSV/JSON/extxyz 格式），含结构信息 + 性质标签
- 数据质量报告（缺失值、重复率、分布统计、异常值检测）
- 数据来源追溯记录（数据库名称、查询条件、下载日期、版本号）

## 流程节点

1. 数据库选型 → API 查询/批量下载 → 数据解析与格式转换 → 数据清洗 → 质量验证 → 存档
   - 每步含操作、参数、工具、质量门禁

## 关键参数

### 通用判据（方法层，同类体系可参考，逐条带证据编号）

| 数据库 | 覆盖范围 | 数据量级 | API/访问方式 | 适用场景 | 来源 |
|--------|---------|---------|-------------|---------|------|
| Materials Project (MP) | 无机晶体材料 | ~15万 | REST API (mp-api) | 通用材料性质 | [1] |
| ICSD | 实验晶体结构 | ~28万 | 付费/API | 实验验证数据 | [2] |
| QMOF | 量子 MOF | ~20万 | GitHub 下载 | MOF 电子结构 | [3] |
| COD | 开放晶体结构 | ~50万 | API/FTP | 通用结构数据 | [2] |
| OQMD | 计算材料 | ~100万 | CSV 批量下载 | 高通量筛选 | [2] |
| CSD (CCDC) | 有机/金属有机 | ~100万 | 付费/API | MOF/COF 结构 | [2] |
| AFLOW | 计算材料 | ~350万 | API/JSON | 高通量计算数据 | [2] |

### 校准数值（体系专属值，引语写明"以下数值来自特定体系，供量级校准；其他体系需以自身证据重新锚定"）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| MP API 每次查询最大条目 | 2000 条 | [1] | 需分页查询 |
| QMOF 数据集大小 | ~20万条 MOF 结构 | [3] | 含 DFT 计算的电子性质 |
| 数据质量最低要求 | 缺失率 <5%，重复率 <1% | [2] | 低于此阈值需人工审查 |

## 边界与分流

- 若目标为实验数据而非计算数据，优先选择 ICSD/CSD 而非 MP/OQMD
- 若需要吸附性质数据，优先选择 CoRE MOF / hMOF 等专项数据库
- 若 API 访问受限（如 ICSD 付费），使用论文 SI 中附带的补充数据作为替代

## 质量检查

- 所有数据条目必须包含：化学式、晶胞参数（a/b/c/alpha/beta/gamma）、原子坐标
- 性质标签必须有明确的计算方法或实验条件标注
- 重复检测：基于化学式 + 空间群 + 晶胞参数去重
- 异常值检测：3σ 准则或 IQR 方法标记潜在异常

## 回退策略

- 若主流数据库 API 不可用，使用论文补充材料中的数据
- 若数据量不足，考虑使用晶体结构生成器（如 USPEX、CALYPSO）扩充

## 资源召回建议

- 当任务需要多孔材料训练数据且未指定数据来源时召回本卡
- 配套资源：基础模型架构卡、GCMC 验证方法卡

## 证据来源

[1] Datta J, et al. "Generative AI for discovering porous oxide materials for next-generation energy storage." Cell Reports Physical Science, 2024, DOI: 10.1016/j.xcrp.2025.102665
[2] Ercakir G, et al. "Hierarchical Computational Screening of Quantum MOF Database." ACS Engineering Au, 2023, DOI: 10.1021/acsengineeringau.3c00039
[3] Zhu R, et al. "Predicting Synthesizability using Machine Learning on Databases of Existing Inorganic Materials." ACS Omega, 2023, DOI: 10.1021/acsomega.2c04856
[4] Scibek J. "Multidisciplinary database of permeability of fault zones." Scientific Data, 2020, DOI: 10.1038/s41597-020-0435-5