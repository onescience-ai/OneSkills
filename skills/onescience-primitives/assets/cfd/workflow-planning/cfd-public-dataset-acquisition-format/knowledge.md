# CFD公开基准数据集获取路径与格式规范

## 适用范围

**触发条件**：
- 需要获取公开CFD基准数据集进行方法演示和验证
- 需要了解公开CFD数据库的访问方式、下载接口和数据格式
- 需要定义数据契约模板确保数据符合场景标准

**适用场景**：
- CFD缺失区补全与压缩任务的数据准备阶段
- 生成模型训练数据采集（无用户自有数据时）
- 方法验证与基准测试数据获取

**不适用场景**：
- 使用用户自有CFD仿真数据
- 仅需几何坐标而无需流场数据的场景
- 数据规模要求极高的生产级训练

## 输入

- 数据获取目标：几何类型（翼型、圆柱等）、工况范围、精度要求
- 数据格式要求：结构化程度、单位标准、坐标系约定
- 数据规模目标：样本数量、工况点数量

## 输出

- 公开CFD数据集访问路径和下载接口
- 数据格式规范（NetCDF/HDF5/CSV/JSON）
- 数据契约模板（变量名、单位、坐标系）
- 数据质量检查清单

## 流程节点

### Step 1：公开数据源识别
- **操作**：识别权威公开CFD数据源（NASA、UIUC、GitHub等）
- **参数**：数据源URL、维护机构、更新频率
- **工具**：文献检索、权威文档查询
- **质量门禁**：确认数据源权威性（.edu/.gov/.org域名或知名机构维护）

### Step 2：数据访问与下载
- **操作**：通过API或直接下载获取数据
- **参数**：下载接口、认证要求、文件格式
- **工具**：wget/curl/Python requests
- **质量门禁**：数据文件完整可读，无损坏

### Step 3：数据格式解析
- **操作**：解析不同格式的CFD数据（NetCDF/HDF5/CSV/JSON）
- **参数**：文件编码、变量命名、维度结构
- **工具**：Python科学计算库（xarray/pandas/h5py）
- **质量门禁**：数据可解析，变量名符合物理意义

### Step 4：数据契约生成
- **操作**：基于数据元信息生成数据契约模板
- **参数**：变量映射、单位转换、坐标系定义
- **工具**：JSON模板生成
- **质量门禁**：契约包含所有必要字段，单位符合SI制

### Step 5：数据规模验证
- **操作**：检查数据规模是否满足训练要求
- **参数**：最小样本数、工况覆盖范围
- **工具**：Python统计脚本
- **质量门禁**：规模指标达到阈值，数据分布合理

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 最小样本数量 | ≥1000 | [归因报告] | 生成模型学习的基本需求 |
| 数据格式兼容性 | NetCDF/HDF5/CSV | [领域知识] | 支持常用科学计算库 |
| 单位标准 | SI制 | [场景标准] | 统一物理量单位 |
| 坐标系 | 笛卡尔坐标 | [场景标准] | 标准空间参考 |
| 数据许可 | 允许学术使用 | [领域知识] | 确保合规性 |

### 校准数值（以下数值来自公开CFD数据集，供量级校准；其他体系需以自身证据重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| UIUC翼型数量 | 约1600+ | [UIUC] | 最大公开翼型坐标库 |
| NASA湍流模型工况 | 约100+标准案例 | [NASA] | 高保真CFD验证数据 |
| 圆柱网格数据集规模 | 20,480个网格 | [论文1] | 三维圆柱网格基准数据集 |
| 典型雷诺数范围 | 1×10⁵ ~ 1×10⁷ | [领域知识] | 覆盖低速到高速流动 |

## 边界与分流

- **数据源访问受限**：转向其他公开数据库（如airfoiltools.com、GitHub仓库）
- **数据格式不兼容**：使用格式转换工具（xarray、pandas）统一数据结构
- **数据规模不足**：使用数据增强（几何扰动、工况插值）或迁移学习策略
- **流场数据缺失**：仅使用几何-性能数据训练几何生成模型
- **单位不一致**：强制转换为SI制，保留原始单位作为参考

## 质量检查

- 数据源权威性验证（.edu/.gov/.org域名）
- 数据完整性检查（无缺失字段、无异常值）
- 数据格式兼容性验证（可被常用库读取）
- 数据规模达到最小阈值
- 数据许可允许学术使用

## 回退策略

- 公开数据源不可用：使用文献中的数据表格手动整理
- 数据规模严重不足：使用合成数据补充（参数化几何+简化物理模型）
- 数据格式复杂：使用专用CFD后处理工具解析
- 无合适数据源：基于场景标准生成模拟数据用于方法验证

## 资源召回建议

- 当需要获取公开CFD数据集进行方法演示时召回本卡片
- 配套资源：cfd-airfoil-dataset-acquisition-format（翼型专用）、cfd-dataset-validation-checklist（数据验证）
- 若涉及多保真数据融合，可关联 cfd-multifidelity-airfoil-optimization-workflow
- 若涉及数据契约定义，可关联 cfd-airfoil-data-intake-contract-validation

## 补充证据（权威文档）

[D1] UIUC Airfoil Data Site, University of Illinois at Urbana-Champaign, URL: https://m-selig.ae.illinois.edu/ads/coord_database.html（权威学术机构维护的翼型坐标数据库）
[D2] NASA Turbulence Modeling Resource, NASA Langley Research Center, URL: https://turbmodels.larc.nasa.gov/（NASA官方湍流模型验证数据）
[D3] 3D Cylinder Mesh Benchmark Dataset, GitHub, URL: https://github.com/MeshDataset/3D-Cylinder（圆柱网格基准数据集，包含20,480个网格）

## 证据来源

[1] Chen et al., "A Neural Network-Based Mesh Quality Indicator for Three-Dimensional Cylinder Modelling", Entropy, 2022, DOI: 10.3390/e24091245
[2] Zhang et al., "Computational Fluid Dynamics (CFD) applications in Floating Offshore Wind Turbine (FOWT) dynamics: A review", Applied Ocean Research, 2024, DOI: 10.1016/j.apor.2024.104075
[3] 归因报告 CFD_S100：隐式表示与扩散桥CFD缺失区补全压缩任务分析