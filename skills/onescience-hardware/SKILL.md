---
name: onescience-hardware
description: OneScience 硬件感知技能。用于在代码生成前识别远程 Host、DCU/GPU 类型、队列、模块环境和运行约束，并把结果拆分为给 `onescience-coder` 的代码生成交接摘要，以及给 `onescience-runtime` / `onescience-installer` 使用的完整硬件画像。
---

# OneScience 硬件感知

这个 skill 只负责“先弄清楚目标硬件是什么样”，不负责生成业务代码，也不负责提交作业。

当你需要完整硬件画像字段、代码生成交接摘要字段或输出格式时，读取：

- `./references/hardware_profile.md`
- `./references/codegen_handoff.md`
- `../../references/remote_fallback.md`

## 适用场景

当任务涉及以下任一动作时，优先使用本 skill：

- 读取本机 `~/.ssh/config`
- 确认应该运行在哪个远程 Host
- 判断目标平台是 DCU、GPU 还是普通 CPU
- 确认可用队列、模块环境、conda 激活方式和路径约定
- 识别代码生成时必须遵守的硬件约束
- 在运行或安装前为下游技能提供完整硬件画像

## 输入

调用本 skill 时，至少明确这些信息：

1. 任务准备运行在哪类环境：DCU、GPU、SLURM、远程主机中的哪一种
2. 是否已有固定 Host、队列或项目环境
3. 后续代码生成最关心哪些硬件信息
4. 后续运行最关心哪些连接与环境信息

## 执行流程

1. 使用 `cat ~/.ssh/config` 读取用户本机 SSH 配置。
2. 解析可用 Host：
   - 没有 Host：停止并提示用户先配置
   - 只有一个 Host：直接使用
   - 有多个 Host：要求上游技能或用户明确选择
3. 如有必要，执行**轻量只读探测**，确认：
   - 平台类型
   - 队列或分区名称
   - 模块与 conda 可用性
   - 常用数据、模型和工作目录约定
4. 将探测结果整理成后续运行与安装阶段可复用的完整硬件画像。
5. 再从完整硬件画像中提炼一份“代码生成交接摘要”交给 `onescience-coder`。
6. 把完整硬件画像交给 `onescience-runtime` / `onescience-installer`，用于连接远程环境、生成脚本、提交或安装。

完整硬件画像字段、代码生成交接摘要字段和输出建议见 `./references/hardware_profile.md`。

## 约束

- 不要在工作区里搜索 `~/.ssh/config`
- 不要替业务技能决定模型、数据、训练逻辑或安装领域
- 不要静默选择多个 Host 里的某一个
- 不要隐式修改用户的 SSH 配置
- 不要把上传文件、提交作业、运行脚本当作本 skill 的默认职责
- 若执行远程探测，优先使用只读且低风险命令
- 当用户只给出模糊远程描述时，先尽量归一化识别；补不齐时只追问最小缺失信息

## 与其他技能的关系

- `onescience-coder`：在开始编码前只读取本 skill 输出的“代码生成交接摘要”，不直接处理硬件探测细节
- `onescience-runtime`：在代码生成后基于本 skill 的完整硬件画像创建远程连接、运行脚本并提交作业
- `onescience-installer`：在环境安装前基于本 skill 的完整硬件画像确定 Host、module、conda 和路径约束
- `onescience-debug`：若排查结果与硬件环境强相关，可先回到本 skill 补齐上下文
