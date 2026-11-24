# 训练监控验收契约

## 独立判定的四类状态

| 类别 | 状态示意 | 证据 |
|---|---|---|
| 代码接入 | passed / partial / failed / not_run | 真实入口、调用位置、配置与静态语义核对 |
| 监控数据 | available / partial / waiting / unsupported / error / not_run | 当前 attempt 的原始 verify 报告及补充事件检查 |
| 训练作业 | 沿用进程/调度状态 | PID/作业号、退出码、调度与运行日志 |
| OneCode 展示 | passed / failed / not_run | 已绑定当前 run/attempt 的展示取证 |

这些是 observation 中的本任务结果，不新增顶层执行状态枚举。execution_result.status 仍为既有 success/partial/failed/blocked 等；代码交付和真实采集分别判断。

## 身份与事件

配置、attempt.json、verify 报告中的 run_id/attempt_id 应与当前任务一致；同时记录所在主机、输出绝对路径、训练进程/作业身份。多 rank 检查 world_size、源完整性和当前 active 汇总代；不能只核对目录名或历史事件存在。

必需训练指标至少两个有限值、严格递增的有效 step 点；采样间隔与真实更新数要能支持这些点。没有足够训练步数时如实 waiting/partial，不伪造点或擅自延长训练。

当前 api=1/contract=1.0 的 verify 主要检查 manifest 声明的 required train loss/window 指标。它不证明 Loss 公式、梯度 hook 位置、当前作业存活，也不自动验证所有验证指标、吞吐、学习率或诊断。用户要求这些指标时必须补充读取对应事件/tag_map、有效值、step 和 component 状态；不能把 verify ok 当作全部指标可用。

## 语义保持

编码审查确认：原通信次数、参数更新、AMP/累积规则、Loss/权重、原 scheduler/checkpoint/早停未被监控改变。已有全局值不再次归约；不能把 rank0 本地值标作全局。模型续训与监控续训分别判断；未经匹配的状态不恢复监控步数。

## 完成边界

- 用户只要求代码接入：源码、配置、接入说明及约定静态检查完成可 success；采集/展示 not_run，不要求训练。
- 用户要求实际监控：必需指标与当前身份需有真实证据；缺失项保留 partial/waiting/unsupported，按用户要求决定是否继续修复。
- 用户只要求查看：只读结果及缺失原因即可，不执行训练/聚合/改配置来制造数据。
- 示例工程验证必须标记 engineering_validation，不进入科研结论；监控通过不能证明模型收敛、正确性或论文复现。

## 宿主与独立知识边界

OneScience 公共 API 与接入示例通过 tools/onescience-training-monitoring 的 spec/usage 召回，无需源仓库。OneCode 项目另召回 contracts/onecode-training-monitoring，核对持久化配置、平台身份、清单、独立来源、缓存权限和分阶段诊断；不把这些平台规则当成 OneScience 公共 API。训练业务源码仍由相应 executor 按任务范围处理。

## 组件状态的结构

当前文件后端 verify.component_status 来自 attempt.json.components，按 rank 字符串索引（如 "0"），每项包含 components、diagnostics、dropped、closed、step 等，不是一个平铺的组件布尔表。按实际 rank 逐项核对；base 的 gradient/latency/memory=false 是配置结果，不直接判失败。
