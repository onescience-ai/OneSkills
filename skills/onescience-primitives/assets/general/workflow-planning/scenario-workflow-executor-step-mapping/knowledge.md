# OneScience场景workflow步骤与executor步骤的映射规则

## 适用范围
适用于OneScience工作流编排中场景步骤到executor步骤的映射。当orchestrator需要将领域工作流步骤（s01-s04）转换为可执行的executor步骤时，必须遵循本映射规则，确保输入输出契约一致。

## 输入
- 场景workflow定义（包含s01-s04步骤）
- executor能力列表（包含各executor的输入输出契约）
- 任务上下文（包含用户需求和约束条件）
- 映射规则（本卡片提供的映射原则）

## 输出
- 映射关系表（记录每个executor步骤对应的场景步骤）
- execution-manifest.json（包含step_mapping字段）
- 执行计划（包含步骤依赖关系和执行顺序）

## 流程节点
1. 分析场景workflow的s01-s04步骤定义
2. 识别每个场景步骤的输入输出契约
3. 匹配executor能力与场景步骤需求
4. 建立场景步骤到executor步骤的映射关系
5. 验证输入输出契约的一致性
6. 生成execution-manifest.json

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 场景步骤编号 | s01, s02, s03, s04 | 场景定义 | 领域工作流步骤 |
| executor步骤编号 | step-1, step-2, ... | execution计划 | 可执行步骤 |
| 映射关系字段 | step_mapping | execution-manifest.json | 记录步骤映射 |
| 输入输出契约一致性 | 必须保持 | 映射规则 | 场景步骤的输入输出必须传递到对应executor步骤 |
| 映射粒度 | 1:N（一个场景步骤可映射到多个executor步骤） | 映射规则 | 根据executor能力灵活映射 |

## 边界与分流
- 当场景步骤与executor能力不匹配时，需寻找替代executor或调整步骤定义
- 当多个场景步骤需要相同executor时，可合并为单个executor步骤
- 当单个场景步骤需要多个executor时，需拆分为多个executor步骤
- 映射关系必须记录在execution-manifest.json的step_mapping字段中
- 映射完成后需验证步骤依赖关系和执行顺序

## 质量检查
- 验证每个场景步骤都有对应的executor步骤
- 检查输入输出契约是否一致
- 确认步骤依赖关系正确
- 验证execution-manifest.json格式正确

## 回退策略
- 如果映射关系不完整，需补充缺失的映射
- 如果输入输出契约不一致，需调整步骤定义或executor配置
- 如果执行顺序错误，需重新规划步骤依赖关系
- 如果executor能力不足，需寻找替代方案或调整任务目标

## 资源召回建议
- 当需要定义场景workflow时，召回场景工作流定义相关知识
- 当需要配置executor时，召回executor配置相关知识
- 当需要验证输入输出契约时，召回数据契约相关知识
- 当需要规划执行顺序时，召回任务调度相关知识

## 证据来源
[1] 归因报告issue-5：场景s01-s04与execution-manifest中step-1到step-6无明确映射关系
[2] 归因报告issue-5：orchestrator在global_plan生成时未将场景workflow的s01-s04步骤与executor能力进行精确映射