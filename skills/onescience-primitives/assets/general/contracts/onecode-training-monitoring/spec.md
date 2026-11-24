# OneCode 训练监控平台接入契约

本卡只描述 OneCode 平台协议，不是 OneScience API。通用指标调用需另召回 tools/onescience-training-monitoring。运行清单 onecode.training/v1 与数据库记录 schemaVersion=3 是不同协议，不可混改。

来源版本与核对文件见 source.json；生成和执行无需访问平台或 OneScience 源码。保留现有工具实际可用性，不虚构工具动作。

## 项目配置、执行与身份


### 训练优先与持久化配置

训练是否成功以真实进程退出或调度器结果为准；监控是尽力接入的附加能力。缺少 OneScience、配置不完整、连接不可达、初始化、写指标、目录上报或关闭失败，都只记录监控告警，不阻止训练、不改变训练退出码，也不自动重新提交。模型、数据、forward/backward、优化器与 checkpoint 的真实异常仍正常失败，禁止把训练循环放进监控异常捕获中。不要自动更换为原生 TensorBoard、替代 writer 或双后端。

生成监控代码时交付训练脚本、业务训练配置及监控适配代码，并通过现有 training_monitor 的 tasks/save_task 维护项目 onescience.json。先读取 revision，再用 expectedRevision 合并 training_tasks：稳定 id、title、真实 entrypoint、config、execution_entrypoints（实际包装脚本），以及 monitoring:{requested:true}。collectionTarget 保存已核对的账号采集连接引用，工具只合并本任务和 runtime.monitoring.execution_target_ref，保留其它 owner 字段。旧 monitoring.required=true 按“请求监控”兼容读取，不再表示训练门禁；保存任务时转为 requested。配置中不存每次运行身份、作业号、凭据或运行结果。只生成代码时不登记运行，不启动训练。

新会话读取已有任务配置即可继承监控请求，用户无需再次在 prompt 写“接入监控”。普通安装、下载、预处理、检查和 verify 不登记为训练。入口更名/删除同步维护任务，revision 冲突重新读取合并。未登记、没有既有监控要求的普通脚本不因名字或 import 字符串自动关联。

### 现有执行入口与当前运行身份

沿用现有 shell、SSH、SCNet 工具和权限机制；不创建另一套执行入口。可引用 onecode_execution={task_ref:任务key,config_path:实际onescience.json路径}，也可由已登记的实际执行入口恢复请求。代码生成与执行可以同轮、跨轮或跨会话；不额外增加应用确认，但“暂不运行”等原始限制必须遵守。

区分命令发起位置、实际训练环境、采集连接：OneCode 本地 Bash 里的 SSH 命令在远端训练，不能把本地当成采集目标。平台只对可确认的执行形态自动准备监控：原本地/SSH执行、单条 literal SSH 远端命令及原 SCNet 提交。连接通过账号已有目标的主机、用户、端口唯一匹配，仍校验访问范围；不能把 DCU、队列或 region 当成文件连接，也不能取消目标校验。不可识别的嵌套包装、动态展开、多跳或不确定目标保留原训练命令，监控报告 unavailable，不扫描任意脚本源码猜执行链。

监控准备成功时，平台为当前调用分配 task/run/attempt/monitor 身份及唯一 ONECODE_RUNTIME_MANIFEST，并持久化当前 session、配置版本和脱敏快照。在现有传输边界注入 ONECODE_TASK_ID、ONECODE_RUN_ID、ONECODE_ATTEMPT_ID、ONECODE_MONITOR_ID、ONECODE_EXECUTION_TARGET、ONECODE_RUNTIME_MANIFEST、ONECODE_REGION 等完整上下文；支持的直接 SSH 形态把变量注入远端命令。调度脚本需保持已有环境继承（例如 sbatch 默认/--export=ALL），不可自行丢弃或重写这些变量。对自定义包装脚本不声称自动跨越隐藏传输边界；监控不可用不影响原训练。

监控准备失败时返回 ONECODE_EXECUTION_RESULT 的监控 warning，继续执行原训练一次。依原工具返回保留真实作业号、输出和退出码，不把监控失败当提交失败，不据此重跑训练。此前提交响应不明的同一任务必须先核对实际作业，禁止猜测未提交后重试。原调用仍由已有权限、取消机制与执行编排负责。

### 训练代码的可选监控边界

按通用工具卡的可选监控边界隔离调用；已有 OptionalTrainingMonitor 可复用，但它是项目/技能辅助而不是 OneScience 公共 API，不要求复制新的执行资产。OneScience 的 import、MonitorConfig、MetricSpec 和 create_monitor 放进 factory 内部；factory 只做监控初始化，不能包含模型/数据初始化或训练计算。用真实公共 API，不猜签名。

有完整平台身份时，以 ONECODE_RUN_ID/ONECODE_ATTEMPT_ID 配置 OneScience，创建当前 attempt 独立目录；所有 rank 共用身份，不能每个 rank 自行产生不同 attempt。若完全独立运行，允许使用训练配置中的显式 OneScience 身份采集本地数据，但不得伪造平台绑定。没有完整平台 task/run/attempt/target/manifest 时，跳过平台报告并记录告警；禁止写空字符串身份的 runtime.json，禁止自行默认到共享 $ROOT/runtime.json。

使用适配器的 record_train/record_validation、start_phase/end_phase、flush/close 等监控调用。with monitor.stage(...) 仅包围测时，训练体异常必须继续向外传播。Loss 使用训练已有且口径正确的 scalar，不因监控改变通信、梯度、AMP、优化器、checkpoint 或早停逻辑。生命周期以 finally/with 关闭；close 的 closed/error/pending_records 与训练结果分别报告。组件缺失且禁止安装时，保留训练执行、监控标 unavailable，不能声称监控完成。

rank 0 初始化真实 writer 后，通过平台接入辅助上报真实绝对目录；裸 TrainingMonitor 没有 publish_runtime 方法。已有 OptionalTrainingMonitor 提供该辅助，新生成代码可使用本卡 usage 的等价清单上报片段。写入位置仅为实际执行环境注入的 ONECODE_RUNTIME_MANIFEST；原子写 onecode.training/v1、kind=training、taskId/runId/attemptId、executionTargetRef、eventRoot，以及有值时的真实 SLURM_JOB_ID/region。eventRoot 指向当前 attempt 中实际事件所在目录或其精确独立根目录；多 rank 不读取旧汇总代，不将 sources 原始分段当 TensorBoard 事件。不得按 latest、ls|tail、名称相似或旧日志选择目录。

### 当前采集、人工关联与验收

平台只轮询本次执行分配的精确运行报告，验证身份、目标、作业与路径后接入已有增量同步器和 TensorBoard。输出中的运行事件也只能更新当前调用已分配的身份；读取旧日志/报告、下载历史文件、服务重启都不能新增历史关联。重启仅继续已有记录的采集，不重放训练提交。

此前未关联的训练默认不处理。只有用户明确要求人工关联指定训练时，才使用 declare/bind 并提供真实 task/run/attempt、作业号、目标和实际事件目录；缺证据就报告缺口，不发明身份、不重训、不按目录猜测。status 可只读查询同工作区已存在的记录，但查询不是关联授权。

新训练默认新 run、新 attempt。用户明确重试/续训时使用 mode=retry/resume 与 previous_monitor_id；须先确认此前作业终止。retry 保留 run、新建 attempt；resume 还需实际 checkpoint 和原训练恢复参数。监控失败不自动触发这些动作。

页面只展示确认提交/实际执行的训练，准备失败或未提交候选、普通作业和非训练任务不展示；已确认训练可以显示等待目录、无数据或采集失败。训练状态、目录绑定、事件字节、有效指标和页面展示分别验收。当前 attempt 的真实 verify 不能替代平台采集验证，平台关联也不能替代训练成功。无展示证据标 not_run；没有监控数据不推断训练失败。

## 执行与来源分离

执行目标保存提交事实，sources.metrics 指明指标读取连接和 eventRoot，sources.status 指明状态连接、scheduler/jobRef，sources.runtime 按需指明精确清单连接与 manifestPath。不能把三者等同于当前默认工作目录。任务配置 collectionTarget 是现有兼容入口，不表示可任意改写已有运行来源。

当前连接按账号引用管理；默认工作目录改变不重写已批准来源范围。凭据更新与主机/用户/端口目标改变分开处理，实际目标改变需重新确认，不按名称猜测换绑。来源授权由平台实施，Agent 不绕过校验。

## 缓存查看、诊断与修复

查看已有缓存只检查账号/工作区历史访问权限与缓存存在，不要求远端在线；继续采集则需要有效来源授权和连接。断网、改默认目录、删除连接不应被解释为缓存必然消失；权限撤销或缓存清理是另一类问题。

tracking 查询作业状态、runtime 确认清单、metrics 采集独立诊断，分别看 lastSuccessAt/lastError/nextAt。状态查询失败不推断训练失败或采集失败，采集失败保留已有曲线；页面读取错误不等于远端没有事件。

control.paused 是持久意图：错误恢复不能解除暂停，暂停不停止训练。finalization 有收尾期限，超期明确报告数据可能不完整；已完成记录不因重启或新任务提交重新激活。租约、退避和过期结果保护属于平台，不由 Agent 再起后台同步器。

有明确修复授权时使用平台来源编辑入口；HTTP 契约为 POST /platform/training-monitors/:id/sources，带 expectedSourceRevision、reason 及完整所需 metrics/status/runtime 来源集合（不是局部字段 patch，省略项可能被移除）。冲突重新读取，不改数据库。采集后禁止换接另一份指标流；不得误将该路由宣称为 training_monitor 已暴露的工具动作。工具未提供时报告能力缺口或由用户在页面操作。

## 训练退出结果与重试

当前身份清单可在结束时原子补写 trainingExitCode（0–255 整数）；0 表示训练成功，非零仅表示真实业务失败。监控缺失/verify waiting 不是非零训练结果。平台继续读取已确认清单以接收退出结果，结果一经确认不可改写。SCNet completed 只是终态，不能单独证明训练成功；在已终止且无成功证据时明确 retry 可沿用 run、新建 attempt，已知训练成功则不能因监控问题重试。禁止把 retry 改 new 绕过拒绝。
