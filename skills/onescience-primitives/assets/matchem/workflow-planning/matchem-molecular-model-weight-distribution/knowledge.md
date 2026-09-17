# 分子生成模型权重管理与离线分发

## 适用范围
本卡服务的问题类是如何在分子生成任务中获取、存储、版本管理和分发模型权重文件，确保模型在不同计算环境中可复现和可靠加载。适用于各类基于深度学习的分子生成模型，包括扩散模型、生成对抗网络、变分自编码器等，尤其针对网络受限或离线环境下的模型部署场景。

## 输入
- 模型架构定义文件（如PyTorch模型类）
- 训练好的模型权重文件（.pt, .pth, .ckpt等格式）
- 模型配置文件（超参数、训练设置等）
- 目标计算环境信息（GPU/CPU、操作系统、Python版本）

## 输出
- 模型权重文件（可加载的checkpoint）
- 权重版本元数据（版本号、训练参数、数据集信息）
- 加载脚本或配置文件
- 环境依赖清单

## 流程节点
1. **权重获取** → 从官方源（GitHub Releases、模型仓库、Google Drive）下载预训练权重
2. **权重验证** → 检查文件完整性（MD5/SHA256校验）、格式兼容性
3. **本地存储** → 按版本号组织目录结构，建立本地缓存
4. **版本管理** → 记录权重与代码版本的对应关系，支持多版本共存
5. **离线分发** → 打包权重文件与依赖，创建离线安装包
6. **权重加载** → 在目标环境中加载权重，验证加载成功

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 权重文件格式 | .pt/.pth/.ckpt | [D1] | PyTorch标准格式，使用torch.save/torch.load |
| 校验算法 | MD5/SHA256 | [D2] | 确保文件传输完整性 |
| 版本号格式 | 主版本.次版本.修订号 | [D1] | 语义化版本控制 |
| 缓存目录结构 | models/{model_name}/{version}/ | [D1] | 统一组织规范 |
| 跨设备兼容 | map_location参数 | [D1] | 支持CPU/GPU迁移加载 |

### 校准数值（以下数值来自BoKDiff体系，供量级校准；其他体系需以自身证据重新锚定）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 典型权重文件大小 | 100MB-1GB | [D1] | 分子生成模型常见规模 |
| 权重存储位置 | pretrained_models/ | [D1] | 项目根目录下的专用文件夹 |
| 权重获取途径 | Google Drive | [D1] | 官方预训练权重分享渠道 |
| 依赖管理工具 | conda/pip | [D1] | 环境隔离与依赖安装 |

## 边界与分流
- **网络完全不通**：使用预下载的离线包，通过USB或内部网络传输
- **权重格式不兼容**：检查PyTorch版本，使用torch.load的weights_only参数或转换格式
- **版本冲突**：使用虚拟环境隔离，或容器化部署（Docker/Singularity）
- **磁盘空间不足**：使用符号链接或网络文件系统（NFS）共享权重
- **多GPU环境**：保存时使用model.module.state_dict()，加载时指定map_location

## 质量检查
- 权重文件非空且可被torch.load成功加载
- 加载后的模型能正常执行forward推理
- 权重版本与代码版本匹配（通过配置文件或元数据验证）
- 跨设备加载测试（GPU→CPU，CPU→GPU）

## 回退策略
- 官方源不可用时，检查镜像源或联系维护者
- 权重损坏时，重新下载或从备份恢复
- 版本不兼容时，使用旧版本代码或重新训练
- 离线环境无法验证时，记录环境信息供后续调试

## 资源召回建议
当遇到以下情况时召回本卡片：
- 需要获取或分发分子生成模型的预训练权重
- 在网络受限环境中部署分子生成模型
- 管理多个模型版本或进行版本回滚
- 建立模型权重的本地缓存机制
- 配置离线科学计算环境

## 补充证据（开源文档/用户自有，可选）
[D1] BoKDiff: Best-of-K diffusion Alignment for Enhancing 3D Molecule Generation, GitHub Repository, main branch, URL: https://github.com/khodabandeh-ali/BoKDiff（accessed_at 2026-09-16，权威开源项目文档）
[D2] Saving and Loading Models, PyTorch Documentation, v2.14.0, URL: https://pytorch.org/tutorials/beginner/saving_loading_models.html（accessed_at 2026-09-16，官方权威文档）

## 证据来源
[1] BoKDiff: Best-of-K diffusion Alignment for Enhancing 3D Molecule Generation, Khodabandeh Yalabadi et al., Bioinformatics Advances, 2025, DOI: 10.1093/bioadv/vbaf137
[2] Saving and Loading Models, PyTorch Contributors, PyTorch Documentation, 2023