# 骨架任务：医学推理与一致性校订

- domain: bio
- 复用场景数: 3
- 实例任务数: 3

## 步骤描述（跨场景聚合去重）
- 生成问答或报告并执行可选的事实一致性校订。

## 执行 prompt（跨场景聚合去重）
- 以温度{TEMPERATURE}和种子{SEED}运行临床奖励对齐的胸部X线报告生成，按{REVISION_PASS}决定是否执行二次事实校订。
- 以温度{TEMPERATURE}和种子{SEED}运行医学文本与影像多模态问答及报告辅助，按{REVISION_PASS}决定是否执行二次事实校订。
- 以温度{TEMPERATURE}和种子{SEED}运行纵向胸部CT变化检测与报告生成，按{REVISION_PASS}决定是否执行二次事实校订。

## 输入槽（var/hint/default）
- {TEMPERATURE} | required=False | type=float | var_name=生成温度 | hint=控制医学文本随机性 | default=0.2
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定医学生成结果 | default=7
- {REVISION_PASS} | required=False | type=bool | var_name=启用二次校订 | hint=是否执行事实二次核对 | default=True

## 产出
- 医学回答或报告
- 校订记录
- 证据定位

## 质量门禁 quality_gate
- 不确定性已明确表达
- 结论可定位到影像证据
- 输出无患者身份信息

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-373ba66e
- it-88817d28
- it-898a7a71

## 复用场景
- B99
- B98
- B100
