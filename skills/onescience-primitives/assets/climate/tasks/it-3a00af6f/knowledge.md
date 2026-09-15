# 实例任务：概率校准与短临产品生成 @ E2

- domain: climate
- 骨架: tk-climate-13b985d0
- 场景: sc-16d509a7 (E2)
- step_id: s05
- depend: ['s04']

## 场景研究主体
- E2
- 关联论文: Skilful nowcasting of extreme precipitation with NowcastNet | doi:; Skilful precipitation nowcasting using deep generative models of radar | doi:; Convolutional LSTM Network: A Machine Learning Approach for Precipitation Nowcasting | doi:; RainNet v1.0: a convolutional neural network for radar-based precipitation nowcasting | doi:

## 本实例步骤描述
计算雨强超阈概率和集合统计，并在独立校准资料可用时执行概率校准。

## 本实例执行 prompt
依据{RAIN_RATE_THRESHOLDS}计算各时效的超阈概率、集合均值和分位数。若{CALIBRATION_MODE}为independent_validation_calibration，必须使用{CALIBRATION_REFERENCE}拟合并记录校准映射；否则把产品明确标记为未校准。按{OUTPUT_FORMAT}写入{OUTPUT_DIRECTORY}并保存完整元数据。

## 本实例输入槽
- {CALIBRATION_REFERENCE} | required=False | type=str | var_name=独立校准资料 | hint=输入校准资料路径。 | default=None
- {CALIBRATION_MODE} | required=True | type=str | var_name=概率校准模式 | hint=输入校准方式或不校准。 | default=None
- {RAIN_RATE_THRESHOLDS} | required=True | type=str | var_name=雨强阈值 | hint=输入雨强阈值，逗号分隔。 | default=None
- {OUTPUT_FORMAT} | required=True | type=str | var_name=输出格式 | hint=输入NetCDF或Zarr。 | default=None
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果保存路径 | hint=输入预报结果保存路径。 | default=None

## 本实例产出
- 降水率集合成员或集合统计
- 逐阈值逐时效超阈概率
- 概率校准记录或未校准标识
- 产品元数据与文件清单

## 本实例质量门禁
- 概率值位于0到1且随阈值变化不存在逻辑矛盾
- 校准资料与训练及最终测试资料相互独立
- 没有校准证据时未将原始生成集合声称为已校准概率预报
- 输出文件能够重新打开且坐标、单位、时效和成员维完整
- 模型、检查点、随机种子和校准版本可追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
