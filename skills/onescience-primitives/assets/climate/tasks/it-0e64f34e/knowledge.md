# 实例任务：粗细分辨率资料及任务边界预检 @ E15

- domain: climate
- 骨架: tk-climate-721f3e3f
- 场景: sc-acf02f5d (E15)
- step_id: s01
- depend: []

## 场景研究主体
- E15
- 关联论文: Global spatio-temporal ERA5 precipitation downscaling to km and sub-hourly scale using generative AI | doi:; A precipitation downscaling method using a super-resolution deconvolution neural network with step orography | doi:; Customized deep learning for precipitation bias correction and downscaling | doi:

## 本实例步骤描述
界定“粗分辨率降水到公里—亚小时尺度的概率降尺度”的任务范围并执行“粗细分辨率资料及任务边界预检”，核验粗网格小时降水、地形及可选环境场的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“粗分辨率降水到公里—亚小时尺度的概率降尺度”，读取{COARSE_PRECIPITATION}、{FINE_PRECIPITATION_REFERENCE}、{TARGET_GRID}、{TARGET_TIME_INTERVAL}、{DATA_CUTOFF_TIME}并完成粗细分辨率资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {COARSE_PRECIPITATION} | required=True | type=str | var_name=粗网格降水 | hint=输入粗网格降水路径。 | default=None
- {FINE_PRECIPITATION_REFERENCE} | required=True | type=str | var_name=细尺度降水参考 | hint=输入细尺度降水参考。 | default=None
- {TARGET_GRID} | required=True | type=str | var_name=公里级目标网格 | hint=输入公里级网格规格。 | default=None
- {TARGET_TIME_INTERVAL} | required=True | type=str | var_name=亚小时时间间隔 | hint=输入亚小时时间间隔。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 粗细分辨率样本严格同期且坐标一致
- 目标同时包含公里级空间细化和亚小时时间细化

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
