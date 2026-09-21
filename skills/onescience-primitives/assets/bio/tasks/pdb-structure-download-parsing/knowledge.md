# PDB Structure Download and Parsing

## 适用范围
Task for downloading and parsing protein structure files from RCSB Protein Data Bank (PDB) for structural biology analysis. Use this task when working with antibody-antigen complex structures, extracting atomic coordinates, identifying interface residues, or preparing structure-based features for computational modeling. Covers API access, file format handling, and coordinate extraction workflows.

## 输入
- **PDB IDs**: One or more PDB accession codes (e.g., 7BZ5, 1IGT)
- **Query parameters**: Organism, method, resolution range, molecule type
- **Format preferences**: PDB, mmCIF, or PDBx formats
- **Chain selection**: Specific antibody or antigen chains to extract

## 输出
- **Structure files**: Downloaded PDB/mmCIF files in local storage
- **Coordinate arrays**: Residue-level 3D coordinates (CA atoms, all atoms)
- **Chain information**: Chain IDs, residue numbers, sequence alignments
- **Interface data**: Contact residues, distance matrices, interaction maps

## 流程节点
1. **API query** → Construct RCSB REST API or FTP download requests
2. **File retrieval** → Download PDB/mmCIF files from RCSB servers
3. **Format parsing** → Parse structure files using BioPython, MDAnalysis, or similar
4. **Coordinate extraction** → Extract CA atom coordinates for residue-level representation
5. **Chain separation** → Separate antibody and antigen chains from complex
6. **Interface identification** → Calculate inter-chain contacts within distance cutoff
7. **Feature generation** → Compute distance matrices, contact maps, structural descriptors

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| RCSB REST API | https://data.rcsb.org/rest/v1/ | [1] | Primary data access endpoint |
| FTP download | ftp://ftp.wwpdb.org/pub/pdb/data/structures/ | [1] | Bulk file downloads |
| Interface cutoff | 5-8 Å | [1] | Distance threshold for contact definition |
| Resolution filter | <3.5 Å | [1] | Quality threshold for experimental structures |
| Coordinate format | PDB ATOM records | [1] | Standard structure file format |

## 边界与分流
- **Large structures**: Very large complexes may have partial coordinates; check completeness
- **Missing residues**: Some structures have missing loops or side chains; use PDBFixer for repair
- **Multiple models**: NMR structures have multiple models; select first or ensemble average
- **Modified residues**: Non-standard amino acids may not parse correctly; handle specially

## 质量检查
- Verify downloaded files are complete and not corrupted (file size, MD5 checksum)
- Check that all expected chains are present in the structure
- Validate coordinate ranges are within physical bounds (no extreme values)
- Confirm interface residues match expected binding site annotations

## 回退策略
- If RCSB API fails, use PDBe (European) or PDBj (Japanese) mirrors
- For missing structures, try AlphaFold Database for predicted structures
- For incomplete coordinates, use MODELLER or Rosetta for loop modeling
- For non-PDB formats, use conversion tools ( pdb4amber, gmx editconf)

## 资源召回建议
- When preparing structural features for antibody-antigen binding prediction
- When analyzing antibody-antigen complex geometries
- When building structure-based models for protein-protein interactions
- Pair with SAbDab for antibody-specific structure curation

## 证据来源
[1] Gaudreault F, Corbeil CR, Sulea T. Enhanced antibody-antigen structure prediction from molecular docking using AlphaFold2. Sci Rep. 2023;13:24090. doi:10.1038/s41598-023-42090-5