# 实例任务：批量生成并拼接农田概率图 @ E56

- domain: climate
- 骨架: tk-climate-6615e7df
- 场景: sc-85b54362 (E56)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E56
- 关联论文: A 30-m landsat-derived cropland extent product of Australia and China using random forest machine learning algorithm on Google Earth Engine cloud computing platform | doi:; Agricultural cropland extent and areas of South Asia derived using Landsat satellite 30-m time-series big-data using random forest machine learning algorithms on the Google Earth Engine cloud | doi:

## 本实例步骤描述
按冻结配置执行“批量生成并拼接农田概率图”，完成从多季节Landsat影像、植被指数和训练样本到30米农田范围图及区域面积的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{CROPLAND_THRESHOLD}、{AREA_STATISTICS_UNITS}执行批量生成并拼接农田概率图，将多季节Landsat影像、植被指数和训练样本转换为30米农田范围图及区域面积。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=制图运行配置 | hint=输入农田制图配置。 | default=None
- {CROPLAND_THRESHOLD} | required=True | type=str | var_name=农田判定阈值 | hint=输入农田判定阈值。 | default=None
- {AREA_STATISTICS_UNITS} | required=True | type=str | var_name=面积统计单位 | hint=输入面积统计单位。 | default=None

## 本实例产出
- 批量生成并拼接农田概率图结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 输出坐标、分辨率、无效值和置信信息完整
- 二分类概率、农田掩膜和面积统计同步生成

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
