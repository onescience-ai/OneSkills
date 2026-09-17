# 蛋白质功能预测数据集获取

## 适用范围
- **触发条件**：执行蛋白质功能预测任务时需要获取公开数据集
- **适用场景**：CAFA挑战赛基准测试、few-shot蛋白功能预测、新蛋白家族功能注释
- **不适用场景**：已有私有数据集、仅需数据格式规范

## 输入
- 数据源选择：CAFA数据集、UniProtKB、TAIR等
- 数据格式要求：CSV（protein_id, sequence, structure_features, go_labels）
- GO注释命名空间：BP（Biological Process）、MF（Molecular Function）、CC（Cellular Component）

## 输出
- 标准化数据集文件（fewshot_functions.csv或等效格式）
- 数据统计：样本量、类别分布、序列长度分布
- 数据质量报告：标签唯一性、序列合法性、缺失值统计

## 流程节点

### 节点1：数据源检索
**操作**：检索CAFA、UniProtKB等公开数据源
**参数**：物种范围、GO命名空间、注释证据代码
**工具**：UniProtKB REST API（https://rest.uniprot.org/）
**质量门禁**：数据源可访问、返回有效数据

### 节点2：数据下载与解析
**操作**：下载数据并解析为标准格式
**参数**：批量下载大小、解析编码
**工具**：Python requests/pandas
**质量门禁**：文件完整性、编码正确、无损坏记录

### 节点3：数据格式验证
**操作**：验证CSV列定义和数据类型
**参数**：列名（protein_id, sequence, structure_features, go_labels）
**工具**：pandas schema validation
**质量门禁**：列完整性、数据类型正确、无空值

### 节点4：数据统计与质量报告
**操作**：生成数据统计和质量报告
**参数**：统计维度（样本量、类别分布、序列长度）
**工具**：pandas/numpy
**质量门禁**：统计完整、报告可读

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| data_format | CSV | [CAFA4] | 标准数据交换格式 |
| columns | protein_id, sequence, structure_features, go_labels | [任务要求] | 必需列定义 |
| go_namespaces | BP, MF, CC | [Gene Ontology] | 三个命名空间 |
| evidence_codes | IEA, IDA, IBA, IMP | [UniProtKB] | 注释证据代码 |

## 边界与分流
- CAFA数据集不可用：使用UniProtKB REST API获取
- 数据量过大：分批下载，流式处理
- 格式不匹配：编写适配器转换
- 标签缺失：记录并标记缺失样本

## 质量检查
- fewshot_functions.csv文件存在且可读
- 列完整性验证（4列必需）
- GO标签与Gene Ontology本体一致性
- 序列字符合法性（仅ACDEFGHIKLMNPQRSTVWY）

## 回退策略
- CAFA不可用：UniProtKB REST API
- UniProtKB不可用：TAIR、Pfam等替代源
- 所有源不可用：使用合成数据（需明确标注）

## 资源召回建议
- 数据集：`edge:resource:bio/datasets/bio-cafa-dataset`、`edge:resource:bio/datasets/bio-uniprotkb-reference`
- 组件：`edge:resource:bio/components/bio-go-ontology-validator`

## 证据来源
[1] Ramola et al., "On the state of protein function prediction: a report on the fourth CAFA challenge", bioRxiv, 2024, DOI: 10.64898/2026.05.06.722942
[2] UniProt Consortium, "UniProt: the Universal Protein Knowledgebase in 2023", Nucleic Acids Research, 2023, DOI: 10.1093/nar/gkac1052