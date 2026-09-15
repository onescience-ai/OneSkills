# 骨架任务：逐时效预测位移或轨迹点

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“逐时效预测位移或轨迹点”，完成从气旋历史位置、强度元数据、风暴中心环境场到多时效中心经纬度、路径和登陆概率的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{OUTPUT_INTERVAL}、{ENSEMBLE_SIZE}执行逐时效预测位移或轨迹点，将气旋历史位置、强度元数据、风暴中心环境场转换为多时效中心经纬度、路径和登陆概率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 产出
- 中间状态与运行日志
- 资源和退出状态记录
- 逐时效预测位移或轨迹点结果

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 滚动过程中未读取起报时间之后的观测或分析资料
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-f0f04d2b

## 复用场景
- E30
