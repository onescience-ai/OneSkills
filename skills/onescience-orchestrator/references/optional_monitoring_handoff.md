# 显式训练监控需求的编排与交接

本文只定义需求保持与步骤边界；API、配置、插入点、指标统计和事件判据通过 resource 契约召回，不在主控实现专业逻辑。不新增监控 expert 或独立监控 executor。

## 触发与操作

从用户原始请求、后续明确补充、已确认任务约束和持久化训练配置判断，不从模型卡推荐、自动模式或普通“训练”推导新增监控需求。

| 请求语义 | 操作/边界 |
|---|---|
| 训练模型，无监控要求 | 不追加监控接入或监控验收，保留脚本既有行为 |
| 接入监控、采集 Loss/学习率、监控训练过程 | 接入：根据现有 executor 能力拆分编码及获准的运行验证 |
| 查看已有训练曲线 | 查看：只读指定运行，不改代码、配置或启动训练/汇总 |
| 监控没有数据、诊断采集异常 | 诊断：先证据检查；源码修复、重跑分别重新选择 owner 并继承授权 |
| 文件变化监控、服务监控、普通进度查询 | 不自动解释成训练监控代码接入 |

上下文已明确的同义表达也适用；仅歧义会改变动作范围时澄清。“接入但不运行”必须继承 training_allowed=false；autonomous_mode 不覆盖此约束。后续用户撤销监控要求时更新未执行计划，不再接入；不擅自删除已有监控。

## 资源与计划

明确相关需求时，通过匹配的 resource 技能请求训练监控 Task、工具与验收知识。跨领域训练的模型资源仍使用原领域；共享监控知识单独查询 general，不把整个气象/生信任务误改为 general。资源不足则按现有补召回规则处理。

planner 未命中监控专家是正常情况；完成现有专家召回后，可沿既有 direct_step 形成步骤。不要新增虚构专家，也不要跳过 executor 能力盘点。已有 expert 的 proposal 如遗漏用户要求，融合时补齐或回交修订。

## 使用现有 handoff

将明确需求及来源写入 task_context.user_goal/constraints；操作范围、真实入口、目标环境、既有配置/运行、所需指标放 inputs。每步 required_outputs 和 completion_criteria 与用户范围一致。监控资源 path 只绑定，内容从 resource result 获取。

可在现有自由结构 inputs 中使用以下可选子对象；这不是新顶层协议，未要求监控时不强制添加：

```yaml
inputs:
  monitoring:
    operation: integrate  # integrate | inspect | diagnose
    request_evidence: "用户原话或已确认约束；不是模型卡建议"
    requested_metrics: [loss]
    # 配置、run/attempt、output_dir、world_size 等仅在已有事实时传递。
```

直接调用子技能时也可从用户明确请求建立本步输入，不因缺 monitoring 字段拒绝合法需求。继承原 training_allowed/completion_scope，不把 operation=integrate 当作训练授权。

编码 owner 交付代码/配置/接入说明与静态证据；运行 owner 处理预检、执行、同步/汇总及事件验证；查看按当前可用日志/分析 executor 能力选择，主控不硬编码新的 executor 链。环境修复沿现有窄委托。

## 状态闭环

结果进入 execution_result.artifacts/observation，并沿既有 observation 更新 Task State。分别保留代码接入、监控数据、训练作业、展示状态；推荐 observation.monitoring，但不新增 Task State 强制顶层字段。

- code_delivery 完成可以 success，采集/展示保持 not_run，不追加未获准训练。
- 用户要求实际监控时，不能用代码已生成、目录存在或预检通过代替事件证据。
- 数据 waiting/partial 不直接判训练失败，也不能据此自动重跑。依缺口重选步骤或如实报告。
- 未在 OneCode 取证展示则 display_status=not_run，不能宣称端到端展示通过。

具体有效点、指标统计与多 rank 验收规则由返回的监控验收资源决定，不在主控另设公式。

## 编码前的监控知识门槛

显式监控请求必须在编码前完成监控 Task、工具和验收正文的召回。使用资源技能的命名直查与本地降级规则；非空但无关的模型搜索结果仍算未命中。将已确认的 OneScience 监控组件要求和真实资源正文交给 executor，不能只转交“训练监控”关键词或路径。

缺少 Python 组件与缺少知识卡分别处理：接口资料充分时可以交付接入代码并标记运行未验证；禁止安装不等于允许取消接入。无有效监控契约时报告监控缺口，保留原训练，不自行批准原生 TensorBoard、替代 writer 或双后端回退。用户明确同意替代方案后才可改变路线。

## 监控知识与平台交接

通过 resource_retrieval_request 取得 pytorch-training-monitoring-integration、onescience-training-monitoring 和 training-monitoring-verification 的真实正文；OneCode 中还需取得 onecode-training-monitoring。消费 matched_resources[].content，不沿资源路径自行读 assets。

这些知识足以指导受支持版本的接入，不要求用户提供 OneScience 源码。编码阶段可按知识交付并标记运行 not_run；执行阶段由 installer 使用目标解释器查询 capabilities，按工具卡的兼容规则核对。缺版本证据或接口不匹配时报告知识缺口，不猜接口、不临时翻源码绕过版本契约。实际用户模型/训练源码仍按任务范围读取。

OneCode 项目通过 tasks/save_task 持久化 training_tasks 和 monitoring.requested，跨会话继承；生成阶段不登记运行。执行复用原 Bash/SSH/SCNet，平台分配身份，脚本读取身份并向指定清单路径报告，不引入新启动器。监控缺失只警告，训练业务异常正常传播，监控失败不改变训练退出码或触发重提。已有 OptionalTrainingMonitor 是可选接入辅助，不是 OneScience 公共类；不将技能脚本冒充已获授权的资源执行资产。

查看、分阶段诊断、来源修复与人工关联按 onecode-training-monitoring；已有缓存查看不要求远端在线，不因默认工作目录变化重绑历史数据。监控关闭、当前事件验证、平台采集和页面展示分别报告，未验证保持 not_run。

## 训练监控首次接入核对

代码生成完成前，必须逐项核对：ONECODE_RUN_ID/ONECODE_ATTEMPT_ID 被用于真实 MonitorConfig，输出为本 attempt 独立目录，初始化后和训练结束调用平台清单上报，业务退出码不受监控验收影响。不能只有 ONESC_MONITOR_CONFIG 的独立 UUID 回退、打印事件目录或原生 writer。通过资源取得完整平台 context/publish 示例，不自行省略身份读取。对代码做静态检查和监控专属异常路径检查，不为检查启动未获准训练。

训练成功后监控 waiting/error，只检查该 attempt 的关闭、事件与平台阶段，不重新训练。真实训练失败后的处理保留原有编排逻辑；重试通过 retry/previous_monitor_id 归入原运行。不能为了修复监控而换 new 重跑成功训练。模型计算、数据和优化器错误正常抛出；监控初始化、上报、关闭、verify 均须窄隔离，不能通过 raise 或 shell set -e 将成功训练改成失败。
