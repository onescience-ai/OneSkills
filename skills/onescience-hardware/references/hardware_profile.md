# Hardware Profile

本文件用于定义 `onescience-hardware` 输出的“完整硬件画像”结构，以及它与“代码生成交接摘要”的关系。

## 完整硬件画像

完整硬件画像主要给 `onescience-runtime` / `onescience-installer` 使用，建议至少包含：

- `host`
- `platform_type`
- `partition`
- `modules`
- `conda_env`
- `dataset_dir`
- `models_dir`
- `work_dir`

如果任务还依赖额外环境事实，也可以补充：

- 登录节点或执行节点约束
- shell 初始化方式
- 数据、模型、日志目录约定
- 远端工作路径约定

## 代码生成交接摘要

代码生成交接摘要只给 `onescience-coder` 使用，建议进一步收口为：

- `device_type`
- `distributed_mode`
- `runtime_mode`
- `needs_distributed_entry`
- `needs_device_guard`
- `needs_path_env`
- `needs_cluster_friendly_io`
- `notes_for_codegen`

核心原则：

- 完整硬件画像回答“远程环境事实是什么”
- 代码生成交接摘要回答“代码应该如何适配”

## 输出建议

至少给出：

1. 使用的 Host
2. 目标硬件或平台类型
3. 关键运行约束：队列、module、conda、路径、设备类型
4. 对代码生成的影响
5. 对后续 `onescience-runtime` / `onescience-installer` 的影响

## 轻量探测建议

如有必要，可执行轻量只读探测，确认：

- 平台类型
- 队列或分区名称
- module 与 conda 可用性
- 常用数据、模型和工作目录约定

优先使用低风险、只读命令，不要把上传文件、提交作业、运行脚本当作本 skill 的默认职责。
