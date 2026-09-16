# 实例任务：方法配置与输入输出契约验证 @ E13

- domain: climate
- 骨架: climate-method-configuration-input-output-contract-validation-task
- 场景: climate-global-ocean-pco2-sparse-observation-spatiotemporal-expansion-scenario (E13)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- E13
- 关联论文: A comparative assessment of the uncertainties of global surface ocean CO 2 estimates using a machine-learning ensemble (CSIR-ML6 version 2019a) – have we hit the wall? | doi:; Global high-resolution monthly p CO 2 climatology for the coastal ocean derived from neural network interpolation | doi:; Spatiotemporal upscaling of sparse air-sea pCO2 data via physics-informed transfer learning | doi:

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
- 伪缺口与独立验证块未参与重建参数选择

## 可调资源（edge:resource，仅真实存在）
- datasets/random-forest-model-performance-evaluation
- models/random-forest-meteorological-normalization
- models/random-forest-regression-for-vertical-wind-speed-extrapolation
- models/tucker-thresholding-method-for-boundary-layer-height-estimation

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
