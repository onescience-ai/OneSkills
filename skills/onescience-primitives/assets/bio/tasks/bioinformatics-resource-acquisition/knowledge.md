# 生物信息学数据集和模型权重的专业获取渠道

## 适用范围
本卡片描述生物信息学领域数据集和模型权重的专业获取渠道和检索策略。当需要获取蛋白质结构数据、分子对接数据集、机器学习模型权重等资源时，可参考此指南。

## 输入
- 资源名称或描述
- 资源类型（数据集、模型权重、工具等）
- 目标用途（训练、评估、应用等）

## 输出
- 资源获取渠道列表
- 访问方式和许可证信息
- 替代资源推荐

## 流程节点
1. **资源识别** → 明确所需资源的名称、类型和用途
2. **权威平台检索** → 直接访问已知权威平台
3. **论文附属资源检查** → 查找论文GitHub仓库或补充材料
4. **专业数据库搜索** → 使用专业生物信息学数据库
5. **许可证确认** → 确认资源使用条款和限制
6. **替代方案评估** → 若原资源不可用，评估替代方案

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 主要数据库 | PDBbind, AlphaFold, UniProt | [1] | 生物信息学核心资源 |
| 模型权重平台 | HuggingFace, GitHub, Zenodo | [D1] | 模型权重常用托管平台 |
| 数据集平台 | PDB, ChEMBL, BindingDB | [1] | 生物活性数据主要来源 |
| 文献预印本 | arXiv, bioRxiv | [1] | 最新研究成果发布渠道 |

## 边界与分流
- 当资源为专有数据时：联系论文作者或机构获取
- 当资源需要注册时：使用机构邮箱注册学术账号
- 当资源有访问限制时：寻找替代数据集或使用API接口
- 当资源格式不兼容时：使用格式转换工具

## 质量检查
- 验证资源URL可访问性
- 确认资源版本和更新时间
- 检查资源完整性和一致性
- 确认许可证兼容性

## 回退策略
- 若权威平台不可用，尝试镜像站点或缓存版本
- 若论文附属资源缺失，联系作者或使用替代数据集
- 若商业资源无法获取，寻找学术替代方案

## 资源召回建议
- 当需要获取生物信息学资源时召回本卡片
- 配套资源：PDBbind（对接数据集）、AlphaFold（蛋白质结构）、HuggingFace（模型权重）

## 补充证据（开源文档）
[D1] AlphaFold Database Structure Extractor, IIT Hyderabad, v2025, URL: https://project.iith.ac.in/sharmaglab/alphafoldextractor/（accessed_at 2026-09-21，官方工具）
[D2] PDBbind Database, Center for Computational Drug Discovery, v2020, URL: http://www.pdbbind.org.cn/（accessed_at 2026-09-21，权威数据库）

## 证据来源
[1] Saraf N, Karthik V, Sharma G. AlphaFold Database Structure Extractor: a web server and API to download AlphaFold structures using common protein accessions. BMC Bioinformatics. 2025;26:237. DOI: 10.1186/s12859-025-06303-0