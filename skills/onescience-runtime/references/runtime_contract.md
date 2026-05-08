# Runtime Contract

本文件用于说明 `onescience-hardware`、`onescience-coder`、`onescience-runtime` 三层之间的交接关系，以及 `onescience.json` / `tpl.slurm` 中各字段的职责归属。

## 先后顺序

远程运行类任务默认按下面顺序推进：

1. `onescience-hardware`
2. `onescience-coder`
3. `onescience-runtime`
4. `onescience-debug`（按需）

不要把 `onescience-runtime` 当成硬件探测层，也不要让 `onescience-hardware` 直接承担运行提交主职责。

## 三层职责

### `onescience-hardware`

负责回答“运行环境是什么”：

- 用哪个 Host
- 是 DCU、GPU 还是 CPU
- 可用队列或分区是什么
- 需要哪些 module / conda 约束
- 数据、模型、工作目录的远端约定是什么

输出结果应形成给 `onescience-runtime` / `onescience-installer` 使用的“完整硬件画像”，并进一步提炼给 `onescience-coder` 的“代码生成交接摘要”。

### `onescience-coder`

负责回答“代码要怎么写”：

- 数据读取入口
- 模型与组件实现
- 训练 / 推理入口脚本
- 基于交接摘要实现设备、路径、批大小、分布式方式相关的适配点

它不负责连接远程环境，也不负责提交作业，也不直接参与硬件探测。

### `onescience-runtime`

负责回答“代码怎么跑起来”：

- 读取 `onescience.json`
- 读取 `tpl.slurm`
- 结合完整硬件画像生成最终运行脚本
- 创建远程连接
- 传输脚本
- 执行运行命令或提交作业

## `onescience.json` 字段归属

### 主要由 `onescience-hardware` 感知后校准

- `runtime.cluster.partition`
- `runtime.cluster.gpu_type`
- `runtime.modules`
- `runtime.conda.env_name`
- `runtime.script.env_vars.ONESCIENCE_DATASETS_DIR`
- `runtime.script.env_vars.ONESCIENCE_MODELS_DIR`

这些字段通常和目标平台强相关，优先以完整硬件画像为准，再由用户或运行配置确认。

### 主要由 `onescience-coder` 决定

- `runtime.script.code_path`
- `runtime.script.job_name`

因为这两个字段直接对应生成出的训练 / 推理入口脚本和任务语义。

### 主要由 `onescience-runtime` 决定或补齐

- `runtime.script.path`
- `runtime.script.generate`
- `runtime.script.template`

这些字段服务于运行脚本生成和提交动作本身。

### 需要用户或任务共同决定

- `runtime.cluster.nodes`
- `runtime.cluster.gpus_per_node`
- `runtime.cluster.cpus_per_task`
- `runtime.cluster.time_limit`
- `runtime.cluster.memory`

这些是资源申请策略，不应只靠某一层单独猜测。

## `tpl.slurm` 的归属

- `tpl.slurm` 属于固定模板资产
- 本仓库内的标准模板存放在 `skills/onescience-runtime/assets/tpl.slurm`
- 用户真正运行任务时，应把该模板复制到目标工程根目录，再作为项目级 `tpl.slurm` 使用
- 模板结构本身不应由 `onescience-hardware` 修改
- 模板变量替换由 `onescience-runtime` 完成
- 模板中引用的脚本路径、环境变量和值，来自 `onescience.json` 与完整硬件画像的合并结果

## 交接清单

### `onescience-hardware -> onescience-coder`

至少传递：

- `device_type`
- `distributed_mode`
- `runtime_mode`
- 是否需要设备适配
- 是否需要分布式入口
- 是否需要路径环境变量
- 代码实现必须保留的备注信息

### `onescience-coder -> onescience-runtime`

至少传递：

- 生成的代码入口文件
- 训练或推理脚本路径
- 作业名称建议
- 是否需要分布式或特殊设备适配

### `onescience-runtime -> onescience-debug`

至少传递：

- 作业 ID
- 远端脚本路径
- 日志路径
- 实际运行命令
- 关键运行失败信息

`onescience-debug` 在需要远程执行事实时，应优先读取这些运行产物或回到完整硬件画像；不要只凭给 `onescience-coder` 的代码生成交接摘要推断远程执行环境。

## 常见错误

### 错误 1：跳过硬件感知直接写远程适配代码

后果：

- 队列写错
- module 写错
- 路径与平台不匹配

### 错误 2：让 `onescience-hardware` 直接负责提交作业

后果：

- 配置解析与提交逻辑耦合
- 分层职责不清

### 错误 3：让 `onescience-runtime` 猜测设备约束

后果：

- 运行脚本和真实环境脱节
- 资源申请错误

## 使用建议

- 当你不确定某个字段应该由谁决定时，先问自己：
  - 这是“环境事实”吗？如果是，优先给 `onescience-hardware`
  - 这是“代码实现选择”吗？如果是，优先给 `onescience-coder`
  - 这是“运行与提交动作”吗？如果是，优先给 `onescience-runtime`
- 当 `coder` 只需要知道“代码该怎么适配”时，优先传递精简的代码生成交接摘要，而不是整份完整硬件画像
