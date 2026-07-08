# architecture_overview

该应用卡以查询模板为核心，负责把公共知识库需求转为结构化 query handoff。任务必须区分 database family、query terms、identifier type、species/taxon、release/date、return fields、evidence type 和 output format；需要实际联网时由执行层按权限处理。

# parameter_scale

非模型原语。规模由 query term 数、数据库数量、返回字段和 evidence record 数决定。

# architecture_structure

- `omics_database_query.yaml`：记录 PRIDE、PeptideAtlas、MassIVE、ProteomeXchange、HMDB、Metabolomics Workbench 等蛋白质组/代谢组查询字段，也可作为 literature-sequence、pathway-ppi、single-cell-atlas、structure-compound、variant-clinical 等数据库请求的通用字段起点。
- `regulatory_query.yaml`：记录 ENCODE、ReMap、Cistrome、JASPAR、RegulomeDB、Roadmap、UCSC track 等调控注释查询字段。
- 其他数据库家族通过 `database_family`、`databases`、`identifier_type`、`evidence_fields`、`return_fields` 和 `output_format` 扩展，不要求新增应用卡格式。

# input_schema

输入包括 database_family、query_terms、identifier_type、species_or_taxon、release_or_date、return_fields、output_format 和证据整理要求。文献/序列任务需记录 PubMed、NCBI、ENA、UniProt、Ensembl、BioProject、BioSample、accession 和下载对象；通路/PPI 任务需记录 GO、KEGG、Reactome、WikiPathways、STRING、BRENDA、QuickGO、background set 和 evidence type；蛋白质组/代谢组任务需区分 dataset、raw files、mzML、peptide evidence、protein inference、metabolite spectral match；调控注释任务需显式给出 genome build、region/gene、cell type、assay、TF/motif 或 track；单细胞图谱任务需记录 species、tissue、technology、reference、cell ontology 和 license；结构/化合物任务需记录 PDB/EMDB/AlphaFold DB、PubChem、ChEMBL、DrugBank、ZINC、OpenTargets、structure resolution、assay condition 和 activity field；变异/临床任务需记录 HGVS/rsID/VCF coordinate、reference build、transcript、ClinVar、gnomAD、dbSNP、COSMIC、cBioPortal、DepMap、GWAS Catalog 或 Monarch。

# output_schema

输出为结构化 YAML query、字段映射、证据表需求、下载计划、候选数据库列表和下游执行 handoff。

# shape_transformations

natural language query
  -> database family routing
  -> structured query YAML
  -> evidence table schema

# key_dependencies

- 数据库名称和 release/date。
- identifier 类型、物种和 genome build。
- 返回字段、证据强度、identification level、ontology/release 和访问权限。

# common_modification_points

- 新增 database family。
- 扩展返回字段、过滤条件和证据等级。
- 增加 accession 映射、background set、reference candidates、compound activity、variant conflict handling 等家族特异字段。
- 增加 API/client 执行脚本。

# implementation_risks

- 不可把模板生成等同于已经完成数据库检索。
- 不可忽略 release/date、genome build 和 identifier 类型。
- 不可把 motif hit 当成实际 TF binding 证据。
- 不可把谱库匹配等同于已确认代谢物身份。
- 不可在同名基因或 accession 未限定物种/版本时直接给结论。
- 不可把 PPI 数据库边、AlphaFold DB 预测结构、docking pose 或数据库临床注释直接当成已验证因果/诊断证据。
- 不可忽略 reference build、transcript、cell ontology、assay 条件、database release 或受控访问限制。

# code_references

- primitive 模板目录：`assets/bio_knowledge_query_app/script/bio_knowledge_templates/`
- 语义来源标签：`knowledge-databases`
- 语义来源标签：`literature-sequence-search`
- 语义来源标签：`pathway-ppi-databases`
- 语义来源标签：`proteomics-metabolomics-databases`
- 语义来源标签：`regulatory-annotation-databases`
- 语义来源标签：`single-cell-atlas-databases`
- 语义来源标签：`structure-compound-databases`
- 语义来源标签：`variant-clinical-databases`
