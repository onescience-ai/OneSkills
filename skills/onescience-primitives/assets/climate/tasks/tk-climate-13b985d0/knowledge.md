# 骨架任务：概率校准与短临产品生成

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 计算雨强超阈概率和集合统计，并在独立校准资料可用时执行概率校准。

## 执行 prompt（跨场景聚合去重）
- 依据{RAIN_RATE_THRESHOLDS}计算各时效的超阈概率、集合均值和分位数。若{CALIBRATION_MODE}为independent_validation_calibration，必须使用{CALIBRATION_REFERENCE}拟合并记录校准映射；否则把产品明确标记为未校准。按{OUTPUT_FORMAT}写入{OUTPUT_DIRECTORY}并保存完整元数据。

## 输入槽（var/hint/default）
- {CALIBRATION_REFERENCE} | required=False | type=str | var_name=独立校准资料 | hint=输入校准资料路径。 | default=None
- {CALIBRATION_MODE} | required=True | type=str | var_name=概率校准模式 | hint=输入校准方式或不校准。 | default=None
- {RAIN_RATE_THRESHOLDS} | required=True | type=str | var_name=雨强阈值 | hint=输入雨强阈值，逗号分隔。 | default=None
- {OUTPUT_FORMAT} | required=True | type=str | var_name=输出格式 | hint=输入NetCDF或Zarr。 | default=None
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果保存路径 | hint=输入预报结果保存路径。 | default=None

## 产出
- 产品元数据与文件清单
- 概率校准记录或未校准标识
- 逐阈值逐时效超阈概率
- 降水率集合成员或集合统计

## 质量门禁 quality_gate
- 校准资料与训练及最终测试资料相互独立
- 概率值位于0到1且随阈值变化不存在逻辑矛盾
- 模型、检查点、随机种子和校准版本可追溯
- 没有校准证据时未将原始生成集合声称为已校准概率预报
- 输出文件能够重新打开且坐标、单位、时效和成员维完整

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-3a00af6f

## 复用场景
- E2
