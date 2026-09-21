# Orchestrator专家召回异常诊断与恢复

## 适用范围
当onescience-orchestrator调用onescience-research-workflow等专家技能后，收到planner_proposals_received=0时，使用本流程诊断原因并执行恢复。适用于所有需要专家规划融合的科研任务编排场景。

## 输入
- execution-manifest.json中的expert_recall记录
- task_state.json中的当前任务状态
- intent_profile（意图识别结果）

## 输出
- 诊断报告（失败原因分类）
- 恢复动作（重试/降级为direct_step）
- 更新后的execution-manifest.json

## 流程节点

### 1. 异常检测
```
检查execution-manifest.json:
- expert_recall.planner_proposals_received == 0
- planning_mode == "direct_step"
- 是否有专家调用的输入输出记录
```

### 2. 原因诊断（按优先级排查）
| 原因 | 诊断线索 | 恢复策略 |
|------|----------|----------|
| 输入不完整 | task_state缺少必要字段 | 补全task_state后重试 |
| 领域不匹配 | intent_profile的domain不在专家覆盖范围 | 降级为direct_step |
| 资源知识不足 | available_resource_summaries为空 | 提供资源摘要后重试 |
| 专家内部异常 | 有异常日志或超时 | 重试一次，仍失败则降级 |
| 规划逻辑未触发 | intent_profile缺少aspect标识 | 补全aspect后重试 |

### 3. 重试策略
- 最多重试1次
- 重试前检查并补全输入（task_state、intent_profile、available_resource_summaries）
- 重试间隔：无等待（即时重试）

### 4. 降级条件
- 重试仍失败 → 降级为direct_step模式
- 降级时必须：
  1. 在execution-manifest.json中标注planning_mode=direct_step
  2. 记录降级原因
  3. 标注"未经专家规划验证"

### 5. 预防措施
- orchestrator在调用专家前验证输入完整性
- 专家技能应在资源知识不足时返回partial proposal而非空结果
- 增加proposal返回检查断言

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 最大重试次数 | 1 | 系统约定 | 避免无限重试 |
| 重试前检查 | 输入完整性 | 经验 | 80%的失败源于输入不完整 |
| 降级标记 | planning_mode=direct_step | 系统约定 | 必须记录 |

## 边界与分流
- 专家技能完全不可用（如依赖未安装） → 直接降级，不重试
- 任务复杂度高（多阶段、多领域交叉） → 即使降级也应在报告中标注"建议专家复核"
- 多次任务均触发降级 → 建议检查专家技能配置或资源知识完整性

## 质量检查
- execution-manifest.json中planner_proposals_received字段存在且有值
- 降级时有明确的原因记录
- 恢复后的任务执行结果与direct_mode一致

## 回退策略
- 所有恢复手段失败 → 以direct_step模式继续执行，但在最终报告中标注风险
- 建议用户后续检查专家技能配置

## 资源召回建议
- 当orchestrator的expert_recall阶段出现异常时召回本卡
- 配套资源：onescience-orchestrator（主循环逻辑）、onescience-research-workflow（专家技能）

## 证据来源
本卡知识来源于onescience系统内部经验总结，无公开论文证据。记录于任务ID 318的归因报告（execution-manifest.json: expert_recall.planner_proposals_received=0）。
