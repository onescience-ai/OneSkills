# UniProtKB参考数据集

## 适用范围
- **触发条件**：需要蛋白质功能注释的权威参考数据
- **适用场景**：GO标签验证、参考标签映射、跨家族泛化评估
- **不适用场景**：仅需序列数据、非GO注释

## 输入
- UniProtKB accession IDs或蛋白名称
- 查询范围：特定物种或全库
- 注释类型：GO terms、EC numbers、Pfam domains

## 输出
- 蛋白质序列（FASTA格式）
- GO注释列表
- 参考标签映射文件（reference_label_mapping.json）

## 数据获取方式

### REST API
```python
import requests
# 单个蛋白查询
url = "https://rest.uniprot.org/uniprotkb/P12345.json"
response = requests.get(url)
data = response.json()

# GO注释提取
go_terms = [ref["id"] for ref in data.get("uniProtKBCrossReferences", [])
            if ref["database"] == "GO"]
```

### 批量下载
```bash
# FTP下载完整数据集
wget ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.gz
```

## 注释字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| GO terms | Gene Ontology功能标签 | GO:0005737 |
| EC numbers | 酶分类编号 | EC:2.7.11.1 |
| Pfam domains | 蛋白质结构域 | PF00069 |
| Evidence codes | 注释证据代码 | IDA, IEA, IBA |

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| api_endpoint | https://rest.uniprot.org/ | [UniProt] | REST API地址 |
| go_namespaces | BP, MF, CC | [Gene Ontology] | 三个命名空间 |
| evidence_codes | IDA, IEA, IBA, IMP | [UniProtKB] | 可接受证据代码 |
| batch_size | 25 | [UniProt] | API批量查询大小 |

## 边界与分流
- API不可用：使用FTP批量下载
- 注释缺失：记录并标记为PARTIAL
- 版本不匹配：使用UniProtKB_2025_01或指定版本

## 质量检查
- GO ID格式正确（GO:XXXXXXXX）
- 注释来源可追溯
- 无重复注释

## 证据来源
[1] UniProt Consortium, "UniProt: the Universal Protein Knowledgebase in 2023", Nucleic Acids Research, 2023, DOI: 10.1093/nar/gkac1052