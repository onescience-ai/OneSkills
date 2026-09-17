# RDKit依赖管理与离线部署

## 适用范围
本卡服务的问题类是如何在分子生成和验证工作流中管理RDKit依赖，确保分子化学价检查、SMILES解析、3D构象生成等核心功能在不同计算环境中可靠运行。适用于需要分子化学操作的各类任务，包括分子生成、分子对接、虚拟筛选、化学信息学分析等，尤其针对网络受限或离线环境下的部署场景。

## 输入
- 分子生成代码或工作流脚本
- 目标计算环境信息（Python版本、操作系统、网络限制）
- 分子数据格式（SMILES、SDF、MOL等）
- 性能需求（批处理大小、计算精度）

## 输出
- 可用的RDKit Python模块
- 分子验证功能（化学价检查、芳香性检查、立体化学检查）
- 分子解析功能（SMILES解析、文件格式转换）
- 3D构象生成功能
- 依赖兼容性报告

## 流程节点
1. **需求分析** → 确定所需RDKit功能模块和版本要求
2. **安装方式选择** → 选择conda或pip安装，评估网络环境
3. **依赖安装** → 执行安装命令，处理依赖冲突
4. **功能验证** → 测试核心功能（SMILES解析、化学价检查、3D生成）
5. **离线打包** → 创建离线安装包（conda包或wheel文件）
6. **环境部署** → 在目标环境安装并验证

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 安装工具 | conda/pip | [D1] | conda推荐用于复杂依赖，pip用于简单安装 |
| Python版本 | 3.8+ | [D1] | RDKit 2026.03.6要求Python 3.8以上 |
| 核心功能模块 | Chem, AllChem, Descriptors | [D1] | 分子操作、化学描述符计算 |
| 文件格式支持 | SMILES, SDF, MOL, PDB | [D1] | 分子结构文件读写 |
| 3D构象生成 | EmbedMolecule, MMFFOptimizeMolecule | [D1] | 分子三维结构生成与优化 |

### 校准数值（以下数值来自BoKDiff体系，供量级校准；其他体系需以自身证据重新锚定）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 典型安装大小 | 100-500MB | [D1] | 包含C++核心和Python包装器 |
| 安装时间 | 5-30分钟 | [D1] | 取决于网络和安装方式 |
| 内存占用 | 50-200MB | [D1] | 运行时内存需求 |
| 批处理速度 | 1000-10000分子/秒 | [D1] | SMILES解析速度 |

## 边界与分流
- **网络完全不通**：使用预下载的conda包或wheel文件，通过USB传输
- **版本冲突**：使用conda环境隔离，或创建新的虚拟环境
- **编译错误**：检查C++编译器版本（需要支持C++11/20），安装必要开发工具
- **功能缺失**：检查是否安装了完整版RDKit，而非精简版
- **性能问题**：使用RDKit的C++扩展模块，或优化批处理逻辑

## 质量检查
- 能够成功导入RDKit核心模块（from rdkit import Chem）
- 能够解析SMILES字符串为分子对象
- 能够执行化学价检查和芳香性检查
- 能够生成合理的3D构象
- 能够读写常见分子文件格式

## 回退策略
- 官方源不可用时，使用镜像源或离线包
- 版本不兼容时，使用旧版本或重新编译
- 功能不完整时，安装额外组件（如PostgreSQL扩展）
- 性能不足时，使用C++扩展或并行处理

## 资源召回建议
当遇到以下情况时召回本卡片：
- 需要在分子生成任务中安装或配置RDKit
- 遇到RDKit导入错误或功能缺失
- 需要在离线环境部署分子化学操作功能
- 管理分子生成工作流的依赖关系
- 优化分子处理性能

## 补充证据（开源文档/用户自有，可选）
[D1] Installation — The RDKit 2026.03.6 documentation, RDKit, version 2026.03.6, URL: https://www.rdkit.org/docs/Install.html（accessed_at 2026-09-16，权威官方文档）
[D2] BoKDiff: Best-of-K diffusion Alignment for Enhancing 3D Molecule Generation, GitHub Repository, main branch, URL: https://github.com/khodabandeh-ali/BoKDiff（accessed_at 2026-09-16，开源项目文档）

## 证据来源
[1] Installation — The RDKit 2026.03.6 documentation, Greg Landrum et al., RDKit, 2026
[2] BoKDiff: Best-of-K diffusion Alignment for Enhancing 3D Molecule Generation, Khodabandeh Yalabadi et al., Bioinformatics Advances, 2025