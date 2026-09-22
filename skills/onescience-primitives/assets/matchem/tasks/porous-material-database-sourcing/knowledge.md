# Porous Material Database Sourcing

## 适用范围
面向多孔材料（MOF、沸石、多孔碳、多孔有机骨架等）的数据获取任务，覆盖从公开数据库检索、下载、格式转换到质量验证的完整流程。适用于需要真实多孔材料结构信息和性质数据的科研任务；不适用于纯实验数据采集或私有数据库接入。

## 输入
- 目标材料类型（MOF/沸石/多孔碳等）
- 所需数据字段（结构信息、吸附性质、力学性质等）
- 数据量需求（筛选规模、训练数据量）
- 质量要求（实验验证/计算验证、数据完整性）

## 输出
- 标准化的材料数据集（CIF文件、结构数据、性质标签）
- 数据质量报告（缺失值、异常值、重复项统计）
- 数据溯源信息（来源数据库、下载日期、版本号）

## 流程节点
1. **数据库选择** → 根据材料类型和数据需求选择合适的数据库
2. **数据检索** → 使用API或批量下载获取数据
3. **格式标准化** → 统一CIF格式、单位、坐标系
4. **质量检查** → 验证结构合理性、去除重复、检查缺失
5. **数据注册** → 记录来源、版本、访问时间等元数据

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Materials Project API | materialsproject.org | [1] | 通过mp-api获取MP数据库，需API key |
| CoRE MOF 2025 | ~5800结构 | [3] | 实验验证MOF数据库，包含推荐筛选列表 |
| CSD MOF Database | >10万MOF | [1] | 剑桥结构数据库MOF子集，PoreBlazer v4.0兼容 |
| QMOF Database | >20万MOF | [1] | 量子化学计算MOF数据库 |
| hMOF Database | ~13万MOF | [1] | 高通量计算生成MOF数据库 |
| ICSD | >28万无机结构 | [1] | 无机晶体结构数据库，实验测定结构 |
| PrISMa Database | >800 MOF | [3] | 含GCMC吸附等温线的MOF数据库 |
| 数据格式 | CIF/VASP/POSCAR | [1] | 晶体信息文件标准格式 |
| 结构验证 | >99%合理 | [1] | 原子间距、键长应在合理范围 |

## 边界与分流
- **MOF数据**：优先选择CoRE MOF 2025（实验验证）或QMOF（量子化学验证）
- **沸石数据**：优先选择IZA数据库或Materials Project中的沸石结构
- **多孔碳数据**：选择专门的多孔碳数据库或从实验文献提取
- **需要吸附性质**：选择PrISMa数据库（含GCMC等温线）或自行模拟
- **数据量不足**：考虑使用数据增强（如结构扰动）或迁移学习
- **私有数据**：仅在用户显式提供时使用，需脱敏扫描

## 质量检查
- 数据来源可追溯：每个样本应有明确的数据库来源和版本
- 结构合理性：原子坐标、键长、晶胞参数应在物理合理范围
- 无重复：去除完全相同的结构（基于ICSD编号或结构指纹）
- 缺失值处理：关键字段（如吸附容量）缺失率应<5%
- 格式一致性：所有CIF文件应遵循统一标准

## 回退策略
- 如果目标数据库不可访问：使用备选数据库（如从Materials Project获取类似结构）
- 如果数据格式不兼容：使用pymatgen或ASE进行格式转换
- 如果数据质量不达标：进行数据清洗或标注为低质量数据

## 资源召回建议
- 需要召回本卡片的场景：用户提到"数据获取""数据库""Materials Project""MOF数据""ICSD"等关键词
- 配套资源：matchem/tasks/porous-material-gnn-foundation-model-selection（模型选择）、matchem/tasks/porous-material-model-validation-gcmc（验证方法）

## 证据来源
[1] Colón YJ, et al. "Materials Informatics with PoreBlazer v4.0 and the CSD MOF Database." Chemistry of Materials, 2020, 32(20): 8682-8692. DOI: 10.1021/acs.chemmater.0c03575
[2] Smit B, et al. "A Database of Porous Rigid Amorphous Materials." Chemistry of Materials, 2020, 32(21): 9389-9400. DOI: 10.1021/acs.chemmater.0c03057
[3] Schnieders MJ, et al. "Fast process-level screening of metal-organic frameworks for adsorption-based gas separation." Digital Discovery, 2025. DOI: 10.1039/d6me00066e
[4] MOF benchmark authors. "Benchmark Maturity in MOF Adsorption Machine Learning." Digital Discovery, 2026. DOI: 10.1039/d6dd00123a
[5] Screening porous materials authors. "Breakthrough Screening of Porous Materials." Applied Surface Science, 2020. DOI: 10.1016/j.apsusc.2020.146115
