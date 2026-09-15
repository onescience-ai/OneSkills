# 实例任务：模型输入与运行条件预检 @ E105

- domain: climate
- 骨架: tk-climate-62e157be
- 场景: sc-7a206965 (E105)
- step_id: s01
- depend: []

## 场景研究主体
- E105
- 关联论文: A Deep Learning-Based Bias Correction Method for Predicting Ocean Surface Waves in the Northwest Pacific Ocean | doi:; WaveUformer: a bias correction model for GWSM4C Wave Forecasting | doi:; AI-based Correction of Wave Forecasts Using the Transformer-enhanced UNet Model | doi:

## 本实例步骤描述
核对模型实际输入的数据身份、版本、权限、资料截止时间、变量、时空覆盖和缺测，形成输入清单与数据阻断项。

## 本实例执行 prompt
读取{OPERATIONAL_WAVE_FORECAST}和{WAVE_OBSERVATIONS}，以{DATA_CUTOFF_TIME}核验待订正产品身份、变量、起报、有效时刻、网格、观测覆盖和使用权限；若待订正产品来自EC或GFS须明确其身份。

## 本实例输入槽
- {OPERATIONAL_WAVE_FORECAST} | required=True | type=str | var_name=业务海浪预报 | hint=输入业务模式产品路径。 | default=None
- {WAVE_OBSERVATIONS} | required=True | type=str | var_name=海浪观测历史 | hint=输入观测与历史数据路径。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 输入时空变量与缺测检查报告
- 数据缺失、权限和契约阻断项

## 本实例质量门禁
- 输入文件存在、可读、获准使用且来源和版本可追溯
- 输入的区域、时段、网格、变量、单位、坐标和资料截止时间已逐项核对
- 未来资料、模型开发资料和独立验证资料的用途已隔离
- 输入数据中的缺失、冲突和异常未被推测值覆盖

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
