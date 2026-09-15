# 实例任务：融合多模态信息生成地面降水场 @ E21

- domain: climate
- 骨架: tk-climate-5c65f3b6
- 场景: sc-61b5e0f0 (E21)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E21
- 关联论文: A Deep Learning Multimodal Method for Precipitation Estimation | doi:; Ground radar precipitation estimation with deep learning approaches in meteorological private cloud | doi:; RainForest- a random forest algorithm for quantitative precipitation estimation over Switzerland | doi:; Improving near real-time precipitation estimation using a U-Net convolutional neural network and geographical information | doi:

## 本实例步骤描述
按冻结配置执行“融合多模态信息生成地面降水场”，完成从雷达观测、卫星云图、雨量计及地理特征到同期格点降水率或累积降水的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{OUTPUT_RESOLUTION}、{DECISION_THRESHOLD}执行融合多模态信息生成地面降水场，将雷达观测、卫星云图、雨量计及地理特征转换为同期格点降水率或累积降水。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_RESOLUTION} | required=True | type=str | var_name=输出分辨率 | hint=输入输出分辨率。 | default=None
- {DECISION_THRESHOLD} | required=False | type=str | var_name=诊断阈值 | hint=输入诊断判定阈值。 | default=None

## 本实例产出
- 融合多模态信息生成地面降水场结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 参考定义或标签未泄漏到待诊断样本
- 任一模态缺失时不得退化成雷达单源场景并宣称完成

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
