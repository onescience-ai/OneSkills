# Remote Status Template

本文件用于统一远程环境缺失、模糊或部分可用时的标准回复模板。

如果需要查看更贴近最终交付的成品示例，读取 `./remote_status_examples.md`。

## 通用字段

建议输出尽量包含以下字段：

- `status`
- `recognized`
- `missing`
- `can_continue_locally`
- `next_action`

可选补充：

- `reason`
- `suggestion`

## 模板 1：可以继续本地代码链路

适用场景：

- 用户未配置远程环境
- 当前任务只是实现、改造、生成代码

```yaml
status: ok
recognized:
  - 当前请求属于代码实现阶段
missing:
  - 远程环境未配置
can_continue_locally: true
next_action: onescience-coder
reason: 当前交付不依赖远程运行
suggestion: 如后续需要提交运行，再补充 Host、队列和运行配置
```

## 模板 2：远程信息部分缺失

适用场景：

- 已识别部分 Host 或平台信息
- 但当前阶段还缺关键字段

```yaml
status: partial_context
recognized:
  - 已识别目标平台为 DCU
  - 已识别一个候选 Host
missing:
  - 队列或分区
  - module / conda 约束
can_continue_locally: false
next_action: onescience-hardware
reason: 当前远程执行链路所需环境事实不完整
suggestion: 先补齐最小远程环境信息，再继续运行或安装阶段
```

## 模板 3：远程描述模糊，需要澄清

适用场景：

- 用户只说“某个 DCU 集群”“昆山环境”
- 无法唯一定位 Host 或环境约束

```yaml
status: need_clarification
recognized:
  - 用户提到目标环境为 DCU 集群
missing:
  - 具体 Host
  - 队列或分区
can_continue_locally: true
next_action: onescience-hardware
reason: 当前远程描述不足以唯一确定执行环境
suggestion: 请补充 Host 名称，或允许先读取 ~/.ssh/config 做归一化识别
```

## 模板 4：必须阻断远程阶段

适用场景：

- 用户要求直接运行、安装或远程测试
- 当前远程环境缺失导致无法继续

```yaml
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
reason: 当前阶段必须依赖远程环境事实和运行配置
suggestion: 先补齐远程环境与运行配置，再进入 onescience-runtime
```

## 使用要求

- 不要为了套模板而伪造 `recognized`
- `missing` 只列当前阶段真正缺的字段
- `can_continue_locally` 必须与当前任务目标一致
- `next_action` 应该是最小下一步，而不是完整流水线
