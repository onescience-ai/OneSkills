# 材料结构文件格式与电池工况参数获取

## 适用范围

面向电池电极材料结构设计任务，当工作流需要用户提供材料结构文件（如CIF、POSCAR）或电池工况参数（电压窗口、温度、倍率）时，本卡片提供标准格式规范、公开数据库获取途径、以及必填输入缺失时的决策规则。适用于锂离子电池、钠离子电池、镁离子电池等二次电池的负极/正极材料设计场景。

## 输入

用户提供的材料结构文件或数据库检索参数：
- CIF文件（Crystallographic Information File）：晶体结构标准格式
- POSCAR文件：VASP计算输入格式
- 材料化学式或数据库ID（如Materials Project ID、ICSD编号）

## 输出

标准化的材料结构文件和工况参数配置，可直接用于后续计算模拟或实验设计。

## 流程节点

1. **需求识别** → 确定任务所需的材料结构类型（块体/纳米/界面）和精度要求
2. **数据库检索** → 从公开数据库获取材料结构文件
3. **格式转换** → 将获取的结构文件转换为目标计算工具的输入格式
4. **工况参数定义** → 确定电压窗口、温度、倍率等电池运行条件
5. **输入完整性检查** → 验证所有必填输入是否齐全，缺失时触发用户交互或BLOCKED标记

## 关键参数

| 参数 | 值/范围 | 来源 | 说明 |
|------|---------|------|------|
| CIF格式 | IUCr标准 | [1] | 包含晶体对称性、原子坐标、温度因子 |
| POSCAR格式 | VASP标准 | [2] | 包含晶格矢量、原子位置、选择性动力学 |
| ICSD数据库 | https://icsd.products.fiz-karlsruhe.de | [1] | 无机晶体结构数据库，收录>28万条记录 |
| Materials Project | https://materialsproject.org | [2] | 计算材料数据库，提供DFT优化结构 |
| OQMD | https://oqmd.org | [2] | 开放量子材料数据库 |
| 电压窗口 | 0.01-2.0 V vs. Li/Li+ | [3] | 硅负极典型测试范围 |
| 测试温度 | 25°C (298 K) | [3] | 标准电化学测试温度 |
| 电流密度 | 400 mA/g | [3] | 多孔硅负极测试条件 |

## 边界与分流

- **用户未提供材料结构文件**：应主动向用户请求补充，而非使用默认值或文献数据替代。缺失时标记BLOCKED状态。
- **数据库中无目标材料结构**：建议用户提供实验测定的CIF文件，或使用第一性原理结构弛豫生成初始结构。
- **工况参数不完整**：电压窗口为必填项；温度和倍率可使用默认值（25°C, 0.1C），但需在报告中注明。

## 质量检查

- 验证CIF文件语法正确性（使用PLATON或checkCIF工具）
- 验证POSCAR文件格式完整性（检查晶格常数、原子数、坐标范围）
- 确认材料结构与目标体系一致（化学式、空间群、晶格参数）

## 回退策略

- 数据库检索失败时，可使用用户提供的实验XRD数据进行Rietveld精修获取结构
- 格式转换失败时，使用ASE（Atomic Simulation Environment）等通用工具进行转换

## 资源召回建议

- 当任务涉及电池电极材料设计时召回本卡片
- 配套卡片：matchem-electrochemical-simulation-tool-selection、matchem-data-driven-design-optimization

## 证据来源

[1] He B, et al. CAVD, towards better characterization of void space for ionic transport analysis. Scientific Data, 2020, 7:153. DOI: 10.1038/s41597-020-0491-x
[2] Franco AA, et al. Boosting Rechargeable Batteries R&D by Multiscale Modeling: Myth or Reality? Chemical Reviews, 2019, 119:4569-4627. DOI: 10.1021/acs.chemrev.8b00239
[3] Shen C, et al. In Situ and Ex Situ TEM Study of Lithiation Behaviours of Porous Silicon Nanostructures. Scientific Reports, 2016, 6:31334. DOI: 10.1038/srep31334
