# 实例任务：0—3小时集合降水生成 @ E2

- domain: climate
- 骨架: tk-climate-476309cc
- 场景: sc-16d509a7 (E2)
- step_id: s04
- depend: ['s02', 's03']

## 场景研究主体
- E2
- 关联论文: Skilful nowcasting of extreme precipitation with NowcastNet | doi:; Skilful precipitation nowcasting using deep generative models of radar | doi:; Convolutional LSTM Network: A Machine Learning Approach for Precipitation Nowcasting | doi:; RainNet v1.0: a convolutional neural network for radar-based precipitation nowcasting | doi:

## 本实例步骤描述
使用已验证的时空预测组件和成员生成配置，生成未来多时次高分辨率降水率集合。

## 本实例执行 prompt
使用已验证的模型、雷达张量和集合配置，按{OUTPUT_INTERVAL_MINUTES}分钟间隔生成至{FORECAST_HORIZON_MINUTES}分钟的降水率集合。根据{SAVE_MEMBER_FIELDS}保存成员格点场，逐成员记录随机种子、输出值域、耗时和异常状态。

## 本实例输入槽
- {OUTPUT_INTERVAL_MINUTES} | required=True | type=str | var_name=输出时间间隔 | hint=输入输出间隔，单位分钟。 | default=10
- {SAVE_MEMBER_FIELDS} | required=True | type=str | var_name=保存成员格点场 | hint=输入是否保存成员场。 | default=true

## 本实例产出
- 多成员降水率预报序列
- 集合均值与分位数场
- 逐成员推理日志与资源统计

## 本实例质量门禁
- 预报时次完整且不超过180分钟
- 所有成员的空间网格、时间轴和单位一致
- 输出不存在未解释的NaN、Inf或负雨强
- 成员差异来自登记的随机采样而非版本或输入不一致
- 推理过程中未读取起报时间之后的雷达观测

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
