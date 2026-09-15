# 实例任务：模型输入与运行条件预检 @ E107

- domain: climate
- 骨架: tk-climate-62e157be
- 场景: sc-6771277f (E107)
- step_id: s01
- depend: []

## 场景研究主体
- E107
- 关联论文: （源场景未提供）

## 本实例步骤描述
核对模型实际输入的数据身份、版本、权限、资料截止时间、变量、时空覆盖和缺测，形成输入清单与数据阻断项。

## 本实例执行 prompt
读取{GLOBAL_FOURCASTNET_ASSET}、{REGIONAL_REANALYSIS_DATA}和{LARGE_SCALE_BOUNDARY_DATA}，以{TARGET_REGION}为范围、{DATA_CUTOFF_TIME}为资料截止时间，核验模型、数据和边界产品的存在性、权限、变量、版本、覆盖和缺测；仅列出数据阻断项。

## 本实例输入槽
- {GLOBAL_FOURCASTNET_ASSET} | required=True | type=str | var_name=全球FourCastNet工件 | hint=输入模型与配置路径。 | default=None
- {REGIONAL_REANALYSIS_DATA} | required=True | type=str | var_name=区域再分析数据 | hint=输入WRF-ERA5等数据路径。 | default=None
- {LARGE_SCALE_BOUNDARY_DATA} | required=True | type=str | var_name=大区域边界产品 | hint=输入边界产品路径。 | default=None
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
- models/fourcastnet

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
