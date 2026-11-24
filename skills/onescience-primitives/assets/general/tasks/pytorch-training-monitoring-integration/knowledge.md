# PyTorch 训练监控接入 (pytorch-training-monitoring-integration)

## 任务目标

在现有科研任务流程内按需接入、查看或诊断 OneScience 训练监控。不新增监控 expert，不建立平行训练入口；编码、环境就绪与运行继续交给各自的现有 executor。

## 适用范围 / 不适用场景

- 用户明确提出训练指标采集、训练监控、接入监控、查看曲线或诊断监控时使用。中文、英文及上下文明确的“监控 Loss”等同义表达均可，不依赖单个关键词。
- “训练 Xihe”“运行训练脚本”本身不构成新增监控需求；模型卡、资源推荐或模板中出现监控也不构成用户授权。未要求监控时保留脚本既有逻辑，不主动接入、删除或切换。
- 首期接入支持可修改的原生 PyTorch 单卡、普通 DDP。AMP/梯度累积先核对原更新语义。JAX、FSDP、TP、PP 不直接套用普通 DDP 规则；仅对实际支持的部分交付。
- 服务监控、文件变化监控、普通日志进度查询不是训练监控代码接入。
- 查看已有曲线仅做只读查看。排查无数据先取证；修复代码需要进入独立编码步骤。只要求接入且禁止运行时不启动训练，包括 smoke/dry-run。

## 实体槽（Entity Slots）

从用户请求和既有任务上下文提取：操作（接入/查看/诊断）、真实训练入口、目标工作区/环境、框架/并行模式、AMP/累积规则、所需指标及统计口径、已有配置/事件、运行授权和恢复需求。run_id、attempt_id、output_dir 必须对应本次实际运行，不从示例照抄。

## 输入输出契约

沿用 step_handoff：task_context.user_goal/constraints 保留原始监控需求和运行限制；inputs 携带入口、配置与环境；required_outputs/completion_criteria 明确本步交付范围。资源内容只通过 resource_retrieval_result.matched_resources[*].content 传递，path 仅追踪。

编码产出适配代码、配置和接入说明（指标范围、权重、步数、hook 与恢复方式）。运行产出目标环境预检、真实事件 verify 回执和事件目录；展示状态另列。所有结果沿用 execution_result.artifacts/observation，不把代码交付当作运行或科研结论。

## 方法路线（可替换）

以 tools/onescience-training-monitoring 的公共 API 为准，默认 threaded_files。复用已有完整接入；缺失时只在实际循环/Callback 中补齐。通用示例仅说明插入位置，不替代训练代码。

## 操作序列（Operations）

1. 区分接入、查看、诊断。查看定位指定 run/attempt 的真实数据；诊断检查原配置、调用、事件和同步证据，不默认重新接入或重跑。
2. 接入时识别实际训练入口与已有采集。复用脚本优先在任务工作区制作适配版本；修改脚本最小插入；新代码按公共接口生成。避免修改未执行的样例或重复 SummaryWriter。
3. 编码 executor 获取规格/使用知识，核对单卡/DDP、全局/本地指标、AMP/累积和恢复语义，交付代码、配置与静态检查。
4. 仅在获准运行时交给运行 executor。环境检查仍由 installer 承接；运行 executor 消费 readiness，调用配置检查、安排单个外部汇总任务、同步和验证。
5. 结果回到 orchestrator。必需事件未验证则不把整项监控标完成；仅代码交付任务可以完成，但采集/展示状态保持 not_run。

## 验证契约（Validations）

消费 contracts/training-monitoring-verification：真实训练点、验证点（如适用）、统计口径、多卡完整性和当前 attempt 关联分别核验。没有事件不能推断训练失败；仅能力查询或 association 更新不能证明接入成功。

## 资源引用（Resources）

- tools/onescience-training-monitoring：接口、配置、CLI、示例差异与能力边界。
- contracts/training-monitoring-verification：阶段结果、事件证据与异常判定。

## 前后置任务（Task Graph）

本任务是既有训练/代码任务的可选组成部分，由明确需求触发。编码、运行、环境修复各自产出正式回执，再由 orchestrator 决定下一步；不由 executor 私自串行选择业务 executor。不要求新建 scenario/workflow 或监控 expert。

## 缺口与降级（Fallback / Gap）

目标环境缺公共 API 或依赖时报告版本/依赖证据并按现有环境流程处理，不猜测接口。缺共享目录/同步时不能宣称 DDP 全局指标完整。未实现的 OneCode 展示报告未验证；不新增数据库、展示系统或在 OneCode 重写加权。无法运行时可交付代码与静态证据，明确 not_run 原因。

## 宿主与独立知识边界

OneScience 公共 API 与接入示例通过 tools/onescience-training-monitoring 的 spec/usage 召回，无需源仓库。OneCode 项目另召回 contracts/onecode-training-monitoring，核对持久化配置、平台身份、清单、独立来源、缓存权限和分阶段诊断；不把这些平台规则当成 OneScience 公共 API。训练业务源码仍由相应 executor 按任务范围处理。

## 蒸馏来源

2026-11-23 按 primitive-distiller 的 resource_only 流程从 OneScience monitoring.training 公共接口、测试判据及 Xihe/Pangu 使用经验提炼。适用 api=1、contract=1.0；精确来源指纹随工具卡 source.json 维护。Task metadata 保持九字段，关系继续使用原有 tags，不在任务卡增加 provider/source 新字段。普通生成不访问来源路径；缺兼容知识返回缺口，不猜 API。
