# 实例任务：独立验证与结论 @ 多孔材料数据高效基础模型构建

- domain: matchem
- 骨架: matchem-independent-validation-conclusion-task
- 场景: matchem-porous-material-data-efficient-foundation-model-construction-scenario (多孔材料数据高效基础模型构建)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- 多孔材料数据高效基础模型构建
- 关联论文: A data-efficient foundation model for porous materials based on expert-guided supervised learning | doi:

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
- models/data-efficient-machine-learning-potentials-modeling-catalytic

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
