# OneScience 训练监控公共接口

## 来源与兼容性

蒸馏核对日期：2026-11-23。OneScience 源码基线：`31065ce4838ca4848a82350fd31b792e0b113a8a`。核对文件：`src/onescience/monitoring/training/{__init__,config,monitor,capabilities,__main__,verify}.py`、`examples/monitoring/README.md`，以及 Xihe/Pangu 的 `train_adapter.py`。上述提交是基线，核对时工作区含未提交修改；精确文件 SHA-256 和验证范围见本卡 source.json。来源仅用于维护追踪，不是生成代码时必须读取的路径。

公共入口 `onescience.monitoring.training`，当前 `api_version="1"`、`contract_version="1.0"`。不要直接实例化内部 Publisher、采集器或复制汇总算法。

公共 `capabilities()` 返回与 capabilities CLI 对应的能力报告；初始化工厂核对实际 api_version、contract_version 和 tensorboard 依赖，不兼容时交统一适配层选择原生后端。能力报告不代替初始化、事件或页面证据，完整选择策略见任务卡。

## 配置和创建

- `MonitorConfig.from_file(path)` 或 `MonitorConfig.from_env()`；后者读取显式提供的 `ONESC_MONITOR_CONFIG` 配置路径，不从环境猜测数据集/工作区路径。
- `create_monitor(config, *, metrics=None, model=None, optimizer=None, device=None, process_group=None, stages=(), gradient_point=None, measurement_scope=None, rank=None, world_size=None)`；关键字沿用 TrainingMonitor 构造参数。process_group 为兼容参数，不用于新增监控通信。
- `MetricSpec(name="loss", unit="1", weight_unit="sample", phase="train", required=True, reduction="weighted_mean", scope="rank")`。phase 为 train/validation；scope 为 rank/global；至少一个训练指标 required。
- 自定义均值用 `Mean(existing_python_scalar, actual_weight)`。record 接口提交既有 Python 数值，不依赖自动 Tensor.item()。
- 每个 rank 创建一个 monitor，复用原 device/rank/world_size；全局指标与 writer_rank、train_mode/validation_mode 一致。

## 调用边界

| 时机 | 公共调用 | 约束 |
|---|---|---|
| 训练生命周期 | `with monitor:` | 保留原训练异常，不包大范围吞异常逻辑 |
| 阶段开始/结束 | `start_phase("train"或"validation", epoch=...)`、`end_phase()` | 对应真实阶段 |
| 每批计算前 | `poll_config()` | 应用后台读到的配置，不自行每批读配置文件 |
| 已有计算区间 | `with monitor.stage(name):` | 创建时声明 stages；主机墙钟时间不是 GPU kernel 时间 |
| 原 backward 后、原裁剪前 | `capture_gradients(point="after_backward_before_clip")` | 创建时 gradient_point 同名 |
| 原 AMP unscale 后、裁剪前 | `capture_gradients(point="after_unscale_before_clip")` | 复用原 unscale，不为监控新增一次；仅在真实更新边界采样 |
| 原参数更新后/微批结束 | `record_train(global_step=..., micro_step=..., loss=..., loss_weight=..., metrics=..., update_applied=..., lr_used=..., sample_count=..., elapsed_seconds=...)` | 每批调用，实际更新才增加 global_step；lr_used 是此次更新使用的学习率列表 |
| 原验证指标得到后 | `record_validation(global_step=..., validation_batch=..., loss=..., loss_weight=..., metrics=..., sample_count=..., elapsed_seconds=...)` | 不增加参数更新步数；validation_batch 每轮递增 |
| 明确恢复监控时 | `state_dict()`、`load_state_dict(state)` | 核对 run/schema/parent_attempt/step，不能把模型恢复当作监控恢复 |

## 统计与性能边界

- 本地样本均值：scope=rank，按真实 sample/token/网格等权重提交。普通 DDP 可使用 ddp_global，后台文件加权，不新增训练 all_reduce/barrier。
- 已有全局值：scope=global，通常配对应 phase 的 writer_local，复用原值，不能再次平均/加权。模型原先全局公式有何统计口径，监控不得擅改。
- 梯度累积未更新批：micro_step 递增，global_step 不变，update_applied=False，不采梯度。更新批 loss 若希望代表整窗口，复用已有正确窗口均值；接口不自动汇总所有未更新微批。
- AMP 溢出跳步依据原训练已有更新结果，不能靠 `scaler.step()` 返回值一律判断成功，也不为监控重复 step/unscale；候选梯度采样不是成功更新的证明。
- base 有队列/提交/后台写入开销；full 梯度诊断在训练进程中执行，可能增加计算与同步开销。不增加 cuda.synchronize() 来伪造精确耗时。
- 无有效配置时如何禁用监控应沿用原脚本/示例的窄配置处理，不能吞掉训练异常。严重设备故障不承诺完全隔离。

## 文件链路

首期 backend=threaded_files。单 rank 默认写 `<output_dir>/tensorboard`，不保留原始分段；多 rank 保留源分段，由一个外部 aggregate 任务增量汇总。汇总端需可见全部 rank 封存文件。OneCode 负责同步/展示，OneScience 负责加权。

多 rank 展示以 `<output_dir>/derived/active.json` 选中的当前代为准，不拼接多代。新启动用新 attempt 和空输出目录。UDP 仅在已明确选定的兼容部署中按实际契约使用，不作为首期默认路线。

## 支持能力

Loss、学习率、吞吐需要正确输入；梯度需要模型和有效 hook；阶段耗时需要声明区间；显存需要训练选择的 CUDA/ROCm 设备。主机/GPU 资源采集依赖 psutil、NVML 或 rocm-smi 等实际可用性；不能因为 GPU 字样就承诺 DCU 全部诊断可用。capabilities 是环境能力说明，不是已采集证据。

### 文件后端关闭结果

支持关闭状态的版本中，TrainingMonitor.close() 返回 closed、error、pending_records；closed=false 或 error 非空表示监控未完整收尾。shutdown_timeout_seconds 默认 30 秒，仍为可配置的有界等待。实际执行先核对目标版本接口；旧版本没有返回状态时用当前 attempt 的真实 verify 和 writer 状态取证，不能只依据训练退出码。with/finally 必须实际关闭。

## 独立使用与版本匹配

本卡为 resource_only：仅提供接口、接入知识和示例，不携带或替代 OneScience 实现。OneSkills 与 OneScience 分别安装/发布；生成代码无需可访问 OneScience 源码，运行监控仍需在真实训练环境安装兼容包。

执行前读取 capabilities 的 api_version=1、contract_version=1.0；它不包含包版本或 close 的特性清单，不能仅凭这两个字段宣称所有修订都兼容。使用目标包的公共构造参数进行配置 check；不支持 shutdown_timeout_seconds 等本次模板用到的字段时，仅报告监控版本不兼容，不猜参数或现场读实现。旧版本 close 返回空值时不能宣称已完整关闭，要保留未知状态并以当前事件和公开状态取证。安装/升级继承原授权。

### 返回值与错误

- create_monitor 配置/初始化失败可能返回禁用对象而不抛异常；先检查 config 是否存在，以及 initialization_error。监控专属 import/配置/调用用窄边界保护，不能把模型、数据或训练体放入异常吞噬范围。
- record_train/record_validation 返回 accepted；accepted=false 时保留 reason（可能是 cadence/disabled，也可能是参数错误）。accepted=true 仅表示已提交后台队列，不能证明事件已落盘。
- start_phase 成功通常返回 None；失败可返回 accepted=false。record 前必须进入对应 phase，结束后 end_phase，不能重叠。
- flush 返回 submitted，只提交状态，不是同步落盘屏障。status 返回 closed、dropped、writer_error、diagnostics 等；status.closed 表示关闭已发起，不能替代 close 返回的排空结果。
- close 返回 closed/error/pending_records（支持该特性的版本）。检查 closed=true、error 为空、pending_records=0，并核对 status.dropped/writer_error。关闭等待有界，由 shutdown_timeout_seconds 控制；超时不自动重训，不无限循环等待。
- is_enabled(component)、capture_gradients(point=...)、reenable(component)、configure(**changes)、poll_config()、state_dict()/load_state_dict(state) 是公开方法；reenable 必须是明确动作，配置切回 full 不会自动解除暂停。load_state_dict 不匹配可禁用监控，不得改变模型恢复结果。
- publish_runtime 不是 OneScience 公共方法；它属于 OneCode 接入辅助，见 contracts/onecode-training-monitoring，不能在裸 TrainingMonitor 上调用。

### 步数和验证轴

训练 global_step 从 0 开始，只在真实参数更新后加 1；micro_step 每个微批递增（首次记录通常为 1）。即使不在采样步，也逐微批调用 record_train 以维护内部计数。validation 使用当前 global_step、从 1 递增的 validation_batch；新验证轮重新计 batch。验证事件轴是连续 validation_sequence，不等同于参数更新步数。

### 公共函数

capabilities(config=None) 返回环境能力；check(config, integration=None, *, probe_write=False) 返回 status/errors/warnings/capabilities；verify(attempt_dir, *, min_points=2) 返回 status/checks/pending/invalid/observed_tags 等。capabilities/check 不证明事件已生成；probe_write 有写入副作用。

### MonitorConfig 字段清单

以下默认值来自本次蒸馏的配置快照；示例身份必须替换，不沿用到真实运行。output_dir 已是本 attempt 的独立根目录，库不会自动追加 run_id/attempt_id。普通业务配置不应固定平台每次身份。advanced UDP 字段保留接口说明，不改变默认 threaded_files 路线。

| 字段 | 类型 | 默认值 |
|---|---|---|
| `output_dir` | `str` | `必填` |
| `run_id` | `str` | `必填` |
| `attempt_id` | `str` | `必填` |
| `profile` | `str` | `'basic'` |
| `contract_version` | `str` | `'1.0'` |
| `api_version` | `str` | `'1'` |
| `record_every_updates` | `int` | `10` |
| `flush_secs` | `int` | `10` |
| `gradient_every_updates` | `int` | `100` |
| `train_mode` | `str` | `'writer_local'` |
| `validation_mode` | `str` | `'writer_local'` |
| `writer_rank` | `int` | `0` |
| `error_policy` | `str` | `'best_effort'` |
| `enabled` | `bool` | `True` |
| `jsonl` | `bool` | `False` |
| `sample_unit` | `str` | `'samples'` |
| `parent_attempt_id` | `str | None` | `None` |
| `resume_from_step` | `int | None` | `None` |
| `service_host` | `str` | `'127.0.0.1'` |
| `service_port` | `int` | `29590` |
| `service_token` | `str` | `''` |
| `buffer_limit_mb` | `int` | `16` |
| `max_packet_bytes` | `int` | `48000` |
| `consecutive_failure_threshold` | `int` | `3` |
| `gradient_enabled` | `bool` | `True` |
| `stage_timing_enabled` | `bool` | `True` |
| `memory_enabled` | `bool` | `True` |
| `backend` | `str` | `'threaded_files'` |
| `queue_max_records` | `int` | `1024` |
| `queue_max_bytes` | `int` | `8388608` |
| `max_record_bytes` | `int` | `65536` |
| `segment_max_bytes` | `int` | `262144` |
| `seal_interval_seconds` | `float` | `30.0` |
| `single_rank_source_enabled` | `bool` | `False` |
| `shutdown_timeout_seconds` | `float` | `30.0` |
| `source_max_bytes` | `int` | `1073741824` |
| `resource_enabled` | `bool` | `False` |
| `resource_interval_seconds` | `float` | `5.0` |
| `gpu_provider` | `str` | `'auto'` |
| `live_reload` | `bool` | `True` |
| `reload_interval_seconds` | `float` | `2.0` |

run_id/attempt_id 为 1–100 位字母、数字、下划线或连字符；profile=base/full，basic 为兼容别名；error_policy 仅支持 best_effort。采样间隔为正整数。恢复须同时提供 parent_attempt_id/resume_from_step，新 attempt 不同于 parent。from_dict 还接受 distributed:{train,validation,writer_rank} 与 resume:{mode,parent_attempt_id,resume_from_step}，不能与对应平铺字段重复。

## 平台边界

OneCode 用户另召回 contracts/onecode-training-monitoring，处理配置持久化、身份注入、清单和采集来源。通用接口卡不管理平台授权、数据库、租约或历史缓存。
