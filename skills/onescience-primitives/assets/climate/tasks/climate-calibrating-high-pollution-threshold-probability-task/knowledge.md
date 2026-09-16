# 骨架任务：校准高污染阈值概率

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 执行“校准高污染阈值概率”，恢复物理量、坐标和元数据，生成逐时或逐日PM2.5浓度和超标概率及必要的质量标志。

## 执行 prompt（跨场景聚合去重）
- 依据{OUTPUT_FORMAT}、{OUTPUT_DIRECTORY}、{POSTPROCESS_CONFIG}、{DERIVED_PRODUCTS}完成校准高污染阈值概率，对核心结果执行已登记的校准、订正、派生或聚合并输出逐时或逐日PM2.5浓度和超标概率。核验单位、坐标、时次、无效值、物理范围和文件可读性；派生量必须记录公式和源变量。

## 输入槽（var/hint/default）
- {OUTPUT_FORMAT} | required=True | type=str | var_name=输出格式 | hint=输入输出文件格式。 | default=None
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果保存路径 | hint=输入结果保存路径。 | default=None
- {POSTPROCESS_CONFIG} | required=False | type=str | var_name=后处理配置 | hint=输入订正派生聚合配置。 | default=None
- {DERIVED_PRODUCTS} | required=False | type=str | var_name=派生产品 | hint=输入派生产品清单。 | default=None

## 产出
- 产品元数据与文件清单
- 质量标志与不确定性信息
- 逐时或逐日PM2.5浓度和超标概率

## 质量门禁 quality_gate
- 派生产品均有明确公式、源变量和质量标志
- 结果单位、坐标、有效时间和物理范围已核验
- 输出文件能够重新打开且变量和元数据完整
- 输出浓度或柱含量满足物理范围和掩膜约束

## 可调资源（edge:resource，仅真实存在）
- datasets/modis-myd13a3-ndvi-product
- datasets/smap-level-3-passive-soil-moisture-products
- datasets/snodas-swe-data-product
- models/ensemble-model-output-statistics-emos-post-processing
- models/matern-gaussian-process-regression

## 实例任务（本骨架在各场景的实例化）
- climate-calibrating-high-pollution-urban-station-pm25-short-inst

## 复用场景
- E42
