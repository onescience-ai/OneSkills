# Bio Domain Role Boundary Contract

本文件约束 `onescience-role/bio_domain` 的职责边界。

## 定位

`bio_domain` 是 `onescience-role` 的领域子路由层，只负责：

- 把 biology / bioinformatics 请求归入最小生信范畴
- 选择需要读取的范畴 skill 和具体生信 skill
- 整理角色链、交接物和未来执行入口
- 区分 OneScience 生信模型任务与通用生信 workflow / tool / database / lab-quality 任务

它不负责：

- 直接执行 Python / shell 脚本
- 直接生成最终业务代码
- 直接提交远程作业
- 直接安装依赖或修复环境
- 承诺模型 checkpoint、数据库、GPU/DCU 或外部工具已经可用

## 与 workflow 的边界

`onescience-workflow` 负责粗路由：

- `domain_route=biology`
- `domain_task_family`
- `stage_intent`
- `planning_only`

`bio_domain` 只继续细化：

- `bio_task_family`
- `onescience_model_related`
- `selected_category_skill`
- `selected_concrete_skill`
- `handoff_artifacts`
- `execution_entry`

如果 workflow handoff 缺少 `domain_task_family`，`bio_domain` 可以做最小补判，但不要重新输出完整 workflow 入口分析。

## 与 coder / runtime / installer 的边界

- 需要写代码、配置、adapter、分析脚本或模型改造时，未来执行入口是 `onescience-skill -> onescience-coder`。
- 需要运行、提交、查状态、下载日志或诊断时，未来执行入口是 `onescience-skill -> onescience-runtime`。
- 需要安装依赖、准备远程环境或修复环境时，未来执行入口是 `onescience-skill -> onescience-installer`。
- 同一个规划阶段最多给出一个最可能的 `execution_entry`，不要展开完整执行链。

## scripts / templates / references 的使用边界

`bio_domain` 下的 templates 和 references 是领域资产，不是 role 层可直接执行动作。执行脚本不保留在 role 子树中，必须位于 coder/runtime/installer 资产层，或位于 `{onescience_path}/onescience` 下的 OneScience 仓库示例/工具目录。

- `references/`：可作为 role 层判断输入协议、风险点和交接字段的依据。
- `templates/`：只作为 handoff / manifest / request schema 的形状参考；role 不直接写入最终运行文件。
- `scripts/`：不得出现在 `bio_domain` role 子树中；role 只引用 coder/runtime/installer 或 OneScience 仓库下的脚本资产路径。

如果用户明确要求执行这些脚本，role 应把请求转成执行层 handoff，而不是在 role 层执行。

## 输出要求

规划或路由阶段至少输出：

- `bio_task_family`
- `onescience_model_related`
- `selected_category_skill`
- `selected_concrete_skill`
- `current_role`
- `role_chain`
- `handoff_artifacts`
- `execution_entry`
- `planning_only`

如果进入 OneScience 生信模型推理或开发，还应补：

- `onescience_model_family`
- `input_protocol`
- `source_anchors`
- `coder_assets_to_read`
- `preflight_or_validation_plan`

## 禁止事项

- 不要把传统生信 workflow 硬路由成 OneScience 模型改造。
- 不要把 leaf `SKILL.md` 当成顶层公开 skill。
- 不要在 role 层运行工具脚本，或把脚本重新放回 `bio_domain`。
- 不要在 checkpoint、输入协议、数据库版本或输出目标缺失时承诺可执行。
- 不要把远程运行和环境安装混入 role 层。
