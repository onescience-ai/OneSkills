# 骨架任务：物理量恢复与产品生成

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 执行反标准化、单位恢复和必要的网格转换，生成带完整时空坐标与版本元数据的多变量产品。

## 执行 prompt（跨场景聚合去重）
- 将预报序列反标准化并恢复物理单位，按{OUTPUT_GRID}和{OUTPUT_FORMAT}写入{OUTPUT_DIRECTORY}。仅生成可由现有变量和明确公式得到的{DERIVED_PRODUCTS}，同时写入起报时间、有效时间、模型、检查点、配置、变量、单位和处理历史。

## 输入槽（var/hint/default）
- {OUTPUT_GRID} | required=True | type=str | var_name=交付网格 | hint=输入目标网格。 | default=None
- {OUTPUT_FORMAT} | required=True | type=str | var_name=输出格式 | hint=输入NetCDF、Zarr或GRIB2。 | default=None
- {DERIVED_PRODUCTS} | required=False | type=str | var_name=派生产品 | hint=输入派生产品，逗号分隔。 | default=None
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果保存路径 | hint=输入预报结果保存路径。 | default=None

## 产出
- 产品元数据与文件清单
- 全球多层多变量确定性预报场
- 经明确配置的派生产品

## 质量门禁 quality_gate
- 反标准化参数与输入预处理版本严格对应
- 变量单位、物理范围、坐标、日历和有效时间已核验
- 派生变量均有明确公式和源变量
- 输出文件能够重新打开且维度、变量和元数据完整

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-6ff1e69b

## 复用场景
- E1
