# 实例任务：方法配置与输入输出契约验证 @ E5

- domain: climate
- 骨架: tk-climate-2d09b01b
- 场景: sc-9a86054e (E5)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- E5
- 关联论文: XiHe: A Data-Driven Model for Global Ocean Eddy-Resolving Forecasting | doi:; GLONET_ Mercator's end-to-end neural Global Ocean forecasting system | doi:; Forecasting the eddying ocean with a deep neural network | doi:

## 本实例步骤描述
执行“方法配置与输入输出契约验证”，冻结方法工件、参数和随机性配置，并以小样本检查输入输出契约。

## 本实例执行 prompt
依据{METHOD_ARTIFACT}、{METHOD_CONFIG}、{RANDOM_SEED}加载方法工件与配置并完成方法配置与输入输出契约验证。核对变量顺序、张量或表结构、目标定义和输出契约，执行最小干运行；版本不匹配、出现缺失字段或异常数值时停止并标记BLOCKED。

## 本实例输入槽
- {METHOD_ARTIFACT} | required=True | type=str | var_name=方法工件 | hint=输入方法工件路径。 | default=None
- {METHOD_CONFIG} | required=True | type=str | var_name=方法配置 | hint=输入方法参数配置。 | default=None
- {RANDOM_SEED} | required=True | type=str | var_name=随机种子 | hint=输入可复现实验种子。 | default=0

## 本实例产出
- 方法工件与配置身份报告
- 输入输出兼容性矩阵
- 最小干运行日志

## 本实例质量门禁
- 方法工件、配置和运行环境属于兼容版本
- 目标变量和输出结构与任务定义一致
- 最小干运行正常退出且结果不存在NaN或Inf
- 强迫与状态资料的有效时间满足任务边界

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
