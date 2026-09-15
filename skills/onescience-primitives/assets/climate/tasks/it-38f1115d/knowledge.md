# 实例任务：方法配置与输入输出契约验证 @ E94

- domain: climate
- 骨架: tk-climate-2d09b01b
- 场景: sc-c3edf438 (E94)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- E94
- 关联论文: Anthropogenic fingerprints in daily precipitation revealed by deep learning | doi:

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
- 训练、检测和显著性评估样本相互独立

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
