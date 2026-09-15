# 实例任务：恢复物理量并计算概率产品 @ E3

- domain: climate
- 骨架: tk-climate-f18e610e
- 场景: sc-04cf543b (E3)
- step_id: s05
- depend: ['s04']

## 场景研究主体
- E3
- 关联论文: GenCast_ learning skillful ensemble forecasting of medium-range weather | doi:; FuXi-ENS- A machine learning model for medium-range ensemble weather forecasting | doi:; LaDCast- A Latent Diffusion Model for Medium-Range Ensemble Weather Forecasting | doi:

## 本实例步骤描述
执行“恢复物理量并计算概率产品”，恢复物理量、坐标和元数据，生成多变量集合预报场、分位数与超阈概率及必要的质量标志。

## 本实例执行 prompt
依据{OUTPUT_FORMAT}、{OUTPUT_DIRECTORY}、{POSTPROCESS_CONFIG}、{DERIVED_PRODUCTS}完成恢复物理量并计算概率产品，对核心结果执行已登记的校准、订正、派生或聚合并输出多变量集合预报场、分位数与超阈概率。核验单位、坐标、时次、无效值、物理范围和文件可读性；派生量必须记录公式和源变量。

## 本实例输入槽
- {OUTPUT_FORMAT} | required=True | type=str | var_name=输出格式 | hint=输入输出文件格式。 | default=None
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果保存路径 | hint=输入结果保存路径。 | default=None
- {POSTPROCESS_CONFIG} | required=False | type=str | var_name=后处理配置 | hint=输入订正派生聚合配置。 | default=None
- {DERIVED_PRODUCTS} | required=False | type=str | var_name=派生产品 | hint=输入派生产品清单。 | default=None

## 本实例产出
- 多变量集合预报场、分位数与超阈概率
- 质量标志与不确定性信息
- 产品元数据与文件清单

## 本实例质量门禁
- 输出文件能够重新打开且变量和元数据完整
- 结果单位、坐标、有效时间和物理范围已核验
- 派生产品均有明确公式、源变量和质量标志
- 滚动过程中未读取起报时间之后的观测或分析资料

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
