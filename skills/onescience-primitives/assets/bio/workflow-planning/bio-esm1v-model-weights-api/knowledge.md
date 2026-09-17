# ESM-1v模型权重和加载API指南

## 适用范围
适用于需要加载和使用ESM-1v模型进行蛋白变异效应预测的场景，包括但不限于：
- 蛋白变异效应预测（DMS数据分析）
- 蛋白质结构预测
- 蛋白序列分析
- 生物信息学研究

不适用场景：
- 非ESM系列模型
- 需要微调模型的场景（本指南仅涉及预训练权重）
- 需要GPU加速的场景（本指南仅涉及CPU加载）

## 输入
- 模型版本：ESM-1v (esm1v_t33_650M_UR90S_1)
- 依赖库：esm (Facebook Research ESM Python库)
- 计算环境：Python 3.7+, PyTorch

## 输出
- 加载的ESM-1v模型对象
- 零样本预测分数（wt-marginals策略）
- 模型验证信息（权重SHA256校验、参数量）

## 流程节点
1. **权重下载** → 从Facebook Research ESM GitHub获取官方权重
2. **环境准备** → 安装esm库和依赖
3. **模型加载** → 使用esm.pretrained加载API
4. **权重验证** → 校验SHA256哈希值
5. **评分计算** → 实现wt-marginals零样本评分策略

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型文件名 | esm1v_t33_650M_UR90S_1.pt | [Facebook Research] | 官方权重文件 |
| 参数量 | 650M | [ESM论文] | 650M参数模型 |
| 加载API | esm.pretrained.esm1v_t33_650M_UR90S_1() | [ESM文档] | 官方加载函数 |
| 评分策略 | wt-marginals | [归因报告] | 零样本评分方法 |
| 依赖库版本 | esm>=1.0.0 | [ESM GitHub] | Python库版本要求 |

## 边界与分流
- **网络不可用**：权重文件约1.2GB，需稳定网络连接
- **磁盘空间不足**：确保至少2GB可用空间
- **版本不兼容**：esm库版本需≥1.0.0
- **GPU不可用**：模型可在CPU上运行，但速度较慢
- **内存不足**：至少需要4GB RAM

## 质量检查
1. **权重文件完整性**：校验SHA256哈希值
2. **参数量验证**：加载后检查参数量是否为650M
3. **加载日志**：记录加载过程中的警告和错误
4. **评分验证**：用已知突变验证评分分布
5. **版本确认**：确认使用的是ESM-1v而非其他版本

## 回退策略
1. **GitHub不可用**：从Hugging Face Hub获取相同权重
2. **esm库安装失败**：从GitHub源码安装
3. **内存不足**：使用较小的ESM模型（如ESM-2 35M）
4. **评分计算失败**：使用简化评分策略（如log-likelihood）

## 资源召回建议
当需要加载ESM-1v模型进行蛋白变异效应预测时召回本卡片。配套资源：
- workflow-planning/bio-tem1-dms-data-sources（数据源原语）
- workflow-planning/dms-supervised-variant-effect-prediction（工作流原语）
- workflow-planning/bio-protein-prediction-quality-metrics（质量评估原语）

## 证据来源
[1] 归因报告：TEM-1β-内酰胺酶深度突变效应排序任务，任务ID：12
[2] ESM-1v模型论文：Evolutionary-scale prediction of atomic-level protein structure with a language model
[3] Facebook Research ESM GitHub仓库：官方权重下载和API文档
[4] ESM Python库文档：加载和使用说明