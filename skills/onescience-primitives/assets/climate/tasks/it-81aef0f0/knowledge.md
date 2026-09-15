# 实例任务：提取连续冰雹风险对象 @ E83

- domain: climate
- 骨架: tk-climate-4ab08771
- 场景: sc-49bf5db0 (E83)
- step_id: s05
- depend: ['s04']

## 场景研究主体
- E83
- 关联论文: A Spatial-temporal Deep Probabilistic Diffusion Model for Reliable Hail Nowcasting with Radar Echo Extrapolation | doi:

## 本实例步骤描述
执行“提取连续冰雹风险对象”，恢复物理量、坐标和元数据，生成分时效冰雹概率格点与风险对象及必要的质量标志。

## 本实例执行 prompt
依据{OUTPUT_FORMAT}、{OUTPUT_DIRECTORY}、{POSTPROCESS_CONFIG}、{DERIVED_PRODUCTS}完成提取连续冰雹风险对象，对核心结果执行已登记的校准、订正、派生或聚合并输出分时效冰雹概率格点与风险对象。核验单位、坐标、时次、无效值、物理范围和文件可读性；派生量必须记录公式和源变量。

## 本实例输入槽
- {OUTPUT_FORMAT} | required=True | type=str | var_name=输出格式 | hint=输入输出文件格式。 | default=None
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果保存路径 | hint=输入结果保存路径。 | default=None
- {POSTPROCESS_CONFIG} | required=False | type=str | var_name=后处理配置 | hint=输入订正派生聚合配置。 | default=None
- {DERIVED_PRODUCTS} | required=False | type=str | var_name=派生产品 | hint=输入派生产品清单。 | default=None

## 本实例产出
- 分时效冰雹概率格点与风险对象
- 质量标志与不确定性信息
- 产品元数据与文件清单

## 本实例质量门禁
- 输出文件能够重新打开且变量和元数据完整
- 结果单位、坐标、有效时间和物理范围已核验
- 派生产品均有明确公式、源变量和质量标志
- 每个目标提前量均生成且未使用未来观测

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
