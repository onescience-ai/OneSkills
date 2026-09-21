# 多孔硅负极电化学模拟工具选择

## 适用范围
适用于多孔硅锂离子电池负极电化学模拟任务，根据模拟尺度（原子、介观、宏观）和物理过程（电子结构、离子扩散、力学响应）选择合适的计算工具。

## 输入
- 模拟目标：电子结构、离子扩散、电化学性能、力学响应
- 尺度要求：原子尺度（DFT）、介观尺度（MD）、宏观尺度（连续介质）
- 精度与成本权衡：高精度但计算昂贵 vs 低精度但快速

## 输出
- 推荐计算工具：VASP、LAMMPS、COMSOL等
- 输入文件格式：POSCAR、INCAR、LAMMPS input script等
- 资源需求评估：CPU/GPU时间、内存、存储

## 流程节点
1. 模拟目标分析 → 确定需要模拟的物理过程和尺度
2. 工具适用性评估 → 根据目标匹配工具能力 [1]
3. 输入输出格式确认 → 准备必要的输入文件和数据
4. 资源需求评估 → 估算计算成本和时间

## 关键参数
| 工具 | 适用尺度 | 适用物理过程 | 输入格式 | 资源需求 | 来源 |
|------|----------|--------------|----------|----------|------|
| VASP | 原子尺度 | 电子结构、DFT计算 | POSCAR, INCAR | 高CPU/内存 | 通用知识 |
| LAMMPS | 原子/介观 | 分子动力学、力学响应 | LAMMPS input | 中等CPU/GPU | 通用知识 |
| COMSOL | 宏观/连续介质 | 电化学、多物理场耦合 | COMSOL模型 | 中等CPU | [1] |
| Gaussian | 原子尺度 | 量子化学 | Gaussian input | 高CPU | 通用知识 |

## 边界与分流
- 若模拟目标不明确：从宏观尺度COMSOL模拟开始，逐步细化到原子尺度
- 若计算资源有限：优先使用COMSOL进行快速原型设计，再用VASP进行高精度验证
- 若工具不熟悉：选择有文档和社区支持的工具（如LAMMPS、COMSOL）

## 质量检查
- 验证工具选择与模拟目标匹配
- 验证输入文件格式正确
- 验证资源需求在可用范围内

## 回退策略
- 若首选工具不可用，使用替代工具（如VASP不可用时尝试Quantum ESPRESSO）
- 若计算成本过高，使用简化模型或降级到介观/宏观尺度

## 资源召回建议
当任务涉及多孔硅负极电化学模拟、计算材料科学、多尺度建模时召回本卡片。配套资源：材料结构参数卡片、电池工况参数卡片。

## 补充证据（开源文档/用户自有，可选）
[D1] COMSOL Multiphysics官方文档, COMSOL AB, 2024, URL: https://www.comsol.com/documentation/ (accessed_at, 交叉验证)
[D2] VASP官方文档, University of Vienna, 2024, URL: https://www.vasp.at/wiki/ (accessed_at, 交叉验证)

## 证据来源
[1] Comsol Simulation of Hierarchical Ordered Porous Microstructure Electrode, Azami-Ghadkolai et al., ECS Meeting Abstracts, 2019, DOI: 10.1149/ma2019-01/22/1158