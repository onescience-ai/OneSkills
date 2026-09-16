# 骨架任务：训练易发性分类器

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“训练易发性分类器”，完成从DEM、河网、土地覆盖、土壤、历史洪水样点到洪水易发性概率图的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{SUSCEPTIBILITY_THRESHOLDS}、{UNCERTAINTY_CONFIG}执行训练易发性分类器，将DEM、河网、土地覆盖、土壤、历史洪水样点转换为洪水易发性概率图。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=易发性制图配置 | hint=输入易发性制图配置。 | default=None
- {SUSCEPTIBILITY_THRESHOLDS} | required=True | type=str | var_name=易发性等级阈值 | hint=输入易发性等级阈值。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 产出
- 中间状态与运行日志
- 训练易发性分类器结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 输出是长期静态易发性而非某次洪水预警概率
- 配置、随机种子、日志和中间状态能够追溯
- 预警阈值在独立验证集上冻结后评估

## 可调资源（edge:resource，仅真实存在）
- tools/ecmwf-hres

## 实例任务（本骨架在各场景的实例化）
- climate-train-susceptibility-classifie-terrain-and-underlying-inst

## 复用场景
- E76
