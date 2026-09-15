# 实例任务：连续生成逐日径流 @ E10

- domain: climate
- 骨架: tk-climate-e0f1bc6d
- 场景: sc-3938a6f7 (E10)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E10
- 关联论文: A note on leveraging synergy in multiple meteorological data sets with deep learning for rainfall–runoff modeling | doi:; Hydrologically informed machine learning for rainfall–runoff modelling: towards distributed modelling | doi:; Rainfall–runoff modelling using Long Short-Term Memory (LSTM) networks | doi:; Rainfall–Runoff Prediction at Multiple Timescales with a Single Long Short-Term Memory Network | doi:

## 本实例步骤描述
按冻结配置执行“连续生成逐日径流”，完成从多源逐日气象强迫、流域静态属性、历史流量到逐日径流过程与水文特征的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{INITIAL_STATE}、{ENSEMBLE_SIZE}执行连续生成逐日径流，将多源逐日气象强迫、流域静态属性、历史流量转换为逐日径流过程与水文特征。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {INITIAL_STATE} | required=False | type=str | var_name=初始水文状态 | hint=输入初始水文状态路径。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 本实例产出
- 连续生成逐日径流结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 水量、状态范围和洪峰时序不存在非物理异常

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
