# Codegen Handoff

本文件定义 `onescience-hardware -> onescience-coder` 的最小交接面。

目标是让 `onescience-coder` 不直接处理硬件探测逻辑，只消费一份稳定、精简的“代码生成交接摘要”。

## 为什么需要这层抽象

`onescience-hardware` 负责识别：

- Host
- 平台类型
- 队列 / 分区
- module / conda 约束
- 路径约定

这些信息很多都属于“环境事实”，不应该让 `onescience-coder` 直接参与探测、判断和选择。

`onescience-coder` 真正关心的，是这些环境事实对代码实现有什么影响。

## 交接格式

建议把交接摘要整理成下面几类信息：

### 1. 设备与运行模式

- `device_type`: `dcu` / `gpu` / `cpu`
- `distributed_mode`: `single` / `multi_gpu` / `multi_node`
- `runtime_mode`: `slurm` / `direct_remote`

### 2. 代码必须适配的约束

- `needs_distributed_entry`
- `needs_device_guard`
- `needs_path_env`
- `needs_cluster_friendly_io`

这些字段回答的是“代码里要不要处理这件事”，而不是“远程环境怎么探测出来的”。

### 3. 运行期路径约定

- `dataset_dir`
- `models_dir`
- `work_dir`

如果这些路径只在运行脚本里使用，也可以只传“是否依赖路径环境变量”，不必把全部远端细节塞给 `coder`。

### 4. 备注信息

- `notes_for_codegen`

例如：

- “入口脚本需要兼容 DCU 环境变量”
- “不要把数据集路径写死为本地绝对路径”
- “训练入口需保留分布式参数占位”

## `onescience-coder` 应该怎么使用

`onescience-coder` 只需要做这几件事：

1. 读取交接摘要
2. 判断代码入口是否需要设备适配
3. 判断脚本是否需要分布式或环境变量占位
4. 在实现中保留与运行层兼容的接口

不要在 `coder` 中重新：

- 解析 SSH 配置
- 选择 Host
- 判断队列
- 探测 module / conda

## `onescience-hardware` 应该怎么输出

如果信息很多，优先输出对代码真正有影响的部分，而不是完整硬件清单。

推荐优先级：

1. 设备类型
2. 运行模式
3. 是否分布式
4. 是否依赖环境变量路径
5. 入口脚本必须保留的适配点

## 示例

```yaml
codegen_handoff:
  device_type: dcu
  distributed_mode: single
  runtime_mode: slurm
  needs_distributed_entry: false
  needs_device_guard: true
  needs_path_env: true
  needs_cluster_friendly_io: true
  dataset_dir: /public/share/.../onedatasets
  models_dir: /public/share/.../onemodels
  work_dir: /home/user/project
  notes_for_codegen:
    - 不要写死本地数据路径
    - 入口脚本需兼容 DCU 环境
```
