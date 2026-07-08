# launch

该卡以模板启用为主：

```sh
cp script/bio_knowledge_templates/omics_database_query.yaml ./omics_database_query.yaml
```

# input_schema

必须填写数据库家族、查询词、标识符类型、物种、版本或日期、返回字段、证据类型和输出格式。实际查询前需要确认是否允许联网、访问本地数据库镜像或使用受控访问数据。

# runtime_interfaces

- 模板入口：`omics_database_query.yaml`、`regulatory_query.yaml`
- 适用任务标签：`literature-sequence-search`、`pathway-ppi-databases`、`proteomics-metabolomics-databases`、`regulatory-annotation-databases`、`single-cell-atlas-databases`、`structure-compound-databases`、`variant-clinical-databases`
- execution_kind：template_only

# main_functions

- emit omics database query
- emit regulatory annotation query
- emit literature/sequence query
- emit pathway/PPI query
- emit atlas, structure/compound, and variant/clinical query fields
- define evidence fields

# execution_resources

模板生成无需计算资源；实际联网查询需要网络权限、API key 或本地数据库镜像。

# operation_limits

该卡不执行联网检索，不保证数据库当前可用性，不替代人工证据审核、临床判断或结构/化合物实验验证。
