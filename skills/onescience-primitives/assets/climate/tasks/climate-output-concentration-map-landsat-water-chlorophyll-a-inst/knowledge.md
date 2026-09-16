# 实例任务：输出浓度图、不确定性和适用域标志 @ E73

- domain: climate
- 骨架: climate-output-concentration-map-uncertainty-and-domain-flag-task
- 场景: climate-landsat-water-chlorophyll-a-probabilistic-retrieval-scenario (E73)
- step_id: s05
- depend: ['s04']

## 场景研究主体
- E73
- 关联论文: A Chlorophyll-a Algorithm for Landsat-8 Based on Mixture Density Networks | doi:

## 本实例步骤描述
执行“输出浓度图、不确定性和适用域标志”，恢复物理量、坐标和元数据，生成叶绿素a浓度、分位数及质量掩膜及必要的质量标志。

## 本实例执行 prompt
依据{OUTPUT_FORMAT}、{OUTPUT_DIRECTORY}、{POSTPROCESS_CONFIG}、{DERIVED_PRODUCTS}完成输出浓度图、不确定性和适用域标志，对核心结果执行已登记的校准、订正、派生或聚合并输出叶绿素a浓度、分位数及质量掩膜。核验单位、坐标、时次、无效值、物理范围和文件可读性；派生量必须记录公式和源变量。

## 本实例输入槽
- {OUTPUT_FORMAT} | required=True | type=str | var_name=输出格式 | hint=输入输出文件格式。 | default=None
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果保存路径 | hint=输入结果保存路径。 | default=None
- {POSTPROCESS_CONFIG} | required=False | type=str | var_name=后处理配置 | hint=输入订正派生聚合配置。 | default=None
- {DERIVED_PRODUCTS} | required=False | type=str | var_name=派生产品 | hint=输入派生产品清单。 | default=None

## 本实例产出
- 叶绿素a浓度、分位数及质量掩膜
- 质量标志与不确定性信息
- 产品元数据与文件清单

## 本实例质量门禁
- 输出文件能够重新打开且变量和元数据完整
- 结果单位、坐标、有效时间和物理范围已核验
- 派生产品均有明确公式、源变量和质量标志
- 输出坐标、分辨率、无效值和置信信息完整

## 可调资源（edge:resource，仅真实存在）
- datasets/modis-myd13a3-ndvi-product
- datasets/smap-level-3-passive-soil-moisture-products
- datasets/snodas-swe-data-product
- models/ensemble-model-output-statistics-emos-post-processing
- models/matern-gaussian-process-regression

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
