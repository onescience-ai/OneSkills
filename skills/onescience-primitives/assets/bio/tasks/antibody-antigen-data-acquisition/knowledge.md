# Antibody-Antigen Data Acquisition for Binding Site Prediction

## 适用范围
Task for acquiring high-quality antibody-antigen binding data from public repositories for computational immunology applications. Use this task when preparing datasets for antibody binding site prediction, affinity modeling, or structure-based design. Covers data sourcing from SAbDab, PDB, and other immunology databases with proper format conversion and quality control.

## 输入
- **Target organisms**: Human, mouse, rabbit, or other species
- **Antigen types**: Proteins, peptides, or other molecular targets
- **Data format preferences**: FASTA, PDB, or structured annotations
- **Quality thresholds**: Resolution limits, sequence completeness, binding affinity ranges

## 输出
- **FASTA file**: Formatted antibody-antigen sequences with headers
- **Annotation file**: Binding site labels, CDR regions, affinity data
- **Metadata**: PDB IDs, experimental methods, resolution, organism source
- **Quality report**: Dataset statistics, redundancy analysis, completeness check

## 流程节点
1. **Database selection** → Choose SAbDab (primary), PDB (complementary), or IMGT/IEDB (specialized)
2. **Query construction** → Define search criteria (species, antigen type, resolution, method)
3. **Data download** → Retrieve structures and sequences in bulk or individual queries
4. **Format parsing** → Convert PDB/mmCIF to FASTA, extract chain information
5. **Quality filtering** → Remove incomplete structures, low-resolution entries, redundant sequences
6. **Annotation extraction** → Identify CDR regions, binding site residues, affinity values
7. **Dataset assembly** → Combine sequences, structures, and annotations into standardized format
8. **Validation** → Verify data integrity, check for missing values, confirm annotation accuracy

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| SAbDab entry count | >12,000 structures | [2] | Primary antibody structure database |
| PDB resolution cutoff | <3.5 Å | [2] | Typical quality threshold for structural data |
| Sequence identity filter | <90% for training | [2] | Reduces redundancy in training set |
| Binding site definition | Within 5 Å of antigen | [1] | Standard interface distance cutoff |
| CDR numbering | IMGT or Chothia | [2] | Standard antibody numbering schemes |

## 边界与分流
- **Incomplete data**: Some PDB entries lack full CDR annotations; use ANARCI for completion
- **Redundancy**: Highly similar sequences bias models; apply sequence clustering (CD-HIT, MMseqs2)
- **Missing affinity**: Not all complexes have measured binding affinities; use structural binding site labels
- **Resolution limits**: High-resolution structures preferred but limited availability; balance quality vs. quantity

## 质量检查
- Verify FASTA headers contain required metadata (PDB ID, chain, organism)
- Check binding site annotations match structural interface definitions
- Validate CDR assignments using ANARCI with chosen numbering scheme
- Assess dataset balance across antigen families and binding affinities

## 回退策略
- If SAbDab unavailable, use PDB advanced search with antibody-specific filters
- For non-protein antigens, use IEDB or specialized glycan databases
- For sequence-only data without structures, use IMGT/LIGM-DB or abYsis
- Consider synthetic data generation if real data insufficient (with appropriate caveats)

## 资源召回建议
- When preparing data for antibody-antigen binding prediction models
- When benchmarking antibody structure prediction methods
- When designing antibody engineering experiments requiring training data
- Pair with ANARCI for CDR annotation and PDB tools for structure parsing

## 证据来源
[1] Ye C, Hu W, Gaeta B. Prediction of Antibody-Antigen Binding via Machine Learning: Development of Data Sets and Evaluation of Methods. JMIR Bioinform Biotechnol. 2022;3(1):e29404. doi:10.2196/29404
[2] Jeon W, Kim D. AbFlex: designing antibody complementarity determining regions with flexible CDR definition. Bioinformatics. 2024;40(3):btae122. doi:10.1093/bioinformatics/btae122