# 训练监控运行与按需诊断

仅明确或持久化要求监控时进入；普通训练不新增监控。查看已有曲线走现有只读流程，不默认安装、写配置或启动训练。

## 正常运行

通过 resource 取得 pytorch-training-monitoring-integration、onescience-training-monitoring 和 native-tensorboard-monitoring 的真实正文；OneCode 另取 onecode-training-monitoring。任务卡统一维护正常流程和后端策略，各工具卡提供接口与示例。正常生成、提交和训练不额外执行 verify，也不要求召回监控验收契约；仅用户明确要求验证或诊断时读取 training-monitoring-verification。

正常流程：生成训练代码 → 初始化时选择后端 → 训练写事件并在结束时刷新、关闭 → OneCode 按现有流程采集展示。训练结果以真实进程/调度结果为准，不增加监控验收门槛。

OneScience 监控接口兼容且初始化成功时优先使用；缺包、接口/依赖不兼容或初始化失败时使用原生 TensorBoard。两者均不可用时告警并继续已获准的训练。后端在初始化时确定，训练中不反复切换；显式关闭监控时不初始化任一后端。监控异常不改变训练退出码、不触发重训，真实训练异常正常传播。

discover 沿用 runsite，环境检查仍完整委托 installer。业务依赖、数据、设备和执行权限保留原有门禁；仅监控不可用单列告警，不降低业务 readiness。runtime 消费预检报告，不建立另一套探测或提交入口。

获准运行后沿原 Bash/SSH/SCNet 入口执行；正常训练结束时关闭监控并交回真实训练结果。OneScience 需要的多 rank 外部汇总按原工具知识安排、最终同步后结束；原生 rank 0 后端不启动该汇总。正常运行不额外提交 verify 作业，不做最小点数或页面验收。

两个后端复用现有任务身份、独立事件目录及采集交接，OneCode 继续按已绑定目录采集标准 TensorBoard 事件。不新增上报机制、任务类型或采集服务。只生成代码时不启动训练，不登记实际运行。

## 按需诊断

仅用户明确要求验证或诊断时召回 training-monitoring-verification，检查指定运行的现有日志、事件、目录绑定与采集状态。OneScience 公共 verify 或原生事件读取器都只是可选诊断手段，不是训练流程的必经阶段。

事件缺失、曲线等待或展示错误分别记录，不据此重训。源码问题返回调用方安排 coder；只读诊断不改代码、安装依赖或制造数据。
