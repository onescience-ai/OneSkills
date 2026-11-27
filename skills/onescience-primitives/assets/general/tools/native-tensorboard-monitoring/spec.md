# 原生 TensorBoard 监控后端

本资源定义 OneScience 监控不可用时的 PyTorch 原生后端，不属于 OneScience 公共 API。后端选择与执行边界以 tasks/pytorch-training-monitoring-integration 为准；本卡提供接口知识，不携带独立执行器。

## 依赖与目录

在实际训练解释器中检查 `from torch.utils.tensorboard import SummaryWriter`；安装了 tensorboard 或 torch 中的一个不代表 writer 可用。OneScience 缺包、版本不兼容、公共接口不可用或初始化失败时，在初始化阶段选择该后端。选择完成后不启动第二个 writer，不在写指标失败后切换后端。

输入为既有的绝对 attempt 根目录、run_id、attempt_id、全局 rank/world_size、采样间隔和 flush 间隔。原生事件写到 `<output_dir>/tensorboard`，保持既有采集根目录和任务身份。没有目标环境证据时，生成自适应代码并将运行状态标 not_run，不以生成环境的依赖情况固定目标后端。

## 接入接口

技能辅助 `OptionalTrainingMonitor(factory, *, output_dir, run_id, attempt_id, rank=0, world_size=1, record_every_updates=10, flush_secs=10)` 统一选择和异常边界。factory 只负责 OneScience 初始化，所有 OneScience-only import、配置和 MetricSpec 声明都留在 factory 内；模型、优化器和训练数据在外部创建。可随生成脚本适配该辅助，它不是 OneScience 公共类。

- `backend` 为 onescience / tensorboard / disabled，`status()` 分别报告选择结果、原因和组件能力。
- `record_train(global_step=..., loss=..., update_applied=True, lr_used=(), sample_count=None, elapsed_seconds=None)` 记录已有 Python scalar。只在实际参数更新后记录；采样按更新步数，重复/回退 step 拒绝写入。不为监控调用 Tensor.item、增加归约或改变优化器行为。
- `start_phase('validation')`、`record_validation(global_step=..., loss=..., loss_weight=...)`、`end_phase()` 在一个 checkpoint 下按真实 weight 汇总一个验证点，不将多个 batch 写成同 step 重复点。
- `flush()` / `close()` 保证可选监控生命周期；close 结果不是事件或页面验收证据。
- `is_enabled('gradient')` 为 false；stage 是不改变训练体的空测时上下文。梯度、显存、阶段耗时、全局聚合、live reload 和监控状态恢复未在原生基础实现中提供；需要这些能力时单独报告 partial/unsupported。

## 指标和多卡口径

单 rank 的基本 tags：`loss/train/step/loss`、`loss/validation/step/loss`、`lr/train/group_N`；提供真实 sample_count/elapsed_seconds 时另记 `throughput/train/step/throughput`。训练 loss 是调用方传入的真实更新点值，不声称自动形成跨微批窗口均值。

普通 DDP 原生基础后端仅全局 rank 0 写事件；loss/throughput tag 将 step 改为 rank_0。它表示 rank 0 实际输入，不能冒称全局。其余 rank 不建 writer，不启动 OneScience aggregate，不新增 all_reduce/barrier。若已有全局统计，可在任务工作区适配并显式标注真实口径；不把共享示例升级为隐含全局实现。每次 attempt 使用独立目录，旧事件和旧后端状态不自动恢复。

## 失败与关闭

`ONECODE_MONITORING_DISABLED=1` 时两个后端均不初始化。OneScience 不可用会记录回退原因；原生依赖或初始化也失败时监控 disabled/unavailable，保留训练执行。仅监控失败不改变训练退出码、不自动安装、不重训。真实训练异常正常传播。没有平台身份或采集连接不能通过换 writer 修复，沿既有采集流程报告相关缺口。
