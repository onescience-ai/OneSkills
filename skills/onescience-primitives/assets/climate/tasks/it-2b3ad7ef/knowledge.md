# 实例任务：模型输入与运行条件预检 @ E108

- domain: climate
- 骨架: tk-climate-62e157be
- 场景: sc-1033997c (E108)
- step_id: s01
- depend: []

## 场景研究主体
- E108
- 关联论文: （源场景未提供）

## 本实例步骤描述
核对模型实际输入的数据身份、版本、权限、资料截止时间、变量、时空覆盖和缺测，形成输入清单与数据阻断项。

## 本实例执行 prompt
读取{WRF_FORECAST_DATA}和{WRF_ERA5_REFERENCE}，以{TARGET_REGION}和{DATA_CUTOFF_TIME}核验预报与参考数据的存在性、权限、版本、变量、起报、有效时刻、网格和缺测；仅列出数据阻断项。

## 本实例输入槽
- {WRF_FORECAST_DATA} | required=True | type=str | var_name=WRF预报数据 | hint=输入WRF历史预报路径。 | default=None
- {WRF_ERA5_REFERENCE} | required=True | type=str | var_name=WRF-ERA5参考数据 | hint=输入再分析参考路径。 | default=None
- {TARGET_REGION} | required=True | type=str | var_name=目标区域 | hint=输入渤黄海区域边界。 | default=渤黄海区域
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
- datasets/ERA5

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
