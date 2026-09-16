# 实例任务：物理量恢复与产品生成 @ E1

- domain: climate
- 骨架: climate-physical-quantity-recovery-product-generation-task
- 场景: climate-global-analysis-driven-1-10-day-multivariate-deterministic-scenario (E1)
- step_id: s05
- depend: ['s04']

## 场景研究主体
- E1
- 关联论文: Learning skillful medium-range global weather forecasting | doi:; Accurate medium-range global weather forecasting with 3D neural networks | doi:; FourCastNet: A Global Data-driven High-resolution Weather Model using Adaptive Fourier Neural Operators | doi:; FengWu: Pushing the Skillful Global Medium-range Weather Forecast beyond 10 Days Lead | doi:; AIFS -- ECMWF's data-driven forecasting system | doi:

## 本实例步骤描述
执行反标准化、单位恢复和必要的网格转换，生成带完整时空坐标与版本元数据的多变量产品。

## 本实例执行 prompt
将预报序列反标准化并恢复物理单位，按{OUTPUT_GRID}和{OUTPUT_FORMAT}写入{OUTPUT_DIRECTORY}。仅生成可由现有变量和明确公式得到的{DERIVED_PRODUCTS}，同时写入起报时间、有效时间、模型、检查点、配置、变量、单位和处理历史。

## 本实例输入槽
- {OUTPUT_GRID} | required=True | type=str | var_name=交付网格 | hint=输入目标网格。 | default=None
- {OUTPUT_FORMAT} | required=True | type=str | var_name=输出格式 | hint=输入NetCDF、Zarr或GRIB2。 | default=None
- {DERIVED_PRODUCTS} | required=False | type=str | var_name=派生产品 | hint=输入派生产品，逗号分隔。 | default=None
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果保存路径 | hint=输入预报结果保存路径。 | default=None

## 本实例产出
- 全球多层多变量确定性预报场
- 经明确配置的派生产品
- 产品元数据与文件清单

## 本实例质量门禁
- 反标准化参数与输入预处理版本严格对应
- 变量单位、物理范围、坐标、日历和有效时间已核验
- 输出文件能够重新打开且维度、变量和元数据完整
- 派生变量均有明确公式和源变量

## 可调资源（edge:resource，仅真实存在）
- datasets/modis-myd13a3-ndvi-product
- datasets/smap-level-3-passive-soil-moisture-products
- datasets/snodas-swe-data-product
- models/ensemble-model-output-statistics-emos-post-processing

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
