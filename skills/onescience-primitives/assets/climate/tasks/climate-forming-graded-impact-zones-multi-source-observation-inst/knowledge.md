# 实例任务：形成分级影响区 @ E92

- domain: climate
- 骨架: climate-forming-graded-impact-zones-task
- 场景: climate-multi-source-observation-and-weather-forecast-driven-dust-event-scenario (E92)
- step_id: s05
- depend: ['s04']

## 场景研究主体
- E92
- 关联论文: Deep multi-task learning for early warnings of dust events implemented for the Middle East | doi:

## 本实例步骤描述
执行“形成分级影响区”，恢复物理量、坐标和元数据，生成沙尘概率、浓度等级和影响区及必要的质量标志。

## 本实例执行 prompt
依据{OUTPUT_FORMAT}、{OUTPUT_DIRECTORY}、{POSTPROCESS_CONFIG}、{DERIVED_PRODUCTS}完成形成分级影响区，对核心结果执行已登记的校准、订正、派生或聚合并输出沙尘概率、浓度等级和影响区。核验单位、坐标、时次、无效值、物理范围和文件可读性；派生量必须记录公式和源变量。

## 本实例输入槽
- {OUTPUT_FORMAT} | required=True | type=str | var_name=输出格式 | hint=输入输出文件格式。 | default=None
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果保存路径 | hint=输入结果保存路径。 | default=None
- {POSTPROCESS_CONFIG} | required=False | type=str | var_name=后处理配置 | hint=输入订正派生聚合配置。 | default=None
- {DERIVED_PRODUCTS} | required=False | type=str | var_name=派生产品 | hint=输入派生产品清单。 | default=None

## 本实例产出
- 沙尘概率、浓度等级和影响区
- 质量标志与不确定性信息
- 产品元数据与文件清单

## 本实例质量门禁
- 输出文件能够重新打开且变量和元数据完整
- 结果单位、坐标、有效时间和物理范围已核验
- 派生产品均有明确公式、源变量和质量标志
- 预警阈值在独立验证集上冻结后评估

## 可调资源（edge:resource，仅真实存在）
- datasets/modis-myd13a3-ndvi-product
- datasets/smap-level-3-passive-soil-moisture-products
- datasets/snodas-swe-data-product
- models/ensemble-model-output-statistics-emos-post-processing
- models/matern-gaussian-process-regression

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
