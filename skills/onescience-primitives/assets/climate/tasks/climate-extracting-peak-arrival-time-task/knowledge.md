# 骨架任务：提取峰值和到时

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 执行“提取峰值和到时”，恢复物理量、坐标和元数据，生成增水时序、峰值及到时及必要的质量标志。

## 执行 prompt（跨场景聚合去重）
- 依据{OUTPUT_FORMAT}、{OUTPUT_DIRECTORY}、{POSTPROCESS_CONFIG}、{DERIVED_PRODUCTS}完成提取峰值和到时，对核心结果执行已登记的校准、订正、派生或聚合并输出增水时序、峰值及到时。核验单位、坐标、时次、无效值、物理范围和文件可读性；派生量必须记录公式和源变量。

## 输入槽（var/hint/default）
- {OUTPUT_FORMAT} | required=True | type=str | var_name=输出格式 | hint=输入输出文件格式。 | default=None
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果保存路径 | hint=输入结果保存路径。 | default=None
- {POSTPROCESS_CONFIG} | required=False | type=str | var_name=后处理配置 | hint=输入订正派生聚合配置。 | default=None
- {DERIVED_PRODUCTS} | required=False | type=str | var_name=派生产品 | hint=输入派生产品清单。 | default=None

## 产出
- 产品元数据与文件清单
- 增水时序、峰值及到时
- 质量标志与不确定性信息

## 质量门禁 quality_gate
- 派生产品均有明确公式、源变量和质量标志
- 结果单位、坐标、有效时间和物理范围已核验
- 输出文件能够重新打开且变量和元数据完整
- 预警阈值在独立验证集上冻结后评估

## 可调资源（edge:resource，仅真实存在）
- datasets/modis-myd13a3-ndvi-product
- datasets/smap-level-3-passive-soil-moisture-products
- datasets/snodas-swe-data-product
- models/ensemble-model-output-statistics-emos-post-processing
- models/matern-gaussian-process-regression

## 实例任务（本骨架在各场景的实例化）
- climate-extracting-peak-arrival-time-typhoon-and-pressure-wind-inst

## 复用场景
- E11
