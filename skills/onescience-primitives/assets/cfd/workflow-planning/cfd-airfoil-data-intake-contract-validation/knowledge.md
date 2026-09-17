# 数据接入与契约核验任务

## 适用范围
本任务适用于接入参数化翼型多工况与多保真数据，核验样本、变量、单位、网格坐标及许可，为后续预处理与建模提供可靠数据基础。

## 输入
- 数据集路径（目录或清单文件）
- 数据集名称
- 数据契约（可选，包含变量单位网格定义）

## 输出
- 数据清单（dataset_manifest.json）
- 数据契约（data_contract.json）
- 数据审计报告（data_audit.md）

## 流程节点
1. 读取数据集路径
2. 检查文件可读性
3. 统计样本数
4. 识别输入与目标变量
5. 验证单位与坐标系
6. 检查网格拓扑
7. 确定时间或工况范围
8. 检测缺失值
9. 核查使用许可
10. 输出机器可读契约

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填输入 | 数据集路径、数据集名称 | [场景需求书] | 缺少时返回BLOCKED |
| 可选输入 | 数据契约 | [场景需求书] | 变量单位网格定义 |
| 输出格式 | JSON, Markdown | [场景需求书] | 机器可读与人工可读 |

## 边界与分流
- 数据文件不可读：返回BLOCKED，列出缺项。
- 样本数不足：警告，但继续执行。
- 变量单位缺失：返回BLOCKED，要求补充。
- 网格坐标未定义：返回BLOCKED，要求补充。
- 使用许可限制：记录限制，提醒后续步骤。

## 质量检查
- 数据文件可读且样本可追溯。
- 输入目标变量单位坐标定义完整。
- 不存在训练测试泄漏。

## 回退策略
- 数据不可读：检查数据路径与格式，或联系数据提供方。
- 变量单位缺失：参考标准单位体系或联系数据提供方。
- 网格坐标未定义：参考翼型标准坐标系或联系数据提供方。

## 资源召回建议
当用户需要进行数据接入与契约核验时，可召回本任务卡片。配套资源包括：
- 数据读取工具
- 数据质量检查工具
- 数据契约生成工具

## 证据来源
[1] A Kernel-based Resource-efficient Neural Surrogate for Multi-fidelity Prediction of Aerodynamic Field, arXiv:2512.10287, 2025
[2] AFBench_ A Large-scale Benchmark for Airfoil Design, arXiv:1411.1784, 2014
[3] Airfoil optimization using Design-by-Morphing with minimized design-space dimensionality, arXiv:2510.16020, 2025
[4] Predictive Criteria for Electrospray-Assisted Droplet Dynamics in Aerodynamic Flow Fields, arXiv:2509.22676, 2025
[5] AeroJEPA_ Learning Semantic Latent Representations for Scalable 3D Aerodynamic Field Modeling, arXiv:2605.05586, 2026
[6] AirfoilGen_ A valid-by-construction and performance-aware latent diffusion model for airfoil generation, arXiv:2605.20303, 2026