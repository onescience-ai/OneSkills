# 实例任务：模型输入与运行条件预检 @ E103

- domain: climate
- 骨架: tk-climate-62e157be
- 场景: sc-e681786f (E103)
- step_id: s01
- depend: []

## 场景研究主体
- E103
- 关联论文: （源场景未提供）

## 本实例步骤描述
核对模型实际输入的数据身份、版本、权限、资料截止时间、变量、时空覆盖和缺测，形成输入清单与数据阻断项。

## 本实例执行 prompt
读取{OCEAN_TEMPERATURE_FORECAST}、{FUSED_SST_OBSERVATION}和{ATMOSPHERIC_FORCING_FORECAST}，以{TARGET_REGION}和{DATA_CUTOFF_TIME}核验系统版本、起报、有效时刻、层次、网格、缺测和未来资料泄漏。

## 本实例输入槽
- {OCEAN_TEMPERATURE_FORECAST} | required=True | type=str | var_name=海温数值预报 | hint=输入三维海温预报路径。 | default=None
- {FUSED_SST_OBSERVATION} | required=True | type=str | var_name=融合海表温度观测 | hint=输入融合SST观测路径。 | default=None
- {ATMOSPHERIC_FORCING_FORECAST} | required=True | type=str | var_name=气象强迫预报 | hint=输入气温降水风场路径。 | default=None
- {TARGET_REGION} | required=True | type=str | var_name=目标区域 | hint=输入北海区区域边界。 | default=北海区
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
