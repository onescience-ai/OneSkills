# rdkit在分子生成工作流中的安装与依赖

## 适用范围
适用于需要rdkit进行分子化学价验证、SMILES解析、3D构象生成等分子生成任务的环境配置。rdkit是分子生成和验证的核心依赖。

## 输入
- Python环境（推荐3.8+）
- 网络访问权限（用于安装）或离线安装包
- conda或pip包管理器

## 输出
- 可导入的rdkit模块
- 版本信息确认

## 流程节点
1. **环境检查** → 确认Python版本和包管理器可用
2. **安装rdkit** → 使用conda或pip安装
3. **版本验证** → 检查rdkit版本兼容性
4. **功能测试** → 导入rdkit并执行简单操作
5. **依赖管理** → 确保其他依赖兼容

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 安装命令（conda） | conda install rdkit -c conda-forge | [D1] | 推荐方式 |
| 安装命令（pip） | pip install rdkit-pypi | [D1] | 备选方式 |
| Python版本 | 3.8+ | [D1] | 兼容性要求 |
| 核心功能 | 分子化学价检查、SMILES解析、3D构象生成 | [D1] | 在分子生成中的作用 |

## 边界与分流
- **网络受限**：无法访问conda-forge或PyPI时，需使用离线安装包或镜像源
- **版本冲突**：rdkit与其他依赖冲突时，需创建独立conda环境
- **安装失败**：pip安装失败时，尝试conda安装或使用预编译wheel

## 质量检查
- 运行 `python -c "from rdkit import Chem; print('rdkit available')"` 确认导入成功
- 检查rdkit版本：`python -c "from rdkit import Chem; print(Chem.rdBase.rdkitVersion)"`

## 回退策略
- 使用其他化学信息学工具（如OpenBabel）
- 使用简化版本或替代算法
- 在容器化环境中预装rdkit

## 资源召回建议
当需要安装rdkit或遇到rdkit导入错误时召回本卡片。

## 补充证据（开源文档）
[D1] BoKDiff GitHub Repository, GitHub, main branch, URL: https://github.com/khodabandeh-ali/BoKDiff（accessed_at 2026-09-21）

## 证据来源
[1] BoKDiff GitHub Repository, https://github.com/khodabandeh-ali/BoKDiff