# Gene Ontology标签验证

## 适用范围
- **触发条件**：需要验证GO标签的唯一性、正确性和与官方本体的一致性
- **适用场景**：蛋白质功能预测数据准备、GO注释质量控制、标签去重
- **不适用场景**：已有经过验证的GO标签、仅需简单格式检查

## 输入
- 待验证的GO标签列表（GO ID + 功能描述）
- 可选：Gene Ontology OBO文件（go-basic.obo）
- 可选：UniProtKB注释文件

## 输出
- 验证报告：唯一性、冗余检测、与官方一致性
- 清洗后的GO标签列表
- 冲突解决记录

## 流程节点

### 节点1：GO ID格式验证
**操作**：检查GO ID格式（GO:XXXXXXXX）
**参数**：正则表达式 ^GO:\d{7}$
**工具**：Python re模块
**质量门禁**：所有GO ID格式正确

### 节点2：功能描述唯一性检查
**操作**：检测同一功能描述对应多个GO ID
**参数**：去重粒度（精确匹配/模糊匹配）
**工具**：pandas/dict
**质量门禁**：无重复功能描述

### 节点3：官方OBO文件验证
**操作**：对比GO ID是否在官方OBO文件中存在
**参数**：OBO文件路径
**工具**：oboparser/go-basic.obo
**质量门禁**：所有GO ID在官方本体中存在

### 节点4：命名空间验证
**操作**：检查GO ID所属命名空间（BP/MF/CC）
**参数**：期望命名空间
**工具**：Gene Ontology API
**质量门禁**：GO ID命名空间与任务要求一致

### 节点5：层级关系验证
**操作**：检查GO ID的is_a关系和层级深度
**参数**：最小/最大层级深度
**工具**：NetworkX + OBO解析
**质量门禁**：无循环引用、层级合理

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| go_id_pattern | ^GO:\d{7}$ | [Gene Ontology] | 标准GO ID格式 |
| obo_source | go-basic.obo | [Gene Ontology] | 官方本体文件 |
| namespaces | BP, MF, CC | [Gene Ontology] | 三个命名空间 |
| evidence_codes | IEA, IDA, IBA, IMP | [UniProtKB] | 可接受的证据代码 |

## 边界与分流
- OBO文件不可用：使用Gene Ontology REST API在线验证
- GO ID不存在：记录并标记为无效
- 功能描述重复：保留证据代码更高级的GO ID
- 命名空间不匹配：根据任务要求过滤

## 质量检查
- 所有GO ID格式正确（GO:XXXXXXXX）
- 无重复功能描述
- 所有GO ID在官方OBO文件中存在
- 命名空间与任务要求一致

## 回退策略
- OBO文件不可用：Gene Ontology REST API
- API不可用：使用本地缓存的OBO文件
- 验证失败：记录问题但继续执行（标记为PARTIAL）

## 资源召回建议
- 组件：`edge:resource:bio/components/bio-go-ontology-validator`
- 数据集：`edge:resource:bio/datasets/bio-uniprotkb-reference`

## 证据来源
[1] UniProt Consortium, "UniProt: the Universal Protein Knowledgebase in 2023", Nucleic Acids Research, 2023, DOI: 10.1093/nar/gkac1052
[2] Zhang et al., "GOBoost: leveraging long-tail Gene Ontology terms for accurate protein function prediction", Bioinformatics, 2025, DOI: 10.1093/bioinformatics/btaf267