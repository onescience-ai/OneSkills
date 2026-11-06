# 使用方式

## 何时召回

需要对无条件/条件扩散做属性定向采样（如 QED/SA/亲和力引导）时

## 如何使用

- KNOW-TM-001：tagmol_framework（concept）
- KNOW-TM-002：guided_sampling_math（concept）
- KNOW-TM-003：multi_objective_guidance（concept）
- KNOW-TM-004：se3_invariant_guide（concept）
- KNOW-TM-005：guide_training（concept）
- KNOW-TM-006：backbone_choice（concept）
- KNOW-TM-009：guidance_strength_oversteer（failure_mode）

## 局限性 / 注意

- 知识来自论文实现对目标的归纳；实际任务须按自身数据与工具链验证。
- 本卡仅作知识承载，不执行安装/运行；环境与资源由 installer/runtime 处理。
- 与既有 molecule/diffusion primitive（如 targetdiff）配合使用时，以其 spec 为准。