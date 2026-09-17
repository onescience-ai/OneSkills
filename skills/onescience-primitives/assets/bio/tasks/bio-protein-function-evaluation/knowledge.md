# 蛋白质功能预测评估

## 适用范围
- **触发条件**：需要评估蛋白质功能预测模型的性能
- **适用场景**：CAFA挑战赛评估、模型性能对比、分层性能分析
- **不适用场景**：仅需简单准确率、二分类评估

## 输入
- 模型预测结果（predictions.csv）
- 真实标签（test set GO labels）
- 评估配置：threshold、n_bootstrap

## 输出
- 分层评估报告：per-class F1、macro/micro/weighted F1
- AUPRC曲线和分数
- bootstrap置信区间
- 适用域声明

## 流程节点

### 节点1：阈值应用
**操作**：将模型输出概率转换为二分类预测
**参数**：threshold=0.5
**工具**：numpy
**质量门禁**：预测标签格式正确

### 节点2：分层F1计算
**操作**：计算per-class F1、macro/micro/weighted F1
**参数**：average参数
**工具**：sklearn.metrics.f1_score
**质量门禁**：各指标计算正确

### 节点3：AUPRC计算
**操作**：计算每个GO类别的AUPRC
**参数**：置信区间
**工具**：sklearn.metrics.average_precision_score
**质量门禁**：AUPRC分数在0-1范围

### 节点4：Bootstrap置信区间
**操作**：估计macro F1的置信区间
**参数**：n_bootstrap=1000、confidence=0.95
**工具**：numpy bootstrap
**质量门禁**：置信区间合理

### 节点5：适用域声明
**操作**：根据性能指标声明模型适用域
**参数**：阈值标准
**工具**：规则引擎
**质量门禁**：适用域声明明确

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| threshold | 0.5 | [任务要求] | 二分类判定阈值 |
| macro_f1_threshold | 0.7 | [任务要求] | 验收硬性门槛 |
| n_bootstrap | 1000 | [经验] | bootstrap次数 |
| confidence | 0.95 | [经验] | 置信区间水平 |
| metrics | F1, AUPRC, Fmax | [CAFA4] | 评估指标集 |

## 边界与分流
- macro_f1 < 0.7：标记REJECT，不通过验收
- 单类别F1极低：检查该类别样本量和标注质量
- 置信区间过宽：增加测试样本量
- 跨家族泛化差：检查训练集和测试集的物种分布

## 质量检查
- macro_f1 > 0.7（验收阈值）
- 各GO类别F1明细表
- bootstrap置信区间声明
- 适用域声明

## 回退策略
- 评估指标不达标：检查数据质量、调整模型
- 无法计算AUPRC：使用Fmax替代
- 适用域声明失败：标记PARTIAL

## 资源召回建议
- 组件：`edge:resource:bio/components/bio-go-ontology-validator`
- 工作流：`edge:workflow:bio-fewshot-protein-function-prediction-workflow`

## 证据来源
[1] Piovesan et al., "CAFA-evaluator: a Python tool for benchmarking ontological classification methods", Bioinformatics Advances, 2024, DOI: 10.1093/bioadv/vbae043
[2] BMC Bioinformatics, "Protein function prediction through multi-view multi-label latent tensor reconstruction", 2024, DOI: 10.1186/s12859-024-05789-4