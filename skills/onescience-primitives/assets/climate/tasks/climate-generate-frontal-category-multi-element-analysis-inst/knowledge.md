# 实例任务：生成锋面类别概率格点并阈值化连接折线 @ E97

- domain: climate
- 骨架: climate-generate-frontal-category-probability-grid-and-threshold-lines-task
- 场景: climate-multi-element-analysis-field-driven-weather-front-detection-and-scenario (E97)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E97
- 关联论文: Automated detection of weather fronts using a deep learning neural network | doi:

## 本实例步骤描述
按冻结配置执行“生成锋面类别概率格点并阈值化连接折线”，完成从表面温湿压风分析场、人工锋面标签到锋面类别概率格点与矢量折线的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{OUTPUT_RESOLUTION}、{DECISION_THRESHOLD}执行生成锋面类别概率格点并阈值化连接折线，将表面温湿压风分析场、人工锋面标签转换为锋面类别概率格点与矢量折线。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_RESOLUTION} | required=True | type=str | var_name=输出分辨率 | hint=输入输出分辨率。 | default=None
- {DECISION_THRESHOLD} | required=False | type=str | var_name=诊断阈值 | hint=输入诊断判定阈值。 | default=None

## 本实例产出
- 生成锋面类别概率格点并阈值化连接折线结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 参考定义或标签未泄漏到待诊断样本
- 先生成冷暖锋类别概率格点再执行阈值化和折线连接

## 可调资源（edge:resource，仅真实存在）
- models/ensemble-model-output-statistics-emos-post-processing
- tools/ecmwf-hres

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
