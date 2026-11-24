# 明确监控需求的运行与诊断

用户/交接明确提出训练监控验证、已有曲线查看或采集诊断，或已有持久化训练任务要求监控时使用；普通训练不主动接入、不强制监控验收。区分 integrate/inspect/diagnose；接入但禁止训练时不执行训练或聚合来制造指标。已有监控保持原行为。

先按元信息发现契约选择匹配的 type=resource 技能，通过 resource_retrieval_request 获取 general 中的监控 Task、工具使用与验收知识，取得 resource_retrieval_result 后继续；content 不足补召回，不能直读 assets。本参考只定义运行职责，不复制公共 API 或加权规则。

## discover

接入/运行验证沿用 runsite 配置检查。定位真实入口、目标训练环境、配置、run/attempt/output_dir、world_size 和用户所需指标；远端配置路径、同步目标与本地展示路径分别记录，不把远端绝对路径直接当本地路径。

只读查看/诊断已有数据时，不因执行流程默认进入业务 execute 或安装/修复：只做本步获准的文件/日志与事件检查，不修改站点、监控配置或已有数据，不启动训练/汇总；需要变化时回报缺口并由调用方按授权安排。无法在只读权限内完成站点检查时报告限制，不静默写配置。

## preflight

环境就绪检查仍完整委托 installer，传入监控资源中列出的公共 API/契约兼容性、torch/TensorBoard 和所需诊断依赖，保留 capabilities 原始报告。runtime 不另建环境探测实现，只消费 readiness。环境修复按原授权；只有查看需求时不自动安装。

环境 readiness 成立后，依据召回的使用知识执行本任务配置/接入声明 check；环境检查通过不代替配置检查。业务必需项的阻断错误先修复；仅监控配置或组件错误单列 unavailable/warning，不阻断训练；warning 对应哪些指标缺失、是否仍能满足本次需求要写明。只读需求不用有副作用的写探针。

## execute

继承原 preflight 硬门禁与执行通道，按运行授权启动实际入口。源码/业务配置缺失返回调用方，不由 runtime 写训练代码或业务配置。

多 rank 根据资源要求由运行/作业管理侧安排一个外部汇总任务，记录唯一身份、日志、停止条件和源文件同步路径，不能每个 rank 启动或插进训练循环。训练无论成功失败，最终同步封存文件后结束汇总；汇总失败报告原因，不遗留无限后台任务。单 rank 不增加汇总。

运行中切换配置仅在明确请求范围内执行，遵守资源的可变字段限制；不擅自更换身份、开启 full 或延长训练。

## diagnose 与验收

按资源验收契约执行真实事件 verify，并补查其未覆盖而用户要求的指标。保留原命令、解释器、主机、退出码、报告和事件位置。waiting 先查采样、flush、源封存/同步、汇总代与训练状态，不自动重跑。

没有指标不等于训练失败；verify ok 不等于验证指标/梯度/展示均通过。数据、作业、代码接入和展示状态分别回传；没有展示证据时保持 not_run。缺 rank 不宣称全局完整；版本/依赖/配置/写入/聚合错误按真实原因分类。

源码问题只回 observation/recommendation，由 orchestrator 重选 coder；runtime 不越权改代码或自行选择新的业务 executor。

## 正式回执

原有 Output Contract 不变。监控相关步骤在 execution_result.artifacts 登记原始报告和数据位置，observation.monitoring 可包含 operation、run_id、attempt_id、output_dir、requested_metrics、available_metrics、missing_metrics、code_status、data_status、training_state、display_status、evidence、limitations。未知值标未知/not_run，不填模拟结果。

## 监控知识与平台交接

通过 resource_retrieval_request 取得 pytorch-training-monitoring-integration、onescience-training-monitoring 和 training-monitoring-verification 的真实正文；OneCode 中还需取得 onecode-training-monitoring。消费 matched_resources[].content，不沿资源路径自行读 assets。

这些知识足以指导受支持版本的接入，不要求用户提供 OneScience 源码。编码阶段可按知识交付并标记运行 not_run；执行阶段由 installer 使用目标解释器查询 capabilities，按工具卡的兼容规则核对。缺版本证据或接口不匹配时报告知识缺口，不猜接口、不临时翻源码绕过版本契约。实际用户模型/训练源码仍按任务范围读取。

OneCode 项目通过 tasks/save_task 持久化 training_tasks 和 monitoring.requested，跨会话继承；生成阶段不登记运行。执行复用原 Bash/SSH/SCNet，平台分配身份，脚本读取身份并向指定清单路径报告，不引入新启动器。监控缺失只警告，训练业务异常正常传播，监控失败不改变训练退出码或触发重提。已有 OptionalTrainingMonitor 是可选接入辅助，不是 OneScience 公共类；不将技能脚本冒充已获授权的资源执行资产。

查看、分阶段诊断、来源修复与人工关联按 onecode-training-monitoring；已有缓存查看不要求远端在线，不因默认工作目录变化重绑历史数据。监控关闭、当前事件验证、平台采集和页面展示分别报告，未验证保持 not_run。

## 训练监控首次接入核对

代码生成完成前，必须逐项核对：ONECODE_RUN_ID/ONECODE_ATTEMPT_ID 被用于真实 MonitorConfig，输出为本 attempt 独立目录，初始化后和训练结束调用平台清单上报，业务退出码不受监控验收影响。不能只有 ONESC_MONITOR_CONFIG 的独立 UUID 回退、打印事件目录或原生 writer。通过资源取得完整平台 context/publish 示例，不自行省略身份读取。对代码做静态检查和监控专属异常路径检查，不为检查启动未获准训练。

训练成功后监控 waiting/error，只检查该 attempt 的关闭、事件与平台阶段，不重新训练。真实训练失败后的处理保留原有编排逻辑；重试通过 retry/previous_monitor_id 归入原运行。不能为了修复监控而换 new 重跑成功训练。模型计算、数据和优化器错误正常抛出；监控初始化、上报、关闭、verify 均须窄隔离，不能通过 raise 或 shell set -e 将成功训练改成失败。
