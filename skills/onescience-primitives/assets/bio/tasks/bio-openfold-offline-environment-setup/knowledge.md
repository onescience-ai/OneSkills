# 科学计算环境离线安装与异常恢复

## 适用范围

面向网络连接受限环境下的科学计算工具（如 OpenFold、AlphaFold2 等）离线安装与配置。涵盖 PyPI 包依赖关系分析、离线包下载、本地镜像源配置、conda 离线安装流程，以及安装过程中的异常恢复策略。适用于 HPC 集群、隔离网络环境或安全限制严格的计算场景。

## 输入

- 目标软件包名称及版本（如 openfold、pytorch）
- 网络环境信息（是否可访问 PyPI/conda-forge）
- 操作系统和 Python 版本
- CUDA 版本（如需要 GPU 支持）

## 输出

- 离线安装包集合（.whl 文件或 conda 包）
- 安装脚本（可重复执行）
- 环境验证报告
- 异常恢复日志

## 流程节点

### 节点 1：依赖分析

操作：分析目标软件包的完整依赖树

工具：
- `pip show <package>`：查看直接依赖
- `pipdeptree`：生成完整依赖树
- `conda list --export`：导出 conda 环境

质量门禁：依赖树完整，无循环依赖

### 节点 2：离线包下载

操作：在有网络环境下预下载所有依赖包

PyPI 离线下载：
```bash
pip download <package> -d ./offline_packages --python-version 3.10 --only-binary=:all:
```

conda 离线下载：
```bash
conda install --download-only -p ./offline_env <package>
```

质量门禁：所有依赖包下载成功

### 节点 3：本地镜像源配置

操作：配置本地镜像源用于离线安装

PyPI 本地源：
```bash
pip install <package> --no-index --find-links=./offline_packages
```

conda 本地源：
```bash
conda install --use-local --offline <package>
```

质量门禁：安装成功，无网络请求

### 节点 4：环境验证

操作：验证安装后的环境

检查项：
- Python 版本正确
- 目标包可导入
- CUDA 可用（如需要）
- 依赖版本兼容

工具：
```bash
python -c "import openfold; print('OK')"
python -c "import torch; print(torch.cuda.is_available())"
```

质量门禁：所有验证通过

### 节点 5：异常恢复

操作：处理安装过程中的异常

常见异常及恢复策略：

| 异常类型 | 原因 | 恢复策略 |
|----------|------|----------|
| 网络超时 | 防火墙/代理限制 | 使用离线包安装 |
| 依赖冲突 | 版本不兼容 | 创建独立 conda 环境 |
| CUDA 不可用 | 驱动版本不匹配 | 安装对应 CUDA 版本的 PyTorch |
| 编译失败 | 缺少系统依赖 | 安装 build-essential 等系统包 |
| 内存不足 | 安装过程 OOM | 增加 swap 空间 |

工具：错误日志分析脚本

质量门禁：异常被正确处理，安装可继续

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Python 版本 | 3.8-3.11 | [1] | OpenFold 支持范围 |
| PyTorch 版本 | ≥ 1.12 | [1] | CUDA 兼容 |
| CUDA 版本 | ≥ 11.6 | [1] | 推荐 11.8 |
| conda 版本 | ≥ 4.10 | 领域标准 | 环境管理 |
| pip 版本 | ≥ 21.0 | 领域标准 | 包管理 |

### 校准数值

以下数值来自 OpenFold 实践，供量级校准；其他体系需以自身证据重新锚定：

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| OpenFold 安装时间（在线） | 10-30 分钟 | [D1] | 取决于网络速度 |
| OpenFold 安装时间（离线） | 5-15 分钟 | 实践经验 | 取决于磁盘速度 |
| OpenFold 依赖包数量 | ~50-100 | [D1] | 包括间接依赖 |
| conda 环境大小 | 2-5 GB | [D1] | 不含 GPU 驱动 |

## 边界与分流

- **前提 1**：有网络环境用于预下载离线包 → 否则需从其他介质传输
- **前提 2**：知道目标软件包的确切版本 → 否则需先确定版本兼容性
- **前提 3**：系统权限足够（或使用 conda 虚拟环境） → 否则使用用户级安装

## 质量检查

| 验证点 | 阈值 | 失败处理 |
|--------|------|----------|
| 依赖分析完成 | 100% | 检查包名称是否正确 |
| 离线包下载成功 | 100% | 检查网络或使用镜像 |
| 环境安装成功 | 无错误 | 查看错误日志 |
| 功能验证通过 | 可导入 | 检查版本兼容性 |

## 回退策略

1. 网络完全不可用 → 使用 USB 传输离线包
2. 依赖冲突 → 创建独立 conda 环境
3. CUDA 不可用 → 安装 CPU 版本 PyTorch
4. 系统权限不足 → 使用 `--user` 或 conda 虚拟环境
5. 磁盘空间不足 → 清理缓存或使用外部存储

## 资源召回建议

- 当用户提到离线安装、网络受限环境时召回本卡
- 当安装 OpenFold 等科学计算工具失败时召回本卡
- 配套资源：
  - `bio-openfold-gpu-computational-requirements`（GPU 需求）
  - `bio-openfold-standard-workflow`（标准工作流）

## 补充证据（开源文档）

[D1] OpenFold Installation Documentation, OpenFold Team, 2024, URL: https://openfold.readthedocs.io/en/latest/Installation.html (accessed_at, 官方文档)
[D2] OpenFold GitHub Repository, aqlaboratory, 2024, URL: https://github.com/aqlaboratory/openfold (accessed_at, 官方仓库)

## 证据来源

[1] Ahdritz G, Bouatta N, Floristean C, et al. OpenFold: retraining AlphaFold2 yields new insights into its learning mechanisms and capacity for generalization. *Nature Methods*, 2024, 21(8): 1514-1524. DOI: 10.1038/s41592-024-02272-z
