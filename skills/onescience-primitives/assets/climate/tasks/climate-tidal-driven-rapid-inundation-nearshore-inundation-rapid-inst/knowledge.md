# 实例任务：沿岸潮位驱动的快速淹没产品生成 @ E109

- domain: climate
- 骨架: climate-tidal-driven-rapid-inundation-product-task
- 场景: climate-nearshore-inundation-rapid-forecast-model-scenario (E109)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E109
- 关联论文: （源场景未提供）

## 本实例步骤描述
将预测沿岸潮位转换为符合s02冻结物理定义的近岸淹没分布和受影响行政区划。

## 本实例执行 prompt
仅在s02任务配置冻结门禁和s03数据与干运行门禁均通过后执行；否则停止并标记BLOCKED。执行前核验本步骤全部输入值或路径已提供；对文件和数据类输入，核验其实际存在、可读、获准使用且与s03冻结的数据契约一致，并记录版本与校验信息；缺失或不一致时停止并标记BLOCKED。按s02冻结方案处理{TARGET_WATER_LEVEL_CYCLE}，生成淹没分布图和受影响行政区划至{OUTPUT_DIRECTORY}，记录潮位批次、地形与防护版本、模型配置和日志。

## 本实例输入槽
- {TARGET_WATER_LEVEL_CYCLE} | required=True | type=str | var_name=目标潮位批次 | hint=输入本次潮位产品路径。 | default=None
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果输出目录 | hint=输入产品输出目录。 | default=None

## 本实例产出
- 漫滩快速预报模型与配置
- 淹没分布图和行政区划清单
- 输入版本、运行日志和产品清单

## 本实例质量门禁
- 任务范围和漫滩产品定义已经冻结
- 潮位、高程、岸线、防护工程和行政边界基准一致
- 淹没产品空间参考、有效时间和质量标志完整
- 完整流程计时包括数据读取、模拟、制图和行政区划叠加

## 可调资源（edge:resource，仅真实存在）
- datasets/gtws-mlrec-machine-learning-based-global-terrestrial-water-storage-anomaly-reconstruction-dataset-and-workflow
- datasets/smap-level-3-passive-soil-moisture-products
- models/1d-cnn-based-groundwater-level-prediction
- models/ensemble-model-output-statistics-emos-post-processing
- tools/multi-level-b-spline-analysis-mba

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
