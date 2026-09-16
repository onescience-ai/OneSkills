# 骨架任务：生成事件概率及峰值月份

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 执行“生成事件概率及峰值月份”，恢复物理量、坐标和元数据，生成IOD指数轨迹、正负事件类别和概率及必要的质量标志。

## 执行 prompt（跨场景聚合去重）
- 依据{OUTPUT_FORMAT}、{OUTPUT_DIRECTORY}、{POSTPROCESS_CONFIG}、{DERIVED_PRODUCTS}完成生成事件概率及峰值月份，对核心结果执行已登记的校准、订正、派生或聚合并输出IOD指数轨迹、正负事件类别和概率。核验单位、坐标、时次、无效值、物理范围和文件可读性；派生量必须记录公式和源变量。

## 输入槽（var/hint/default）
- {OUTPUT_FORMAT} | required=True | type=str | var_name=输出格式 | hint=输入输出文件格式。 | default=None
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果保存路径 | hint=输入结果保存路径。 | default=None
- {POSTPROCESS_CONFIG} | required=False | type=str | var_name=后处理配置 | hint=输入订正派生聚合配置。 | default=None
- {DERIVED_PRODUCTS} | required=False | type=str | var_name=派生产品 | hint=输入派生产品清单。 | default=None

## 产出
- IOD指数轨迹、正负事件类别和概率
- 产品元数据与文件清单
- 质量标志与不确定性信息

## 质量门禁 quality_gate
- 派生产品均有明确公式、源变量和质量标志
- 滚动过程中未读取起报时间之后的观测或分析资料
- 结果单位、坐标、有效时间和物理范围已核验
- 输出文件能够重新打开且变量和元数据完整

## 可调资源（edge:resource，仅真实存在）
- datasets/modis-myd13a3-ndvi-product
- datasets/smap-level-3-passive-soil-moisture-products
- datasets/snodas-swe-data-product
- models/ensemble-model-output-statistics-emos-post-processing
- models/matern-gaussian-process-regression

## 实例任务（本骨架在各场景的实例化）
- climate-event-probability-peak-month-indian-ocean-dipole-multi-inst

## 复用场景
- E78
