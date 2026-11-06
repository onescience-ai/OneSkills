# 使用方式

## 何时召回

用于分子生成任务（对接打分由外部 soft 提供）时

## 如何使用

- KNOW-TM-007：metrics_protocol（concept）
- KNOW-TM-008：main_results（example）

## 局限性 / 注意

- 知识来自论文实现对目标的归纳；实际任务须按自身数据与工具链验证。
- 本卡仅作知识承载，不执行安装/运行；环境与资源由 installer/runtime 处理。
- 与既有 molecule/diffusion primitive（如 targetdiff）配合使用时，以其 spec 为准。