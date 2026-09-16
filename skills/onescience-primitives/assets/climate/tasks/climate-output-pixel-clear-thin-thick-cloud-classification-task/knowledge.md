# 骨架任务：输出晴空、薄云和厚云逐像元分类

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“输出晴空、薄云和厚云逐像元分类”，完成从多光谱或RGB影像、观测几何和清空参考到云概率、类别及质量掩膜的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{DECISION_THRESHOLD}、{UNCERTAINTY_CONFIG}执行输出晴空、薄云和厚云逐像元分类，将多光谱或RGB影像、观测几何和清空参考转换为云概率、类别及质量掩膜。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {DECISION_THRESHOLD} | required=False | type=str | var_name=判定阈值 | hint=输入分类或检测阈值。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 产出
- 中间状态与运行日志
- 资源和退出状态记录
- 输出晴空、薄云和厚云逐像元分类结果

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 输出坐标、分辨率、无效值和置信信息完整
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- tools/ecmwf-hres

## 实例任务（本骨架在各场景的实例化）
- climate-output-pixel-clear-thin-thick-visible-image-cloud-mask-inst

## 复用场景
- E35
