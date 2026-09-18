# PINN复杂几何边界与无网格配点数据集标准

## 适用范围

面向物理信息神经网络（PINN）在复杂几何边界条件下的训练数据生成与管理，定义标准化数据格式、必需字段、无网格配点生成方法及公开数据源。适用于需要为CFD领域PINN模型准备包含复杂几何边界和配点坐标的训练数据集的场景。

**不适用场景**：
- 简单规则几何（矩形、圆形等标准域）的数据生成
- 传统网格方法（有限元/有限体积）的网格生成
- 非CFD领域的PINN应用（如金融、生物等）

## 输入

- **几何边界描述**：复杂几何的表示文件（STL、网格文件、隐式函数定义）
- **PDE定义**：需要求解的偏微分方程及其边界条件
- **配点参数**：配点数量、分布策略、采样区域

## 输出

- **几何数据文件**：包含几何边界信息的结构化文件
- **配点坐标数据**：包含内部配点和边界配点坐标的文件
- **物理量标签**：对应配点位置的物理量（速度、压力、温度等）
- **数据契约文件**：定义数据格式、单位、变量范围的JSON契约

## 流程节点

### Step 1：几何边界获取与表示

#### 1.1 几何边界表示方法
- **STL格式**：三角面片表示，适用于复杂3D几何
  - 文件格式：ASCII或二进制STL
  - 必需字段：`vertices`（顶点坐标）、`faces`（三角面片索引）
  - 单位：米（默认）或与其他数据保持一致
- **网格文件格式**：Gmsh/OpenFOAM等网格格式
  - 支持格式：`.msh`、`.obj`、`.vtk`、`.cgns`
  - 必需信息：节点坐标、单元连接、边界标记
- **隐式表示**：通过函数定义几何边界
  - 函数签名：`phi(x, y, z) = 0` 定义边界，`phi < 0` 定义内部
  - 适用于参数化几何或几何形状变化频繁的场景

#### 1.2 几何数据验证
- **文件可读性检查**：文件存在、格式正确、可解析
- **几何完整性**：无孔洞、无自相交、边界封闭
- **单位一致性**：几何尺寸与PDE定义的物理尺度匹配

### Step 2：无网格配点生成

#### 2.1 配点类型
- **内部配点**：位于几何内部的点，用于PDE残差计算
- **边界配点**：位于几何边界上的点，用于边界条件施加
- **初始配点**：初始条件定义位置的点（时变问题）

#### 2.2 采样方法
- **均匀采样**：在几何域内均匀分布配点
  - 优点：简单、覆盖均匀
  - 缺点：无法自适应调整密度
- **拉丁超立方采样（LHS）**：分层随机采样
  - 优点：更好的空间填充性
  - 参数：采样点数量 $N$、维度 $d$
- **Halton/Hammersley序列**：低差异序列
  - 优点：均匀性优于纯随机
  - 适用于中等规模问题
- **残差自适应采样**：根据PDE残差调整配点密度
  - 优点：在高残差区域增加配点
  - 参数：残差阈值、采样比例
  - 证据：DeepXDE库实现 `[1]`

#### 2.3 配点生成算法
```python
# 示例：使用DeepXDE生成复杂几何配点
import deepxde as dde

# 定义复杂几何
geom = dde.geometry.CSGPolygon([rect1, rect2, circle], "union")

# 生成内部配点
num_interior = 1000
x interior = geom.sample(num_interior, "uniform")

# 生成边界配点
num_boundary = 200
x boundary = geom.sample(num_boundary, "boundary")

# 残差自适应采样
def residual_sampler(model, geom, num_points):
    # 计算当前残差
    residuals = compute_residual(model, geom)
    # 在高残差区域增加采样
    # ...
```

### Step 3：数据格式标准化

#### 3.1 数据契约定义
```json
{
  "geometry": {
    "format": "STL|mesh|implicit",
    "units": "meters",
    "file_path": "path/to/geometry.stl"
  },
  "collocation": {
    "interior": {
      "num_points": 1000,
      "sampling_method": "uniform|LHS|Halton|adaptive"
    },
    "boundary": {
      "num_points": 200,
      "sampling_method": "uniform|boundary"
    }
  },
  "variables": {
    "position": {"units": "m", "dimensions": ["x", "y", "z"]},
    "velocity": {"units": "m/s", "dimensions": ["u", "v", "w"]},
    "pressure": {"units": "Pa"},
    "temperature": {"units": "K"}
  },
  "boundary_conditions": {
    "type": "Dirichlet|Neumann|Robin|periodic",
    "locations": ["inlet", "outlet", "wall", "symmetry"]
  }
}
```

#### 3.2 必需字段清单
| 数据类型 | 必需字段 | 说明 |
|---------|---------|------|
| 几何数据 | vertices, faces (STL) | 几何边界表示 |
| 内部配点 | x, y, z | 配点坐标 |
| 边界配点 | x, y, z, boundary_id | 配点坐标及边界标识 |
| 物理量 | u, v, w, p, T (根据PDE) | 对应位置的物理量值 |
| 边界条件 | bc_type, bc_value, location | 边界条件类型和值 |

### Step 4：数据质量验证

#### 4.1 几何验证
- **文件可读性**：文件存在、格式正确
- **几何完整性**：无孔洞、边界封闭
- **无自相交**：三角面片无交叉

#### 4.2 配点验证
- **位置有效性**：配点在几何域内（内部配点）或边界上（边界配点）
- **无重复点**：配点坐标不重复
- **覆盖完整性**：几何域被充分覆盖

#### 4.3 物理量验证
- **单位一致性**：所有物理量单位一致
- **数值范围**：物理量在物理合理范围内
- **边界条件符合**：边界配点满足边界条件

## 关键参数

### 通用判据（方法层）

| 参数 | 推荐值 | 来源 | 说明 |
|------|-------|------|------|
| 内部配点数量 | $N_{interior} \propto L^d$ | [通用实践] | 与几何尺寸和维度相关 |
| 边界配点数量 | $N_{boundary} \propto N_{interior}^{(d-1)/d}$ | [通用实践] | 边界点数量随内部点调整 |
| 采样方法选择 | 规则几何→均匀，复杂几何→LHS/自适应 | [通用实践] | 根据几何复杂度选择 |
| 残差自适应阈值 | 残差 > 均值 + 2×标准差 | [DeepXDE文档] | 在高残差区域增加采样 |
| 配点密度比 | 边界:内部 ≈ 1:5 到 1:10 | [CFD领域知识] | 边界配点密度相对较低 |

### 校准数值（特定任务参考）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 典型2D问题内部配点 | 1000-5000 | [DeepXDE示例] | 2D域的典型配点数量 |
| 典型3D问题内部配点 | 5000-20000 | [CFD领域实践] | 3D域的典型配点数量 |
| 边界配点密度 | 100-500 | [CFD领域实践] | 边界上的配点数量 |
| STL文件格式 | ASCII或二进制 | [STL标准] | 支持两种格式 |
| 坐标精度 | float64 | [通用实践] | 双精度浮点数 |

## 边界与分流

### 几何文件不可读
- **前提**：提供的几何文件不存在或格式错误
- **分流**：终止数据生成，返回几何文件错误，提示用户检查文件路径和格式

### 配点生成失败
- **前提**：配点生成算法无法在几何域内找到有效点
- **分流**：尝试替代采样方法，或减少配点数量

### 边界条件定义不完整
- **前提**：边界条件定义缺失或不完整
- **分流**：使用默认边界条件模板，或要求用户补充定义

### 物理量单位不一致
- **前提**：不同物理量的单位不匹配
- **分流**：终止数据验证，返回单位不一致错误

## 质量检查

- **几何文件可读性**：文件存在且格式正确
- **配点位置有效性**：所有配点在几何域内或边界上
- **无重复配点**：配点坐标唯一性
- **物理量单位一致**：所有物理量单位匹配
- **边界条件完整性**：边界条件定义完整
- **数据契约符合**：数据格式符合契约定义

## 回退策略

1. **几何简化**：对于过于复杂的几何，尝试简化表示
2. **降级采样**：使用更简单的采样方法（如均匀采样）
3. **部分配点**：生成部分可用配点，标记无效区域
4. **模板数据**：使用预定义的模板数据集

## 资源召回建议

- 当任务涉及PINN模型训练且需要复杂几何边界数据时，应召回本卡片
- 当需要生成无网格配点数据时，可参考本卡片
- 配套资源：onescience-data-standardizer（数据标准化）、onescience-coder（模型编码）

## 补充证据

### 开源权威文档

[D1] **DeepXDE: A deep learning library for solving differential equations**
- 发布机构：GitHub Repository (lululxvi)
- 版本：master branch
- URL: https://github.com/lululxvi/deepxde
- 访问时间：2026-09-18
- 说明：DeepXDE库提供了复杂几何边界处理的实现，支持CSG布尔操作、点云表示、残差自适应采样等功能

[D2] **DeepXDE Documentation - Complex Domain Geometries**
- 发布机构：ReadTheDocs
- 版本：latest
- URL: https://deepxde.readthedocs.io
- 访问时间：2026-09-18
- 说明：DeepXDE文档详细描述了复杂几何边界处理的方法和API

### 关键实现细节

1. **几何表示**：DeepXDE支持通过CSG（构造性实体几何）使用union、difference、intersection操作构建复杂几何
2. **点云表示**：支持基于点云的几何表示，适用于不规则几何
3. **采样方法**：提供uniform、LHS、Halton、Hammersley、Sobol等多种采样方法
4. **残差自适应采样**：根据PDE残差自适应调整配点密度 `[D1]`

## 证据来源

[1] Liu Y, Chen Y, Liu R, et al. Physics-encoded convolutional neural operators for parametric PDEs: A convergence-guaranteed framework via pre-computed kernel fields. Neural Networks, 2026, 204: 109309. DOI: 10.1016/j.neunet.2026.109309

[2] Vaseem M, Uddin Z, Upreti H. Peristaltic transport and thermodynamic analysis of hybrid nanofluids in porous media using physics-informed neural networks. Discover Nano, 2026, 21(1). DOI: 10.1186/s11671-026-04694-4

[3] Abda M, Berthet L, Hamedi M, et al. The finite element neural network method to simulate two dimensional partial differential equations and perform parameter identification. Scientific Reports, 2026, 16(1). DOI: 10.1038/s41598-026-46707-3

[4] Rotkopf LT, Holzschuh JC, Schlemmer HP, et al. Simulation of spin dephasing in arbitrary susceptibility fields using physics-informed neural networks. Physical Review E, 2025, 112(5-2): 055306. DOI: 10.1103/wdrv-v6pj

[D1] DeepXDE: A deep learning library for solving differential equations. GitHub Repository. https://github.com/lululxvi/deepxde (accessed 2026-09-18)

[D2] DeepXDE Documentation. ReadTheDocs. https://deepxde.readthedocs.io (accessed 2026-09-18)