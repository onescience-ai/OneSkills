# OneScience工作流步骤输出契约

## 适用范围
面向OneScience工作流执行任务，定义各步骤的标准输出文件契约。适用于CFD工作流（如LES亚格子闭合任务），不适用于其他领域工作流。

## 输入
- 工作流步骤定义（s01、s04等）
- 场景标准配置
- 任务状态信息

## 输出
- 标准输出文件（execution-manifest.json、data_contract.json、apriori_closure/等）
- 步骤执行结果验证

## 流程节点
1. 步骤规划 → 2. 输出生成 → 3. 格式验证 → 4. 状态更新

### 步骤1：步骤规划
- 操作：确定步骤输出要求
- 参数：步骤ID、目标、依赖关系
- 工具：orchestrator规划
- 质量门禁：execution-manifest.json在Global Plan生成后创建

### 步骤2：输出生成
- 操作：生成标准输出文件
- 参数：文件格式、目录结构
- 工具：脚本生成
- 质量门禁：输出文件符合契约要求

### 步骤3：格式验证
- 操作：验证输出文件格式和内容
- 参数：文件存在性、格式正确性
- 工具：验证脚本
- 质量门禁：preflight检查通过

### 步骤4：状态更新
- 操作：更新任务状态机
- 参数：current_phase从planning到execution
- 工具：状态管理
- 质量门禁：状态正常流转

## 关键参数
### 通用判据
| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| execution-manifest.json | 必须在Global Plan生成后、步骤执行前创建 | 归因报告 | manifest_source不能是orchestrator_synthesized |
| data_contract.json | 必须包含input_fields、target_fields、units、coordinates | 归因报告 | 是下游步骤引用数据字段定义的唯一权威来源 |
| data_audit.md | 必须是Markdown格式 | 归因报告 | 不能是JSON格式 |
| s04输出目录 | 必须包含apriori_closure/、aposteriori_fields/、solver_stability.csv | 归因报告 | 后验CFD耦合需要这些产物 |

### 校准数值
以下数值来自CFD工作流任务，供量级校准；其他工作流需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| execution-manifest字段 | task_id, steps数组, dependencies, status | 归因报告 | 缺失时preflight检查失败 |
| data_contract字段 | input_fields, target_fields, units, coordinates | 归因报告 | 缺失时下游步骤字段不匹配 |
| s04输出文件 | apriori_closure/*.npy, aposteriori_fields/*.npy, solver_stability.csv | 归因报告 | 缺失时后验验证缺失 |

## 边界与分流
- **前提1：OneScience平台环境可用** → 不成立时：降级到本地执行，记录阻塞原因
- **前提2：API限流时** → 不成立时：切换到Semantic Scholar API或本地知识库
- **前提3：execution-manifest格式正确** → 不成立时：重建manifest，标注orchestrator_synthesized

## 质量检查
- 检查.onescience/execution-manifest.json存在且manifest_source不是orchestrator_synthesized
- 验证data/dns/包含dataset_manifest.json、data_contract.json、data_audit.md三个文件
- 确认outputs/s04_evaluation/包含apriori_closure/、aposteriori_fields/子目录和solver_stability.csv

## 回退策略
- 若execution-manifest缺失，由编排器重建并标注来源
- 若API限流，使用Semantic Scholar API或本地知识库

## 资源召回建议
- 执行OneScience工作流前召回本卡片
- 生成execution-manifest时召回本卡片
- 验证步骤输出时召回本卡片

## 补充证据（开源文档/用户自有，可选）
[D1] OneScience orchestrator SKILL.md，OneScience官方文档，版本未知，URL: 内部文档（accessed_at，单源参考）

## 证据来源
基于归因报告CFD_S078的优化计划推断，无公开论文证据。阻塞原因：OneScience平台内部知识，无公开权威来源。