# 实例任务：源观测和参考资料及任务边界预检 @ E21

- domain: climate
- 骨架: tk-climate-9558a47e
- 场景: sc-61b5e0f0 (E21)
- step_id: s01
- depend: []

## 场景研究主体
- E21
- 关联论文: A Deep Learning Multimodal Method for Precipitation Estimation | doi:; Ground radar precipitation estimation with deep learning approaches in meteorological private cloud | doi:; RainForest- a random forest algorithm for quantitative precipitation estimation over Switzerland | doi:; Improving near real-time precipitation estimation using a U-Net convolutional neural network and geographical information | doi:

## 本实例步骤描述
界定“雷达—卫星—雨量计多模态同期定量降水估计”的任务范围并执行“源观测和参考资料及任务边界预检”，核验雷达观测、卫星云图、雨量计及地理特征的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“雷达—卫星—雨量计多模态同期定量降水估计”，读取{RADAR_VOLUME}、{SATELLITE_OBSERVATIONS}、{RAIN_GAUGE_DATA}、{TARGET_PERIOD}、{DATA_CUTOFF_TIME}并完成源观测和参考资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {RADAR_VOLUME} | required=True | type=str | var_name=雷达体扫资料 | hint=输入雷达体扫资料路径。 | default=None
- {SATELLITE_OBSERVATIONS} | required=True | type=str | var_name=卫星观测资料 | hint=输入卫星观测资料路径。 | default=None
- {RAIN_GAUGE_DATA} | required=True | type=str | var_name=雨量计资料 | hint=输入雨量计资料路径。 | default=None
- {TARGET_PERIOD} | required=True | type=str | var_name=目标估计时段 | hint=输入目标估计时段。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 源观测与辅助资料的有效时间和来源可追溯
- 雷达、卫星和雨量计三种模态均为必需输入

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
