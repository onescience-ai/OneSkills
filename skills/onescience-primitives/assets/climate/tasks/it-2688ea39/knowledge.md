# 实例任务：网格对齐与输入标准化 @ E1

- domain: climate
- 骨架: tk-climate-5e6eb541
- 场景: sc-07460df1 (E1)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E1
- 关联论文: Learning skillful medium-range global weather forecasting | doi:; Accurate medium-range global weather forecasting with 3D neural networks | doi:; FourCastNet: A Global Data-driven High-resolution Weather Model using Adaptive Fourier Neural Operators | doi:; FengWu: Pushing the Skillful Global Medium-range Weather Forecast beyond 10 Days Lead | doi:; AIFS -- ECMWF's data-driven forecasting system | doi:

## 本实例步骤描述
依据版本化模型输入契约执行重网格、变量排序、单位换算、标准化及静态地理特征编码。

## 本实例执行 prompt
根据{MODEL_INPUT_SPEC}和{PREPROCESS_CONFIG}处理通过预检的分析场，执行{MISSING_VALUE_POLICY}，生成与模型严格兼容的输入张量。记录每项重网格、单位换算、变量排序和标准化参数，保证处理可追溯。

## 本实例输入槽
- {MODEL_INPUT_SPEC} | required=True | type=str | var_name=模型输入规格 | hint=输入模型类型，如Swin-transformer、GNN、AFNO。 | default=None
- {PREPROCESS_CONFIG} | required=True | type=str | var_name=预处理配置 | hint=输入预处理配置路径。 | default=None
- {MISSING_VALUE_POLICY} | required=True | type=str | var_name=缺测处理策略 | hint=输入拒绝或插补策略。 | default=None

## 本实例产出
- 标准化模型输入张量
- 输入掩膜与静态特征
- 预处理转换清单

## 本实例质量门禁
- 张量维度、变量顺序、时次顺序和坐标方向与模型输入契约一致
- 经度周期、极点、日历和气压层顺序已核验
- 归一化参数与检查点版本一致
- 不存在模型不支持的NaN或Inf

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
