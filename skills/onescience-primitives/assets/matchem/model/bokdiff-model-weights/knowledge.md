# BoKDiff模型权重获取与管理

## 适用范围
适用于需要加载BoKDiff模型权重进行靶标特异性三维分子生成的任务。权重文件必须与BoKDiff代码版本匹配，格式为PyTorch检查点(.ckpt)。

## 输入
- BoKDiff代码仓库（可通过GitHub克隆）
- 网络访问权限（用于下载权重）或本地缓存的权重文件
- PyTorch环境

## 输出
- 可加载的模型权重文件（bokdiff.ckpt）
- 权重文件元数据（版本、来源）

## 流程节点
1. **获取权重文件** → 从Google Drive下载预训练检查点
2. **验证文件完整性** → 检查文件大小、校验和
3. **本地存储** → 将权重文件放置在指定目录（如pretrained_models/）
4. **版本匹配** → 确保权重与代码版本兼容
5. **加载权重** → 使用PyTorch加载检查点到模型

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 权重文件格式 | .ckpt | [D1] | PyTorch检查点文件 |
| 下载来源 | Google Drive | [D1] | 官方提供预训练权重 |
| 存储路径 | pretrained_models/ | [D1] | 代码仓库内默认路径 |
| 基础模型 | DecompDiff | [D1] | BoKDiff基于DecompDiff训练 |

## 边界与分流
- **网络受限**：无法访问Google Drive时，需使用离线镜像或预下载权重
- **版本不匹配**：权重与代码版本不兼容时，需重新下载对应版本
- **文件损坏**：下载文件损坏时，需重新下载或验证校验和

## 质量检查
- 检查权重文件是否存在且可读
- 验证文件大小是否合理（通常数百MB）
- 尝试加载权重确保无格式错误

## 回退策略
- 使用其他来源的权重（如社区共享）
- 从头训练模型（需要数据和计算资源）
- 使用简化模型或替代方案

## 资源召回建议
当需要加载BoKDiff模型权重或遇到权重相关错误时召回本卡片。

## 补充证据（开源文档）
[D1] BoKDiff GitHub Repository, GitHub, main branch, URL: https://github.com/khodabandeh-ali/BoKDiff（accessed_at 2026-09-21）

## 证据来源
[1] BoKDiff GitHub Repository, https://github.com/khodabandeh-ali/BoKDiff