# 实例任务：生成海床高程及多时效变化场 @ E74

- domain: climate
- 骨架: climate-seabed-elevation-multileadtime-change-task
- 场景: climate-coastal-bathymetry-reconstruction-morphological-evolution-scenario (E74)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E74
- 关联论文: Advancing bathymetric reconstruction and forecasting using deep learning | doi:

## 本实例步骤描述
按冻结配置执行“生成海床高程及多时效变化场”，完成从历史浴深测量、水动力和泥沙强迫到完整浴深场及未来海床高程变化的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{OUTPUT_INTERVAL}、{ENSEMBLE_SIZE}执行生成海床高程及多时效变化场，将历史浴深测量、水动力和泥沙强迫转换为完整浴深场及未来海床高程变化。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 本实例产出
- 生成海床高程及多时效变化场结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 输出在岸线、深水区和强梯度区无异常跳变

## 可调资源（edge:resource，仅真实存在）
- datasets/cesm2-large-ensemble
- datasets/large-ensemble-testbed
- models/crpsexp-loss-function-for-ensemble-forecasting
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
