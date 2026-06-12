# Biology Domain Knowledge

| 字段 | 摘要 |
| --- | --- |
| 适用领域 | 生信、生命科学、蛋白、基因组、单细胞和生物图像论文。 |
| 召回信号 | biology、genomics、protein、sequence、MSA、structure、ligand、cell、expression matrix、AnnData、microscopy、WSI。 |
| 核心用途 | 提示序列/结构/表达矩阵/图像/样本划分/数据泄漏/生物指标的提取与审计。 |
| 注意事项 | 只作为检查清单；只有论文或用户材料出现的内容才能写成确定要求。 |

用于生信、生命科学、蛋白、基因组、单细胞和生物图像论文的提取提示。这里只提供检查清单，不提供论文事实。

## 常见数据对象

- sequence、token、MSA、structure、atom/residue graph、ligand、complex。
- expression matrix、AnnData、sample metadata、cell type labels。
- microscopy image、WSI tile、mask、flow cytometry table。
- train/test split by homology、family、species、time、patient、batch。

## 提取时重点检查

- tokenization、masking、padding、chain/complex organization 和 residue/atom indexing 要写清。
- 输入模态与输出目标分开：sequence、structure、graph、expression、image、label、score。
- 数据泄漏风险必须检查：homologous sequences、similar structures、patient/sample overlap、batch leakage。
- loss target 和 evaluation target 要分清，例如 perplexity、structure coordinates、distance map、classification label。
- 生物实验或临床语义如果需要人工审核，写入缺口或风险，不写成自动结论。

## 常见评估提示

- AUC、F1、accuracy、perplexity、AUROC/AUPRC。
- RMSD、TM-score、lDDT、DockQ、contact precision。
- clustering/label transfer scores、DE consistency、segmentation IoU/Dice。

只有论文实际出现或用户材料提供的指标才能写成确定评估要求。
