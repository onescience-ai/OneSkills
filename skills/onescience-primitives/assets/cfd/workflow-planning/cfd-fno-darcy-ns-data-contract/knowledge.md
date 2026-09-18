# Darcy流与Navier-Stokes规则网格数据集标准数据契约

## 适用范围

适用于FNO算子学习任务中Darcy流和Navier-Stokes规则网格数据集的数据接入与契约核验步骤。提供输入输出字段定义、单位约定、网格坐标规范和数据验证规则的标准化模板。不适用于非规则网格数据、实验测量数据（需额外校准）或多物理场耦合数据。

## 输入

### Darcy流数据契约

- **输入字段**：渗透率场 $a(x) \in \mathbb{R}^{H \times W}$（标量场），表示空间分布的扩散系数
- **输出字段**：压力场 $u(x) \in \mathbb{R}^{H \times W}$（标量场）
- **网格坐标**：规则笛卡尔网格，物理域 $[0, 1]^2$（标准配置），分辨率 $241 \times 241$（标准）或 $64 \times 64$（轻量）
- **单位**：SI制无量纲化后值（渗透率和压力均为无量纲量）
- **数据格式**：HDF5文件，包含 `input` (a) 和 `output` (u) 数据集

### Navier-Stokes数据契约

- **输入字段**：初始涡度场 $w_0(x) \in \mathbb{R}^{H \times W}$ 或初始速度场 $(u_0, v_0) \in \mathbb{R}^{H \times W \times 2}$
- **输出字段**：后续时刻的涡度场序列 $w(x,t) \in \mathbb{R}^{H \times W \times T}$ 或速度+压力场序列
- **网格坐标**：规则笛卡尔网格，物理域 $[0, 2\pi]^2$（标准周期域），分辨率 $64 \times 64$（标准）
- **时间离散**：时间步长 $\Delta t$ 需明确记录，总时间 $T$ 需在契约中标注
- **单位**：SI制无量纲化后值（速度、压力、涡度均为无量纲量）
- **数据格式**：HDF5文件，包含 `input` (w0或u0) 和 `output` (w_t或u_t) 数据集

## 输出

### 数据契约Schema（JSON格式）

```json
{
  "dataset_name": "<数据集名称>",
  "domain": "cfd",
  "pde_type": "darcy|navier_stokes",
  "grid": {
    "type": "regular_cartesian",
    "resolution": [H, W],
    "physical_domain": [[x_min, x_max], [y_min, y_max]],
    "coordinate_system": "cartesian",
    "units": "dimensionless"
  },
  "input_fields": [
    {
      "name": "permeability|vorticity|velocity",
      "shape": [H, W] or [H, W, C],
      "dtype": "float32",
      "units": "dimensionless",
      "description": "输入物理量描述"
    }
  ],
  "target_fields": [
    {
      "name": "pressure|vorticity_t|velocity_t",
      "shape": [H, W] or [H, W, T],
      "dtype": "float32",
      "units": "dimensionless",
      "description": "输出物理量描述"
    }
  ],
  "temporal": {
    "is_steady": true|false,
    "dt": null|<时间步长>,
    "T": null|<总时间>,
    "n_steps": null|<时间步数>
  },
  "n_samples": <样本数>,
  "license": "<许可证>",
  "source": "<数据来源>"
}
```

## 流程节点

### 1. 数据文件可读性检查
- **操作**：验证HDF5文件可读，检查所需数据集存在
- **参数**：文件路径、数据集键名
- **质量门禁**：文件可打开，input/output数据集存在且形状匹配

### 2. 字段完整性验证
- **操作**：核验输入输出字段名称、形状、数据类型
- **参数**：契约schema
- **质量门禁**：所有必需字段存在，形状与契约一致

### 3. 单位与坐标系核验
- **操作**：确认物理量单位和坐标系约定
- **参数**：契约中的单位和坐标信息
- **质量门禁**：单位与契约一致，坐标系为笛卡尔

### 4. 样本可追溯性验证
- **操作**：确认每个样本有唯一标识，可追溯到生成参数
- **参数**：样本ID字段
- **质量门禁**：样本ID唯一，无重复

### 5. 训练测试泄漏检查
- **操作**：确认输入参数空间无重叠
- **参数**：输入参数范围
- **质量门禁**：不同集合的输入参数无交集

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据格式 | HDF5 | [1] | 支持高效读写和部分加载 |
| 网格类型 | 规则笛卡尔 | [1] | FNO要求规则网格输入 |
| 单位制度 | 无量纲化 | [1] | 统一跨工况量纲 |
| 数据类型 | float32 | [1] | 平衡精度与内存 |

### 校准数值（体系专属）

| 参数 | Darcy流 | Navier-Stokes | 来源 | 说明 |
|------|---------|---------------|------|------|
| 标准分辨率 | 241×241 | 64×64 | [1][2] | Li et al. 2020使用的标准配置 |
| 物理域 | [0,1]² | [0,2π]² | [1][2] | 标准无量纲化域 |
| 输入通道数 | 1 | 2-3 | [1] | 渗透率/涡度或速度场 |
| 输出通道数 | 1 | 2-3 | [1] | 压力/涡度或速度场 |
| 标准样本数 | 1000 | 1000 | [1] | 训练集标准规模 |

## 边界与分流

**关键前提不成立时的改道方案**：
1. **数据非HDF5格式**：需先转换为HDF5或修改数据加载代码
2. **非笛卡尔网格**：需使用Geo-FNO或GNO等支持非规则网格的方法
3. **多物理场耦合**：需扩展契约以支持多变量输入输出
4. **实验数据**：需额外的校准和不确定性量化步骤

## 质量检查

- 数据文件可读且样本数与契约一致
- 输入输出字段形状、类型与契约匹配
- 网格坐标范围与物理域一致
- 无NaN或Inf值
- 样本ID唯一且可追溯

## 回退策略

- 数据格式不兼容：使用数据转换工具适配
- 分辨率不匹配：使用下采样或上采样预处理
- 单位不一致：执行单位转换和无量纲化

## 资源召回建议

- 本卡片适用于FNO算子学习任务的数据接入与契约核验步骤
- 配套卡片：`cfd-fno-regular-grid-pde-operator-learning-workflow`（完整工作流）
- 配套组件：`datapipes/pdenneval`（PDEBench数据处理）

## 补充证据（开源文档）

[D1] NeuralOperator GitHub Repository, NeuralOperator Team, main branch (2025), URL: https://github.com/neuraloperator/neuraloperator（accessed_at 2026-09-18，官方实现文档，包含数据格式约定）

## 证据来源

[1] Duruisseaux, V., Kossaifi, J., & Anandkumar, A. (2025). Fourier Neural Operators Explained: A Practical Perspective. arXiv:2512.01421.

[2] Li, Z., Kovachki, N., Azizzadenesheli, K., Liu, B., Bhattacharya, K., Stuart, A., & Anandkumar, A. (2020). Fourier Neural Operator for Parametric Partial Differential Equations. arXiv:2010.08895.
