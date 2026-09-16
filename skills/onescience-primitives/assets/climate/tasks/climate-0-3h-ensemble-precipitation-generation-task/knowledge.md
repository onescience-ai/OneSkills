# 骨架任务：0—3小时集合降水生成

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 使用已验证的时空预测组件和成员生成配置，生成未来多时次高分辨率降水率集合。

## 执行 prompt（跨场景聚合去重）
- 使用已验证的模型、雷达张量和集合配置，按{OUTPUT_INTERVAL_MINUTES}分钟间隔生成至{FORECAST_HORIZON_MINUTES}分钟的降水率集合。根据{SAVE_MEMBER_FIELDS}保存成员格点场，逐成员记录随机种子、输出值域、耗时和异常状态。

## 输入槽（var/hint/default）
- {OUTPUT_INTERVAL_MINUTES} | required=True | type=str | var_name=输出时间间隔 | hint=输入输出间隔，单位分钟。 | default=10
- {SAVE_MEMBER_FIELDS} | required=True | type=str | var_name=保存成员格点场 | hint=输入是否保存成员场。 | default=true

## 产出
- 多成员降水率预报序列
- 逐成员推理日志与资源统计
- 集合均值与分位数场

## 质量门禁 quality_gate
- 成员差异来自登记的随机采样而非版本或输入不一致
- 所有成员的空间网格、时间轴和单位一致
- 推理过程中未读取起报时间之后的雷达观测
- 输出不存在未解释的NaN、Inf或负雨强
- 预报时次完整且不超过180分钟

## 可调资源（edge:resource，仅真实存在）
- models/ensemble-model-output-statistics-emos-post-processing
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 实例任务（本骨架在各场景的实例化）
- climate-0-3h-ensemble-precipitation-radar-driven-0-3-hour-inst

## 复用场景
- E2
