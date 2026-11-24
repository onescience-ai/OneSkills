# 明确要求的训练监控编码步骤

用户原始请求、handoff 或已有持久化训练任务明确要求接入/修复训练监控时使用。普通训练不主动接入；已有监控保留。查看曲线不属于编码步骤，返回只读需求给调用方，不通过修改代码满足查看。

## 资源获取

按本技能元信息发现与 resource 调用规则，取得通用监控 Task、工具规格/使用知识和验收契约。共享监控知识查询 general；模型知识仍使用模型所在领域。只消费 resource result content，不凭路径读取 resource assets；本参考只提供编码流程，不替代资源中的 API 契约。

## 实现与静态检查

1. 找到真实训练入口，识别已有监控、框架、设备/rank、AMP/累积、Loss 来源和 checkpoint。已有接入满足需求就复用，避免重复 writer。
2. 将需求映射到真实插入点；复用共享脚本时优先在任务工作区适配，记录实际运行入口。修改/新生成代码使用资源中已确认 API，不猜函数或套用演示训练逻辑。
3. 保留原通信、参数更新/裁剪/unscale、Loss 统计、学习率调度、checkpoint 与早停语义。按资源对齐步数、指标 scope/weight 与恢复边界。
4. 交付配置与接入说明：真实入口、所需指标、统计范围/权重、hook、并行模式、监控恢复策略和运行限制。稳定任务要求保存到 onescience.json；每次执行身份由平台生成，不复用示例 attempt。
5. 对照改动审查调用位置、签名、配置、异常传播和语义不变。无法验证的公共边界明确 not_run；禁止以 smoke/dry-run 名义违反 training_allowed=false。

## 回执

登记代码、配置、接入说明的实际路径与校验信息。execution_result.observation 中分别报告代码静态核对与真实采集状态，可用 monitoring.code_status/data_status/display_status 描述；仅完成编码时 data_status/display_status=not_run。

需要目标环境验证时只建议下一步并返回调用方，不自行启动训练、安装依赖或串行调用 runtime。既有授权继续继承，但不因“接入监控”推导新的运行授权。

## 接入前检查与交付门槛

明确接入监控但未收到 Task、工具和验收真实正文时，先请求资源技能按 pytorch-training-monitoring-integration、onescience-training-monitoring、training-monitoring-verification 补召回，不直接编写 SummaryWriter 实现。目录返回无关结果不能替代知识卡。

按实际目标版本的公共接口生成 OneScience 监控接入。组件缺失时分别报告代码交付、训练执行与监控不可用；禁止安装不授权替代实现。用户未同意时，不自行引入原生 TensorBoard、替代 writer 或双后端回退。监控导入失败应记录告警并继续原训练；按契约报告组件 unavailable 和监控未完成，不改变训练结果，不自动重跑。暂不运行约束继续有效。

## 监控知识与平台交接

通过 resource_retrieval_request 取得 pytorch-training-monitoring-integration、onescience-training-monitoring 和 training-monitoring-verification 的真实正文；OneCode 中还需取得 onecode-training-monitoring。消费 matched_resources[].content，不沿资源路径自行读 assets。

这些知识足以指导受支持版本的接入，不要求用户提供 OneScience 源码。编码阶段可按知识交付并标记运行 not_run；执行阶段由 installer 使用目标解释器查询 capabilities，按工具卡的兼容规则核对。缺版本证据或接口不匹配时报告知识缺口，不猜接口、不临时翻源码绕过版本契约。实际用户模型/训练源码仍按任务范围读取。

OneCode 项目通过 tasks/save_task 持久化 training_tasks 和 monitoring.requested，跨会话继承；生成阶段不登记运行。执行复用原 Bash/SSH/SCNet，平台分配身份，脚本读取身份并向指定清单路径报告，不引入新启动器。监控缺失只警告，训练业务异常正常传播，监控失败不改变训练退出码或触发重提。已有 OptionalTrainingMonitor 是可选接入辅助，不是 OneScience 公共类；不将技能脚本冒充已获授权的资源执行资产。

查看、分阶段诊断、来源修复与人工关联按 onecode-training-monitoring；已有缓存查看不要求远端在线，不因默认工作目录变化重绑历史数据。监控关闭、当前事件验证、平台采集和页面展示分别报告，未验证保持 not_run。

## 训练监控首次接入核对

代码生成完成前，必须逐项核对：ONECODE_RUN_ID/ONECODE_ATTEMPT_ID 被用于真实 MonitorConfig，输出为本 attempt 独立目录，初始化后和训练结束调用平台清单上报，业务退出码不受监控验收影响。不能只有 ONESC_MONITOR_CONFIG 的独立 UUID 回退、打印事件目录或原生 writer。通过资源取得完整平台 context/publish 示例，不自行省略身份读取。对代码做静态检查和监控专属异常路径检查，不为检查启动未获准训练。

训练成功后监控 waiting/error，只检查该 attempt 的关闭、事件与平台阶段，不重新训练。真实训练失败后的处理保留原有编排逻辑；重试通过 retry/previous_monitor_id 归入原运行。不能为了修复监控而换 new 重跑成功训练。模型计算、数据和优化器错误正常抛出；监控初始化、上报、关闭、verify 均须窄隔离，不能通过 raise 或 shell set -e 将成功训练改成失败。
