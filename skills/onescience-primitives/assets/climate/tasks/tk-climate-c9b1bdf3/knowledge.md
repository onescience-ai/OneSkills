# 骨架任务：生成连续高分辨率场

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“生成连续高分辨率场”，完成从卫星土壤湿度、植被地表温度、地形土壤属性到高分辨率土壤湿度与质量标志的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{DOWNSCALING_CONFIG}、{TEMPORAL_FILL_POLICY}、{UNCERTAINTY_CONFIG}执行生成连续高分辨率场，将卫星土壤湿度、植被地表温度、地形土壤属性转换为高分辨率土壤湿度与质量标志。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {DOWNSCALING_CONFIG} | required=True | type=str | var_name=降尺度配置 | hint=输入降尺度运行配置。 | default=None
- {TEMPORAL_FILL_POLICY} | required=True | type=str | var_name=时序重建规则 | hint=输入时序重建规则。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 产出
- 中间状态与运行日志
- 生成连续高分辨率场结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 水量、状态范围和洪峰时序不存在非物理异常
- 目标区域和时段内结果完整且无重复或错位
- 空间降尺度与时间缺口重建结果可分别追溯
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-e3fc365d

## 复用场景
- E16
