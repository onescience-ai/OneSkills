# Materials Project API (MPRester)

## 适用范围
Materials Project API用于查询公开材料数据库中的材料属性数据，包括带隙、形成能、晶体结构、电子结构等。适用于材料筛选、高通量虚拟筛选、机器学习训练数据获取等场景。特别适合需要从公开数据库获取真实材料数据的CO2光催化剂筛选任务。

## 输入
- API密钥（需在Materials Project官网注册获取）
- 查询参数：材料ID、元素组成、属性范围等
- Python环境：需要安装`mp_api`包

## 输出
- 材料属性数据：带隙、形成能、体积、密度、晶体结构等
- 数据格式：Python对象列表，可转换为DataFrame或JSON
- 支持字段筛选：可指定返回特定属性以提高查询效率

## 流程节点
1. **环境准备** → 安装mp_api包，配置API密钥
2. **客户端初始化** → 使用MPRester创建API客户端
3. **数据查询** → 通过search方法查询材料数据
4. **结果处理** → 提取所需属性，进行后续分析

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| band_gap | (0.0, 3.0) | [1] | 光催化剂带隙范围，可见光响应需<3.0 eV |
| elements | ["Ti", "O"] | [2] | 元素组成筛选 |
| material_ids | ["mp-149", "mp-13"] | [D1] | 材料ID查询 |
| fields | ["material_id", "band_gap", "structure"] | [D1] | 指定返回字段 |
| thermo_types | ["GGA_GGA+U"] | [D1] | DFT计算类型筛选 |

## 边界与分流
- API密钥缺失：需注册Materials Project账号获取
- 查询超时：减少查询范围或分批查询
- 数据不完整：某些材料可能缺少特定属性，需检查origins字段
- 计算类型不确定：通过origins和run_type字段确认DFT计算方法

## 质量检查
- 验证返回数据的完整性（所有必需字段是否非空）
- 检查材料属性是否在合理物理范围内
- 与文献数据对比验证（如带隙值是否合理）

## 回退策略
- API不可用时：使用AWS Open Data或本地数据库镜像
- 数据缺失时：使用替代数据源如OQMD、AFLOWLIB
- 查询失败时：简化查询条件或使用分页查询

## 资源召回建议
- 当任务需要真实材料数据时召回此卡片
- 配套使用VASP计算工作流卡片进行DFT验证
- 与机器学习模型卡片结合用于数据驱动筛选

## 证据来源
[1] Scaling deep learning for materials discovery, Nature, 2023, DOI: 10.1038/s41586-023-06735-9
[2] Data-Driven Strategies for Accelerated Materials Design, Accounts of Chemical Research, 2021, DOI: 10.1021/acs.accounts.0c00785
[D1] Materials Project Documentation - Getting Started, Materials Project, 2026, URL: https://docs.materialsproject.org/downloading-data/using-the-api/getting-started.md
[D2] Materials Project Documentation - Querying Data, Materials Project, 2026, URL: https://docs.materialsproject.org/downloading-data/using-the-api/querying-data.md