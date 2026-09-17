# 多孔硅负极材料结构与电池工况参数知识

## 适用范围
- **触发条件**：orchestrator 在 s01 步骤执行材料与工况建模时
- **适用场景**：多孔硅锂离子电池负极结构设计任务，需要用户提供材料结构和工况参数
- **不适用场景**：已有完整输入参数的任务、非硅基负极材料任务

## 输入
### 材料结构文件格式
1. **CIF (Crystallographic Information File)**
   - 适用于晶体结构描述
   - 包含原子坐标、晶格参数、空间群等信息
   - 常用来源：ICSD、Materials Project、COD

2. **POSCAR (VASP Position File)**
   - 适用于第一性原理计算
   - 包含晶格矢量、原子坐标、选择性动力学约束
   - 格式：注释行 + 缩放因子 + 晶格矢量 + 原子种类和数量 + Direct/Cartesian坐标

### 电池工况参数
| 参数类别 | 具体参数 | 单位 | 说明 |
|----------|----------|------|------|
| 电压参数 | 充电截止电压 | V | 通常 0.01-1.5V vs Li/Li+ |
| 电压参数 | 放电截止电压 | V | 通常 0.01-1.5V vs Li/Li+ |
| 温度参数 | 工作温度 | °C 或 K | 室温 25°C 或高温 45-60°C |
| 电流参数 | 充放电倍率 | C | 0.1C-5C，影响容量和寿命 |
| 电解液 | 电解液类型 | - | EC:DMC、LiPF6浓度等 |
| 对电极 | 对电极材料 | - | 金属锂、LiFePO4等 |

## 输出
### 输入完整性检查结果
- **完整**：所有必填参数已提供，可进入计算/实验配置
- **部分缺失**：部分参数缺失，需向用户请求补充
- **缺失**：关键参数完全缺失，标记 BLOCKED

### 用户请求模板
```yaml
missing_inputs:
  - parameter: MATERIAL_STRUCTURE
    description: "材料结构文件（CIF/POSCAR格式）"
    required: true
    suggestion: "请提供多孔硅的晶体结构文件，或从Materials Project等数据库获取"
  - parameter: CELL_CONDITION
    description: "电池工况参数"
    required: true
    suggestion: "请提供电压窗口、温度、倍率等参数"
```

## 流程节点
1. **接收任务上下文** → 提取用户提供的材料和工况信息
2. **格式验证** → 检查文件格式是否符合CIF/POSCAR规范
3. **完整性检查** → 按必填参数列表逐项验证
4. **决策路由**：
   - 参数完整 → 标记"已提供"，进入s02
   - 参数部分缺失 → 向用户请求补充
   - 参数完全缺失 → 标记BLOCKED，终止流程

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填参数数量 | 6 | 工作流标准 | 材料结构、电压窗口、温度、倍率、电解液、对电极 |
| 可选参数数量 | 5 | 工作流标准 | 孔隙率、粒径分布、比表面积、压实密度、粘结剂 |
| 用户响应超时 | 300s | 配置 | 超时后使用默认值或终止 |

## 边界与分流
### 异常处理
1. **文件格式错误**：拒绝解析，返回格式说明
2. **参数超出范围**：警告但允许继续（如倍率>10C）
3. **用户无响应**：超时后标记BLOCKED

### 降级策略
- 当用户无法提供CIF文件时，可使用简化POSCAR（仅原子坐标）
- 当工况参数不完整时，使用标准测试条件（25°C, 0.1C）

## 质量检查
- [ ] 材料结构文件可被VASP/LAMMPS正确读取
- [ ] 电压窗口在硅负极安全范围内（0.01-1.5V）
- [ ] 温度参数在合理范围内（-20°C 至 60°C）
- [ ] 倍率参数与电池设计目标匹配

## 回退策略
1. 用户拒绝提供 → 使用文献典型值（标注来源）
2. 文件损坏 → 请求重新上传或提供下载链接
3. 格式不兼容 → 提供格式转换工具或说明

## 资源召回建议
- **何时召回**：s01步骤开始时、用户输入验证失败时
- **配套资源**：matchem-si-anode-simulation-tools（计算工具选择）

## 证据来源
[1] Hierarchical porous silicon structures with extraordinary mechanical strength as high-performance lithium-ion battery anodes, Nature Communications, 2020, DOI: 10.1038/s41467-020-15217-9
[2] Fundamental Understanding and Facing Challenges in Structural Design of Porous Si-Based Anodes for Lithium-Ion Batteries, Advanced Functional Materials, 2023, DOI: 10.1002/adfm.202301109