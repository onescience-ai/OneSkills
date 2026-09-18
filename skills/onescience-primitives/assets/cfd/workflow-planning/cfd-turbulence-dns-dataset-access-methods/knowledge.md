# 公开湍流DNS数据集获取路径与接入方法

## 适用范围
本规范适用于公开湍流DNS数据集的获取与接入，涵盖主要公开数据源（JHTDB、NASA turbulence data repository、Kaggle turbulence datasets等）的API接口、下载协议、数据格式规范。适用于监督学习湍流场超分辨率重建任务中真实DNS数据的获取需求。不适用于合成数据生成或私有数据接入。

## 输入
- 数据访问需求（数据集类型、变量、分辨率、时间步长）
- 访问权限（多数公开数据集需要注册账户）
- 下载工具（Python、Matlab、Fortran、C接口）

## 输出
- 湍流场数据文件（HDF5、Zarr、NetCDF格式）
- 数据元信息（模拟参数、网格分辨率、时间步长、物理量定义）
- 数据访问日志（用于追溯）

## 流程节点

### Step 1：数据源选择与评估
- **操作**：根据任务需求评估不同公开数据源的适用性
- **参数**：数据类型（各向同性湍流、槽道流、边界层等）、雷诺数范围、网格分辨率
- **工具**：文献调研、数据源文档
- **质量门禁**：数据源提供真实DNS数据（非合成数据）

### Step 2：账户注册与权限获取
- **操作**：在目标数据源网站注册账户，获取访问令牌
- **参数**：数据使用协议、访问限制
- **工具**：Web浏览器、API密钥管理
- **质量门禁**：成功获取访问权限

### Step 3：API接口调用与数据下载
- **操作**：使用官方API接口查询并下载数据
- **参数**：时空点查询、变量选择、数据格式
- **工具**：Python API、Matlab接口、数据切片服务
- **质量门禁**：数据下载完整，格式正确

### Step 4：数据验证与格式转换
- **操作**：验证下载数据的完整性、物理量范围、格式兼容性
- **参数**：数据校验和、物理量范围检查
- **工具**：h5py、zarr、numpy
- **质量门禁**：数据可读取，物理量在合理范围内

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据集类型 | 各向同性湍流、槽道流、边界层 | [D1][D2] | 根据任务需求选择 |
| 数据格式 | HDF5、Zarr、NetCDF | [D1] | 现代科学数据格式 |
| 访问接口 | Python、Matlab、Fortran、C | [D1] | 多语言支持 |
| 数据分辨率 | 最高4096^3 | [D1] | 高分辨率湍流数据 |
| 数据大小 | TB级别 | [D1] | 大规模数据集 |

### 校准数值
以下数值来自公开数据源文档，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| JHTDB雷诺数范围 | Reλ = 50-1000 | [D1] | 各向同性湍流数据 |
| JHTDB数据格式 | HDF5、Zarr | [D1] | 支持多种数据格式 |
| NASA数据格式 | NetCDF、HDF5 | [D2] | 翼型绕流DNS数据 |
| Kaggle数据格式 | CSV、Parquet | [D3] | 机器学习友好格式 |

## 边界与分流
- **访问权限不足**：需注册账户并遵守数据使用协议
- **网络带宽限制**：使用数据切片服务获取子集，而非完整数据集
- **存储空间不足**：选择低分辨率数据或部分时间步长
- **数据格式不兼容**：使用HDF5或Zarr库进行格式转换
- **数据源不可用**：尝试备用数据源或联系数据提供者

## 质量检查
- 验证数据文件可正常读取（使用h5py、zarr库）
- 检查数据元信息是否完整（模拟参数、单位、坐标系）
- 确保数据下载完整（校验和验证）
- 验证数据物理量范围合理（速度、压力在预期范围内）
- 确认数据源为真实DNS数据（非合成数据）

## 回退策略
- 若主要数据源访问失败，可尝试备用公开数据源
- 若数据格式不兼容，使用格式转换工具（如h5dump）
- 若下载速度过慢，使用数据子集或降低分辨率
- 若无法获取真实DNS数据，应标注BLOCKED并说明阻塞原因，不应使用合成数据绕过

## 资源召回建议
当任务涉及湍流数据获取、真实数据训练、数据验证时，应召回本卡片。配套资源：`cfd-turbulence-dataset-jhtdb-access`（JHTDB数据访问详情）、`cfd-turbulence-data-contract-specification`（数据契约生成）。

## 补充证据（开源文档/用户自有，可选）
[D1] Johns Hopkins Turbulence Database (JHTDB), Johns Hopkins University, URL: https://turbulence.pha.jhu.edu/（accessed_at: 2026-09-17，权威数据源）
[D2] NASA Turbulence Data Repository, NASA, URL: https://www.nas.nasa.gov/p/science/turbulence.html（accessed_at: 2026-09-17，权威数据源）
[D3] Kaggle Turbulence Datasets, Kaggle, URL: https://www.kaggle.com/datasets（accessed_at: 2026-09-17，社区数据源）

## 证据来源
[1] Li et al., "Johns Hopkins Turbulence Database", Physics of Fluids, 2008
[2] NASA Langley Research Center, "Turbulence Data Repository", NASA Technical Reports, 2020