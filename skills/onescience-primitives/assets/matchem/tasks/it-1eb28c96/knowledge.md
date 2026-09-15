# 实例任务：独立验证与结论 @ 高熵固溶体形成机器学习预测

- domain: matchem
- 骨架: tk-matchem-74528141
- 场景: sc-e282a1e9 (高熵固溶体形成机器学习预测)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- 高熵固溶体形成机器学习预测
- 关联论文: Machine-learning informed prediction of high-entropy solid solution formation: Beyond the Hume-Rothery rules | doi:

## 本实例步骤描述
用独立实验或高保真计算验证优先候选。

## 本实例执行 prompt
有 {VALIDATION_DATA} 时进行独立验证；没有时明确为待验证预测，不得宣称实验成功。

## 本实例输入槽
- {VALIDATION_DATA} | required=False | type=doc | var_name=独立验证数据 | hint=留出测试集、外部实验或高保真计算结果。 | default=optional

## 本实例产出
- 验证对照
- PASS/REJECT/BLOCKED 结论

## 本实例质量门禁
- 预测与验证分开报告
- 失败候选保留记录

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
