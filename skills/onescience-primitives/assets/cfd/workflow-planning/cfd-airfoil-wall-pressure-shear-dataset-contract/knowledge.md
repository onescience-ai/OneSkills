# 翼型壁面压力剪切数据集规范

## 适用范围

面向翼型壁面压力剪切与积分气动力联合反演任务，提供壁面压力系数、剪切应力、速度场数据的标准格式规范、数据契约要求及权威获取路径。适用于CFD反演任务中数据接入与契约核验步骤，支持数据格式校验、缺失数据降级策略与替代数据源评估。

## 输入

### 数据源类型
- **实验测量数据**：风洞实验获取的翼型壁面压力分布、油膜干涉测量的剪切应力
- **高保真仿真数据**：DNS/LES计算的壁面压力与剪切应力分布
- **公开数据集**：NASA Turbulence Modeling Resource、Airfoil Preprocessing Toolkit等权威来源

### 数据格式要求
- **结构化网格格式**：HDF5、NetCDF或结构化CSV
- **点云格式**：适用于非结构化网格的XYZ坐标+场变量格式
- **单位规范**：压力单位Pa，剪切应力单位Pa，速度单位m/s，坐标单位m

## 输出

### 标准数据契约
```
{
  "dataset_id": "string",
  "geometry": "airfoil_type/chord_length/angle_of_attack",
  "variables": {
    "pressure_coefficient": "Cp (dimensionless)",
    "wall_shear_stress": "tau_w (Pa)",
    "velocity_field": "u,v,w (m/s)",
    "reynolds_stress": "u'u',v'v',w'w' (m²/s²)"
  },
  "mesh_info": "grid_type/cell_count/quality_metrics",
  "boundary_conditions": "Reynolds_number/Mach_number/turbulence_model",
  "data_source": "experimental/synthetic/CFD_reference",
  "validation_status": "verified/unverified/synthetic_warning"
}
```

### 验证标准
- Cp分布应符合翼型理论（前缘峰值、压力恢复）
- 剪切应力分布应与边界层理论一致（层流→湍流转捩特征）
- 数据完整性检查：无NaN值，变量范围合理

## 流程节点

```
数据源识别 → 格式解析 → 契约校验 → 物理合理性检查 → 降级决策
    ↓              ↓              ↓              ↓              ↓
权威数据源    结构化解析    字段完整性    物理约束校验    合成数据标记
    ↓              ↓              ↓              ↓              ↓
ModelScope     HDF5/CSV      命名规范      Cp峰值检查    synthetic=True
NASA/AFDB      点云解析      单位一致      剪切应力范围   fallback_warning
```

### 步骤1：数据源识别
- 优先级：ModelScope官方数据集 > NASA/AFDB权威库 > 用户提供 > 合成数据
- 合成数据必须标注`"data_source": "synthetic"`并附警告

### 步骤2：格式解析
- 检查文件格式（HDF5/CSV/NetCDF）
- 验证坐标系（笛卡尔/极坐标）
- 确认变量命名规范

### 步骤3：契约校验
- 必填字段检查：geometry、variables、mesh_info、boundary_conditions
- 单位一致性验证
- 数据范围合理性检查

### 步骤4：物理合理性检查
- Cp分布：前缘应有明显峰值，压力恢复区应平滑
- 剪切应力：层流区低值，湍流区高值，转捩点应有突变
- Reynolds应力：近壁面应有峰值

### 步骤5：降级决策
- 数据缺失时的处理策略：
  - 仅缺少剪切应力：可用边界层理论估算
  - 仅缺少速度场：可用压力数据反推
  - 数据完全缺失：使用合成数据并标注`synthetic_warning`

## 关键参数

### 通用判据（方法层）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 压力系数范围 | -2.0 ≤ Cp ≤ 1.0 | 翼型理论 | 超出范围需检查数据质量 |
| 剪切应力数量级 | 0.01-10 Pa | 典型风洞实验 | 取决于Reynolds数 |
| 网格分辨率 | ≥100点/弦长 | 工程精度要求 | 近壁面需加密 |
| 数据完整性 | 无NaN/Inf | 基本质量要求 | 缺失值需插值或标记 |

### 校准数值（翼型实验典型值）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| NACA 0012 Cp前缘峰值 | -1.5 ~ -2.0 | NASA TM 2006 | 零升力状态 |
| NACA 0012 Cp后缘值 | 0.3 ~ 0.5 | NASA TM 2006 | 尾迹恢复 |
| 层流边界层厚度 | 0.5-2mm | 实验测量 | Re=10⁶量级 |
| 湍流边界层厚度 | 5-20mm | 实验测量 | Re=10⁶量级 |

## 边界与分流

### 数据源不存在时
- **ModelScope数据集缺失**：检查数据集ID是否正确，或使用NASA/AFDB备用源
- **权威数据库不可用**：降级为用户提供数据或合成数据，标注来源

### 数据格式不兼容时
- **坐标系不匹配**：执行坐标变换（极坐标↔笛卡尔）
- **单位不一致**：统一转换为SI单位
- **变量命名不规范**：映射到标准变量名

### 物理约束违反时
- **Cp分布异常**：检查攻角设置、Reynolds数是否合理
- **剪切应力异常**：检查网格质量、湍流模型设置
- **数据噪声过大**：应用滤波或降噪处理

## 质量检查

### 检查点1：文件完整性
- 文件可正常读取
- 数据维度匹配几何尺寸

### 检查点2：变量完整性
- 所有必需变量存在
- 变量类型正确（float/double）

### 检查点3：物理合理性
- Cp分布在合理范围内
- 剪切应力与边界层类型一致
- 无明显物理异常

### 检查点4：数据一致性
- 几何参数与数据匹配
- 边界条件设置合理
- 数据源标识明确

### 失败处理
- 检查点1失败：终止任务，报告文件错误
- 检查点2失败：尝试补充缺失变量或使用降级数据
- 检查点3失败：警告用户，继续执行但标记数据质量
- 检查点4失败：标记数据不一致，建议用户确认

## 回退策略

### 策略1：权威数据源替代
- ModelScope缺失 → NASA Turbulence Modeling Resource
- NASA缺失 → Airfoil Preprocessing Toolkit (AFDB)

### 策略2：数据格式转换
- 非结构化网格 → 插值到结构化网格
- 极坐标 → 笛卡尔坐标

### 策略3：合成数据降级
- 使用理论公式生成近似数据
- 标注`"data_source": "synthetic"`
- 附`synthetic_warning`提示

## 资源召回建议

### 何时召回本卡片
- 任务涉及翼型壁面压力剪切数据接入
- 数据契约核验步骤发现格式不符
- 需要评估数据源的权威性

### 配套资源
- `cfd-airfoil-data-intake-contract-validation`：通用翼型数据接入流程
- `cfd-acceptance-validation-applicability`：任务验收验证
- `cfd-model-evaluation-conservation-metrics`：物理约束指标评估

## 补充证据（权威文档）

[D1] NASA Turbulence Modeling Resource - Airfoil Validation Cases, NASA Langley Research Center, 2024, URL: https://turbmodels.larc.nasa.gov/airfoil.html（accessed_at 2026-09-17，权威数据源）
[D2] OpenFOAM Validation Guide - Incompressible Flow over Airfoil, OpenCFD Ltd, Version 11, URL: https://www.openfoam.com/documentation/guides/latest/doc/guide-tutorials.html（accessed_at 2026-09-17，权威数据源）

## 证据来源

[1] NASA Turbulence Modeling Resource, Airfoil Validation Cases, NASA Langley Research Center, 2024
[2] OpenFOAM Validation Guide, OpenCFD Ltd, Version 11, 2024
