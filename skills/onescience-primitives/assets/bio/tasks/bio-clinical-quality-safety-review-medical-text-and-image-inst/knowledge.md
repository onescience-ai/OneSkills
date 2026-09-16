# 实例任务：临床质量与安全复核 @ B98

- domain: bio
- 骨架: bio-clinical-quality-safety-review-task
- 场景: bio-medical-text-and-image-multimodal-qa-and-report-assistant-scenario (B98)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- B98
- 关联论文: MedGemma 1.5 Technical Report | doi:

## 本实例步骤描述
计算临床正确率并检查事实、遗漏、矛盾和安全风险。

## 本实例执行 prompt
计算临床正确率并与{MIN_CLINICAL_SCORE}比较；按{REQUIRE_REVIEW}标记医生复核后方可使用。

## 本实例输入槽
- {MIN_CLINICAL_SCORE} | required=False | type=float | var_name=临床得分下限 | hint=设置临床质量下限 | default=0.7
- {REQUIRE_REVIEW} | required=False | type=bool | var_name=要求医生复核 | hint=是否标记必须人工复核 | default=True

## 本实例产出
- 临床质控报告
- 临床正确率明细
- 人工复核清单

## 本实例质量门禁
- 无依据结论已标记
- 关键异常遗漏已检查
- 输出明确不是最终诊断

## 可调资源（edge:resource，仅真实存在）
- datasets/tm-score-evaluation

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
