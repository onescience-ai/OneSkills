# 验收操作

1. 核对本步范围与授权，区分代码交付/采集/查看/诊断；复核真实训练入口及身份。
2. 检查目标环境原始 capabilities/check 报告；保留版本、命令、主机、解释器、退出码、warning/error。能力支持与实际采集分开。
3. 运行后或查看时对指定 attempt 执行只读 verify，记录其原始 status/checks/pending/invalid/observed_tags/limitations。启动中等待合理采样与 flush，不因 waiting 直接重跑训练。
4. 对用户要求而 verify 未覆盖的指标补充事件检查：验证点（如该任务确实有验证阶段）、学习率、吞吐或 full 诊断；逐项报告，不将所有请求指标笼统标 available。
5. 多 rank 检查所有预期 rank 源、封存/同步、聚合日志及 active 代。缺 rank 只能宣称相应局部/部分曲线，不能冒充完整全局结果。
6. 需要 base/full 切换验收时，检查配置应用记录和指定采样点新增诊断；切回 base 后停止新增，历史保留。没有请求或运行授权时不为验收主动启动/延长训练。
7. 分别回传代码、数据、作业、展示状态与证据位置。汇总进程无论训练成功失败都按运行方案收尾。

结果建议放在 execution_result.observation.monitoring，包含 operation、code_status、data_status、training_state、display_status、requested_metrics、available_metrics、missing_metrics、evidence 和 limitations。原始报告作为 artifacts 登记；不把大报告内嵌到 handoff。

## 宿主与独立知识边界

OneScience 公共 API 与接入示例通过 tools/onescience-training-monitoring 的 spec/usage 召回，无需源仓库。OneCode 项目另召回 contracts/onecode-training-monitoring，核对持久化配置、平台身份、清单、独立来源、缓存权限和分阶段诊断；不把这些平台规则当成 OneScience 公共 API。训练业务源码仍由相应 executor 按任务范围处理。
