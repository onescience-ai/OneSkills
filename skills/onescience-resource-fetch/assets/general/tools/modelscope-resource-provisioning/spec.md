# modelscope-resource-provisioning — 规格说明

## 定位
`onescience-resource-fetch`（type=resource）对外暴露的资源供给原语：当任务需要的
模型权重 / checkpoint 或数据集在本地不存在时，从 ModelScope 拉取到本地统一缓存，
并返回可直接使用的绝对路径。只做「数据准备 / 资源物化」，不做格式转换、知识卡检索、
编码、训练推理、软件安装与凭据代管。

## 输入 / 输出契约
- 输入：统一 `resource_retrieval_request`（`intent=provision`）。
- 输出：统一 `resource_retrieval_result`，附 `provisioned_resources[]`，每项含
  `name / kind / repo_id / repo_id_source / local_path / files / bytes / selection /
  fetch`（`fetch.method` ∈ sdk|cli|git_lfs|cache_hit）。
- 调用方只消费返回内容，不直接读本技能 assets/ 或缓存目录内部结构。

## 覆盖范围
- 仓库类型：ModelScope 的 `dataset` 与 `model` 两类。
- 语义域：general（对 earth/biology/materials/cfd 等任务通用）。

## 边界与失败码
- 认证失败 → `authentication_failed`（不代管凭据，如实上报）。
- 检索无可选仓库 → `no_selectable_repo`；任务级规划为空 → `resource_plan_empty`。
- `--strict-name` 下多同名 → `repo_ambiguous`（不猜）。
- 下载成功但无可见文件 → `empty_payload`。
- 禁止用占位 / 模拟数据顶替未获取到的资源。
