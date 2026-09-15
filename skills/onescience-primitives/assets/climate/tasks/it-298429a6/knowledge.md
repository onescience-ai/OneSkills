# 实例任务：模型输入与运行条件预检 @ E109

- domain: climate
- 骨架: tk-climate-62e157be
- 场景: sc-2c4fca50 (E109)
- step_id: s01
- depend: []

## 场景研究主体
- E109
- 关联论文: （源场景未提供）

## 本实例步骤描述
核对模型实际输入的数据身份、版本、权限、资料截止时间、变量、时空覆盖和缺测，形成输入清单与数据阻断项。

## 本实例执行 prompt
读取{PREDICTED_COASTAL_WATER_LEVEL}、{TERRAIN_COAST_DEFENSE}和{ADMINISTRATIVE_BOUNDARIES}，以{TARGET_COASTAL_AREA}和{DATA_CUTOFF_TIME}核验存在性、权限、水位与高程基准、坐标、空间覆盖、有效时间、岸线、防护工程和行政边界；缺少任一必要输入或关键定义时标记BLOCKED。

## 本实例输入槽
- {PREDICTED_COASTAL_WATER_LEVEL} | required=True | type=str | var_name=预测沿岸潮位 | hint=输入沿岸潮位预报路径。 | default=None
- {TARGET_COASTAL_AREA} | required=True | type=str | var_name=目标近岸区域 | hint=输入目标区域边界。 | default=None
- {TERRAIN_COAST_DEFENSE} | required=True | type=str | var_name=地形岸线防护数据 | hint=输入地形岸线工程路径。 | default=None
- {ADMINISTRATIVE_BOUNDARIES} | required=True | type=str | var_name=行政区划数据 | hint=输入行政边界数据路径。 | default=None
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
