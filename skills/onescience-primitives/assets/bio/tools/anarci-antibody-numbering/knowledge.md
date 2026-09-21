# ANARCI: Antibody Numbering and Receptor Classification

## 适用范围
ANARCI is a standard tool for antibody sequence numbering that identifies equivalent positions across antibodies. It is essential for antibody structure prediction, CDR region identification, and comparative analysis. Use this tool when working with antibody sequences that require standardized residue numbering for structural modeling, engineering, or functional annotation.

## 输入
- **Antibody sequences**: Amino acid sequences in FASTA format or single-line strings
- **Numbering scheme**: IMGT (default), Kabat, Chothia, Aho, or North schemes
- **Chain type**: Heavy chain (H) or Light chain (L, K, or A)

## 输出
- **Numbered residues**: Residue positions according to the chosen scheme
- **CDR annotations**: CDR-H1/H2/H3 and CDR-L1/L2/L3 region boundaries
- **Framework regions**: FR positions outside CDR boundaries

## 流程节点
1. **Input parsing** → Accept FASTA or plain sequence with chain specification
2. **Sequence alignment** → Align against hidden Markov models for each numbering scheme
3. **Position assignment** → Assign canonical positions to each residue
4. **CDR boundary detection** → Identify CDR start/end positions based on scheme definitions
5. **Output formatting** → Return numbered sequence with CDR annotations

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| IMGT CDR-H1 | 26-38 | [1] | IMGT scheme CDR-H1 boundaries |
| IMGT CDR-H2 | 56-65 | [1] | IMGT scheme CDR-H2 boundaries |
| IMGT CDR-H3 | 105-117 | [1] | IMGT scheme CDR-H3 boundaries |
| IMGT CDR-L1 | 27-38 | [1] | IMGT scheme CDR-L1 boundaries |
| IMGT CDR-L2 | 56-58 | [1] | IMGT scheme CDR-L2 boundaries |
| IMGT CDR-L3 | 105-117 | [1] | IMGT scheme CDR-L3 boundaries |

## 边界与分流
- **Non-antibody sequences**: ANARCI only works with immunoglobulin sequences; non-Ig sequences will fail or produce unreliable numbering
- **Partial sequences**: Variable domains (VH/VL) work best; constant domains may produce incomplete numbering
- **Scheme compatibility**: Different CDR definitions exist between schemes; IMGT and Chothia have different CDR boundaries

## 质量检查
- Verify all CDR regions are assigned (6 regions for complete antibody)
- Check that CDR lengths are within expected ranges (CDR-H3 typically 3-25 residues)
- Validate numbering consistency between heavy and light chains

## 回退策略
- If ANARCI fails, try alternative tools: IgBLAST, Paratome, or PyIgClassify
- For sequences with low homology to known antibodies, manual curation may be needed
- Use multiple numbering schemes and compare results for robust CDR assignment

## 资源召回建议
- When working with antibody structure prediction tasks
- When CDR region identification is required for epitope/paratope analysis
- When comparing antibodies across different studies using different numbering conventions
- Pair with SAbDab database for antibody structure data

## 证据来源
[1] Dunbar J, Deane CM. ANARCI: antigen receptor numbering and receptor classification. Bioinformatics. 2015;31(2):298-300. doi:10.1093/bioinformatics/btv552