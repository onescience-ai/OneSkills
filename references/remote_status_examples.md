# Remote Status Examples

本文件提供远程环境异常场景下的最终推荐输出示例。

## 示例 1：纯代码任务，但没有远程环境

适用场景：

- 用户只要求实现、改造或生成代码
- 当前没有远程配置

```yaml
task_type: 代码实现
reason: 当前目标是生成代码，不依赖远程运行
status: ok
recognized:
  - 当前请求属于代码实现阶段
  - 尚未进入远程运行链路
missing:
  - 远程环境未配置
can_continue_locally: true
next_action: onescience-coder
```

## 示例 2：远程描述模糊

适用场景：

- 用户只说“昆山 DCU”“某个 GPU 集群”
- 还不能唯一确定 Host 或队列

```yaml
task_type: 远程环境感知
reason: 用户提供了远程环境线索，但不足以唯一定位执行环境
status: need_clarification
recognized:
  - 用户提到目标环境为 DCU 集群
missing:
  - 具体 Host
  - 队列或分区
can_continue_locally: true
next_action: onescience-hardware
```

## 示例 3：运行任务被阻断

适用场景：

- 用户要求直接提交作业或远程运行
- 当前远程环境事实或运行配置不完整

```yaml
task_type: 远程运行
reason: 当前阶段必须依赖完整硬件画像与运行配置
status: blocked
recognized:
  - 当前请求属于远程运行阶段
missing:
  - Host
  - 完整硬件画像
  - onescience.json
  - tpl.slurm
can_continue_locally: false
next_action: onescience-hardware
```

## 示例 4：远程环境部分可识别，但仍缺关键字段

适用场景：

- 已识别一个候选 Host 或平台类型
- 但还不能安全进入运行 / 安装阶段

```yaml
task_type: 远程环境补全
reason: 当前远程执行链路所需环境事实不完整
status: partial_context
recognized:
  - 已识别目标平台为 DCU
  - 已识别一个候选 Host
missing:
  - 队列或分区
  - module / conda 约束
can_continue_locally: false
next_action: onescience-hardware
```

## 使用建议

- 优先复用字段结构，不要随意增删核心字段
- `recognized` 只写已经确认的信息
- `missing` 只写当前阶段真正缺的内容
- `next_action` 指向最小下一步，而不是完整链路
