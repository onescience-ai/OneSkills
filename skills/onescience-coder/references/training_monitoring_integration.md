# 训练监控代码接入

仅明确或持久化要求监控时使用。普通训练保留现有行为，已有接入满足需求时复用。查看曲线不属于编码步骤，继承“暂不运行”等约束。

## 接入依据

通过 resource 取得 pytorch-training-monitoring-integration、onescience-training-monitoring 和 native-tensorboard-monitoring 的真实正文；OneCode 另取 onecode-training-monitoring。任务卡统一维护正常流程和后端策略，各工具卡提供接口与示例。正常生成、提交和训练不额外执行 verify，也不要求召回监控验收契约；仅用户明确要求验证或诊断时读取 training-monitoring-verification。

## 编码职责

1. 确定真实训练入口、已有 writer、输出目录、rank、AMP/累积及指标口径。
2. 按任务卡的后端策略适配 OptionalTrainingMonitor。OneScience-only import/类型/配置留在 factory；两个后端共用的身份、目录和业务数值在外部准备。
3. 保留训练计算、通信、参数更新、checkpoint 和早停语义。监控失败仅告警，不能吞掉训练异常；结束时沿现有生命周期关闭监控。
4. 交付代码、配置与使用说明。核对调用位置、导入边界和异常传播即可；不附加测试脚本、verify 命令或默认验收阶段。仅代码任务不启动训练。

## 交接

两个后端复用现有任务身份、独立事件目录及采集交接，OneCode 继续按已绑定目录采集标准 TensorBoard 事件。不新增上报机制、任务类型或采集服务。只生成代码时不启动训练，不登记实际运行。

按原 execution_result 记录实际入口、后端策略和限制。需要实际执行或环境修复时回调用方，沿既有授权选择 owner；coder 不自行启动训练或安装依赖。
