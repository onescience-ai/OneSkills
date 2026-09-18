# 工作流状态管理与编排协议

## 适用范围
面向科学工作流的状态管理与编排协议，确保任务状态实时更新和编排流程正确执行。适用于任何需要状态跟踪和步骤编排的科学计算任务。

## 输入
- 任务定义和目标
- 资源和技能列表
- 工作流配置

## 输出
- task_state.json：任务状态文件，包含 status、current_phase、completed_steps、global_plan
- execution-manifest.json：执行清单，包含 step_id、executor_skill、input/output 映射、依赖关系
- 编排日志：记录每个步骤的执行状态

## 流程节点
1. **资源召回**：调用 onescience-primitives 获取匹配资源
2. **意图识别**：分析资源和用户请求生成 intent_profile
3. **专家召回**：调用 type=expert 技能获取 proposal
4. **融合阶段**：合并 proposal 生成 global_plan
5. **执行清单生成**：生成 execution-manifest.json
6. **步骤选择**：从 global_plan 中选择 Next Step Spec
7. **状态更新**：每个步骤完成时更新 task_state.json

每步质量门禁：
- 资源召回匹配度高
- 意图识别准确
- 执行清单字段完整
- 状态更新及时

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| status 可选值 | initialization/running/completed/failed/blocked | [D1] | 任务状态 |
| current_phase | 随步骤推进更新 | [D1] | 当前执行阶段 |
| completed_steps | 已完成步骤 ID 列表 | [D1] | 记录执行进度 |
| global_plan | 融合后的步骤规划 | [D1] | 完整执行计划 |

## 边界与分流
- 如果状态更新失败：记录日志并继续执行
- 如果编排协议不完整：使用最小化执行路径
- 如果执行清单缺失：手动创建并记录缺失原因

## 质量检查
- 验证点：task_state.json 与实际执行一致
- 阈值：状态更新延迟 < 1 分钟
- 失败处理：重新同步状态文件

## 回退策略
- 如果编排协议失败：使用手动执行模式
- 如果状态文件损坏：从备份恢复或重新生成

## 资源召回建议
- 何时召回：当工作流编排状态不一致或执行清单缺失时
- 配套资源：状态管理模板、编排协议检查清单

## 补充证据（开源文档/用户自有，可选）
[D1] Apache Airflow Documentation, Apache Airflow, v2.7.0, URL: https://airflow.apache.org/docs/（accessed_at 2026-09-17，交叉验证）
[D2] Prefect Documentation, Prefect, v2.13.0, URL: https://docs.prefect.io/（accessed_at 2026-09-17，单源参考）

## 证据来源
[1] Apache Airflow Contributors. (2023). Apache Airflow Documentation. Retrieved from https://airflow.apache.org/docs/
[2] Prefect Technologies. (2023). Prefect Documentation. Retrieved from https://docs.prefect.io/