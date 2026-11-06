# 使用方式

## 何时召回

在科研/论文复现中规划 SBDD 分子工作（生成/排序/评估）时；安装动作由 installer 处理，本卡仅作资源与依赖清单

## 如何使用

- KNOW-R-BD-003：software_deps（resource_requirement）
- KNOW-R-TM-002：software_tools_tm（resource_requirement）

## 局限性 / 注意

- 知识来自论文实现对目标的归纳；实际任务须按自身数据与工具链验证。
- 本卡仅作知识承载，不执行安装/运行；环境与资源由 installer/runtime 处理。
- 与既有 molecule/diffusion primitive（如 targetdiff）配合使用时，以其 spec 为准。