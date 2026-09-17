# Gene Ontology标签验证器

## 适用范围
- **触发条件**：需要验证GO标签的唯一性、正确性和一致性
- **适用场景**：蛋白质功能预测数据准备、标签质量控制、去重
- **不适用场景**：已有验证标签、仅需格式检查

## 输入
- 待验证的GO标签列表（GO ID + 功能描述）
- 可选：Gene Ontology OBO文件（go-basic.obo）
- 可选：UniProtKB注释文件

## 输出
- 验证报告：唯一性、冗余检测、与官方一致性
- 清洗后的GO标签列表
- 冲突解决记录

## 验证规则

### 规则1：GO ID格式验证
```python
import re
pattern = r"^GO:\d{7}$"
def validate_go_id(go_id):
    return bool(re.match(pattern, go_id))
```

### 规则2：功能描述唯一性
```python
def check_unique_descriptions(go_list):
    desc_to_go = {}
    duplicates = []
    for go_id, desc in go_list:
        if desc in desc_to_go:
            duplicates.append((go_id, desc_to_go[desc], go_id))
        else:
            desc_to_go[desc] = go_id
    return duplicates
```

### 规则3：OBO文件验证
```python
# 下载go-basic.obo
# https://purl.obolibrary.org/obo/go-basic.obo
def validate_against_obo(go_id, obo_terms):
    return go_id in obo_terms
```

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| go_id_pattern | ^GO:\d{7}$ | [Gene Ontology] | 标准格式 |
| obo_source | go-basic.obo | [Gene Ontology] | 官方本体 |
| namespaces | BP, MF, CC | [Gene Ontology] | 命名空间 |

## 边界与分流
- OBO文件不可用：使用REST API在线验证
- GO ID不存在：记录并标记为无效
- 功能描述重复：保留证据代码更高级的GO ID

## 质量检查
- 所有GO ID格式正确
- 无重复功能描述
- 所有GO ID在官方OBO中存在

## 证据来源
[1] Zhang et al., "GOBoost: leveraging long-tail Gene Ontology terms for accurate protein function prediction", Bioinformatics, 2025, DOI: 10.1093/bioinformatics/btaf267