# 骨架任务：校准空间时间相关性

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 执行“校准空间时间相关性”，恢复物理量、坐标和元数据，生成校准辐照度分布、分位数和区间及必要的质量标志。

## 执行 prompt（跨场景聚合去重）
- 依据{OUTPUT_FORMAT}、{OUTPUT_DIRECTORY}、{POSTPROCESS_CONFIG}、{DERIVED_PRODUCTS}完成校准空间时间相关性，对核心结果执行已登记的校准、订正、派生或聚合并输出校准辐照度分布、分位数和区间。核验单位、坐标、时次、无效值、物理范围和文件可读性；派生量必须记录公式和源变量。

## 输入槽（var/hint/default）
- {OUTPUT_FORMAT} | required=True | type=str | var_name=输出格式 | hint=输入输出文件格式。 | default=None
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果保存路径 | hint=输入结果保存路径。 | default=None
- {POSTPROCESS_CONFIG} | required=False | type=str | var_name=后处理配置 | hint=输入订正派生聚合配置。 | default=None
- {DERIVED_PRODUCTS} | required=False | type=str | var_name=派生产品 | hint=输入派生产品清单。 | default=None

## 产出
- 产品元数据与文件清单
- 校准辐照度分布、分位数和区间
- 质量标志与不确定性信息

## 质量门禁 quality_gate
- 校准后分布、分位数或概率满足单调与取值约束
- 派生产品均有明确公式、源变量和质量标志
- 结果单位、坐标、有效时间和物理范围已核验
- 输出文件能够重新打开且变量和元数据完整

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-58895ff7

## 复用场景
- E24
