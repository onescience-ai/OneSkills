# 实例任务：医学推理与一致性校订 @ B100

- domain: bio
- 骨架: tk-bio-b2b908cc
- 场景: sc-e4455cb5 (B100)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- B100
- 关联论文: ALTER: Modeling Longitudinal Changes via Regional Differencing for 3D CT Report Generation | doi:

## 本实例步骤描述
生成问答或报告并执行可选的事实一致性校订。

## 本实例执行 prompt
以温度{TEMPERATURE}和种子{SEED}运行纵向胸部CT变化检测与报告生成，按{REVISION_PASS}决定是否执行二次事实校订。

## 本实例输入槽
- {TEMPERATURE} | required=False | type=float | var_name=生成温度 | hint=控制医学文本随机性 | default=0.2
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定医学生成结果 | default=7
- {REVISION_PASS} | required=False | type=bool | var_name=启用二次校订 | hint=是否执行事实二次核对 | default=True

## 本实例产出
- 医学回答或报告
- 证据定位
- 校订记录

## 本实例质量门禁
- 输出无患者身份信息
- 结论可定位到影像证据
- 不确定性已明确表达

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
