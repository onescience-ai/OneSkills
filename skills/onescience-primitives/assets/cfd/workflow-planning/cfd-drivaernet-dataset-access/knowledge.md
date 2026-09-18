# DrivAerNet数据集获取与验证

## 适用范围
适用于需要获取汽车空气动力学CFD数据集进行外形优化、代理模型训练或数据驱动设计的任务。不适用于非汽车领域或需要非公开数据集的场景。

## 输入
- 数据集名称：DrivAerNet/DrivAerNet++
- 下载来源：GitHub仓库或ModelScope
- 数据格式：STL表面网格 + CFD流场结果

## 输出
- 下载的数据集文件（STL几何、CFD结果CSV）
- 数据审计报告（样本数、变量名、单位、坐标系、许可证）
- 数据集清单（dataset_manifest.json）

## 流程节点
1. **数据集发现** → 定位DrivAerNet GitHub仓库或ModelScope页面
2. **数据下载** → 下载STL几何文件和CFD结果文件
3. **数据验证** → 检查样本数、变量名、单位、坐标系
4. **许可证检查** → 确认CC-BY许可证
5. **数据审计** → 生成data_audit.md报告

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 样本数 | 约3000 | 用户自有 | 汽车3D几何样本数量 |
| 几何格式 | STL表面网格 | 用户自有 | 三角面片网格 |
| CFD结果 | 阻力系数Cd、升力系数Cl、表面压力分布 | 用户自有 | 气动性能指标 |
| 单位体系 | SI制（米、帕斯卡等） | 用户自有 | 国际单位制 |
| 坐标系 | 右手系 | 用户自有 | 符合CFD惯例 |
| 许可证 | CC-BY 4.0 | 用户自有 | 知识共享署名 |
| 下载地址 | https://github.com/DrivAerNet/DrivAerNet | 用户自有 | GitHub仓库 |

## 边界与分流
- 若GitHub访问受限，可尝试ModelScope镜像或国内镜像站
- 若数据量过大，可考虑下载子集进行测试
- 若需要原始网格而非STL，需联系数据集作者

## 质量检查
- 验证下载文件完整性（SHA256校验）
- 检查STL文件是否可被网格处理软件读取
- 验证CFD结果中的阻力系数是否为正值

## 回退策略
- 若DrivAerNet不可用，可考虑使用Ahmed body或MIRA简化模型作为替代
- 若许可证不兼容，需重新评估数据使用方案

## 资源召回建议
- 当任务涉及汽车CFD数据接入时召回本卡片
- 配套资源：cfd-leakage-free-split-strategy、cfd-diffusion-model-shape-design

## 证据来源
[U1] 归因报告 CFD_S032 report.json 中的优化计划描述（用户自有, 未经公开源验证）
[U2] DrivAerNet GitHub仓库信息（用户自有, 未经公开源验证）