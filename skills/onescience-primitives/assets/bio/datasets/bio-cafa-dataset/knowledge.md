# CAFA Challenge数据集

## 适用范围
- **触发条件**：需要蛋白质功能预测标准基准数据集
- **适用场景**：CAFA挑战赛评估、模型性能对比、few-shot蛋白功能预测
- **不适用场景**：特定物种专有数据、非GO标注数据

## 输入
- 物种范围：CAFA1/2/3/4涵盖细菌、古菌、真核生物
- GO命名空间：BP（Biological Process）、MF（Molecular Function）、CC（Cellular Component）
- 注释证据代码：IDA、IEA、IBA、IMP等

## 输出
- 蛋白质序列文件（FASTA格式）
- GO注释文件（TSV/CSV格式）
- 数据统计：样本量、类别分布、序列长度

## 数据格式规范

### 序列文件
```
>protein_id
MKWVTFISLLFLFSSAYSRGVFRRDAHKSEVAHRFKDLGEENFKALVLIAFAQYLQQCPFEDHVKLVNEVTEFAKTCVADESAENCDKS
```

### 注释文件
```
protein_id	go_id	namespace	evidence_code
P12345	GO:0005737	CC	IEA
P12345	GO:0006915	BP	IDA
```

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| cafa_version | CAFA4 | [CAFA4] | 最新挑战赛版本 |
| species | bacteria, archaea, eukaryota | [CAFA4] | 覆盖物种 |
| namespaces | BP, MF, CC | [CAFA4] | 三个命名空间 |
| evidence_codes | IDA, IEA, IBA, IMP | [CAFA4] | 注释证据代码 |
| sequence_length | 50-3000 aa | [统计] | 序列长度范围 |

## 数据获取方式
- CAFA官网：https://cafa.ai/
- UniProtKB REST API：https://rest.uniprot.org/
- 批量下载：FTP站点或REST API分页

## 质量检查
- 序列字符合法性（ACDEFGHIKLMNPQRSTVWY）
- GO ID格式正确（GO:XXXXXXXX）
- 标签唯一性验证
- 无空值或缺失

## 证据来源
[1] Ramola et al., "On the state of protein function prediction: a report on the fourth CAFA challenge", bioRxiv, 2024, DOI: 10.64898/2026.05.06.722942