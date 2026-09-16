# 实例任务：恢复缺测海温并估计逐像元条件误差 @ E69

- domain: climate
- 骨架: climate-restoring-missing-sst-estimating-pixel-conditional-error-task
- 场景: climate-cloud-covered-satellite-sst-reconstruction-pixel-uncertainty-scenario (E69)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E69
- 关联论文: DINCAE 1.0: a convolutional neural network with error estimates to reconstruct sea surface temperature satellite observations | doi:

## 本实例步骤描述
按冻结配置执行“恢复缺测海温并估计逐像元条件误差”，完成从带云缺测的卫星海温序列、质量标志和时空坐标到完整海温场及像元误差的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RECONSTRUCTION_CONFIG}、{OUTPUT_RESOLUTION}、{UNCERTAINTY_CONFIG}执行恢复缺测海温并估计逐像元条件误差，将带云缺测的卫星海温序列、质量标志和时空坐标转换为完整海温场及像元误差。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RECONSTRUCTION_CONFIG} | required=True | type=str | var_name=重建配置 | hint=输入缺口重建配置。 | default=None
- {OUTPUT_RESOLUTION} | required=True | type=str | var_name=输出分辨率 | hint=输入输出分辨率。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 本实例产出
- 恢复缺测海温并估计逐像元条件误差结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 观测位置保持原值且缺口结果无拼接突变

## 可调资源（edge:resource，仅真实存在）
- datasets/gtws-mlrec-machine-learning-based-global-terrestrial-water-storage-anomaly-reconstruction-dataset-and-workflow
- models/ensemble-model-output-statistics-emos-post-processing
- models/swe-reconstruction-using-energy-balance-model

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
