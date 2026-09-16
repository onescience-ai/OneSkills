# 骨架任务：临床质量与安全复核

- domain: bio
- 复用场景数: 3
- 实例任务数: 3

## 步骤描述（跨场景聚合去重）
- 计算RadGraph-F1并检查事实、遗漏、矛盾和安全风险。
- 计算临床正确率并检查事实、遗漏、矛盾和安全风险。
- 计算变化F1并检查事实、遗漏、矛盾和安全风险。

## 执行 prompt（跨场景聚合去重）
- 计算RadGraph-F1并与{MIN_CLINICAL_SCORE}比较；按{REQUIRE_REVIEW}标记医生复核后方可使用。
- 计算临床正确率并与{MIN_CLINICAL_SCORE}比较；按{REQUIRE_REVIEW}标记医生复核后方可使用。
- 计算变化F1并与{MIN_CLINICAL_SCORE}比较；按{REQUIRE_REVIEW}标记医生复核后方可使用。

## 输入槽（var/hint/default）
- {MIN_CLINICAL_SCORE} | required=False | type=float | var_name=临床得分下限 | hint=设置临床质量下限 | default=0.7
- {REQUIRE_REVIEW} | required=False | type=bool | var_name=要求医生复核 | hint=是否标记必须人工复核 | default=True

## 产出
- RadGraph-F1明细
- 临床正确率明细
- 临床质控报告
- 人工复核清单
- 变化F1明细

## 质量门禁 quality_gate
- 关键异常遗漏已检查
- 无依据结论已标记
- 输出明确不是最终诊断

## 可调资源（edge:resource，仅真实存在）
- datasets/tm-score-evaluation

## 实例任务（本骨架在各场景的实例化）
- bio-clinical-quality-safety-review-clinical-reward-aligned-inst
- bio-clinical-quality-safety-review-longitudinal-chest-ct-inst
- bio-clinical-quality-safety-review-medical-text-and-image-inst

## 复用场景
- B99
- B98
- B100
