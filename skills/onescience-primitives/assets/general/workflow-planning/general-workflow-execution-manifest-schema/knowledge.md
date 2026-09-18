# 执行清单Schema：多步骤工作流的必填字段与预检门禁

## 适用范围

面向需要多步骤执行的科研工作流任务，定义执行清单（execution-manifest.json）的必填字段Schema，以确保任务通过预检门禁（preflight validation）并实现完整的执行轨迹追踪。适用于任何使用OneScience编排器（orchestrator）调度多个执行技能（executor skills）完成复杂科研任务的场景。

不适用于单步简单任务、纯查询任务或不需要预检验证的任务。

## 输入

- 任务ID（task_id）：唯一标识符
- 任务名称（task）：任务的自然语言描述
- 工作流步骤列表：从Global Plan中提取的执行步骤
- 执行技能映射：每个步骤对应的executor skill
- 输入输出契约：每个步骤的输入数据和预期输出
- 依赖关系：步骤之间的依赖顺序
- 资源绑定：每个步骤所需的资源（模型、数据、配置等）

## 输出

- execution-manifest.json文件：包含完整执行计划的JSON对象
- 通过预检验证：workflow_preflight.py返回退出码0
- 可追踪的执行轨迹：支持任务回放和审计

## 流程节点

1. **Global Plan生成** → 2. **清单提取与转换** → 3. **预检验证** → 4. **执行与更新** → 5. **最终归档**

### 步骤1：Global Plan生成
- 操作：orchestrator融合expert proposals生成global_plan
- 参数：global_plan列表，每个元素包含stage_id、goal、execution_skill、depends_on等字段
- 工具：onescience-orchestrator
- 质量门禁：executor_inventory_complete=true，所有executor已读取

### 步骤2：清单提取与转换
- 操作：从global_plan提取执行清单必填字段
- 参数：task_id、task_name、global_plan、resource_bindings
- 工具：orchestrator内联逻辑
- 质量门禁：所有必填字段完整，无空值

### 步骤3：预检验证
- 操作：workflow_preflight.py检查execution-manifest.json
- 参数：--task-id, --task, --task-artifact-dir, --output-dir, --catalog
- 工具：workflow_preflight.py
- 质量门禁：退出码=0，manifest存在且为有效JSON对象

### 步骤4：执行与更新
- 操作：执行workflow steps并更新manifest状态
- 参数：execution-manifest.json，步骤执行结果
- 工具：各executor skills
- 质量门禁：每个步骤的状态字段正确更新

### 步骤5：最终归档
- 操作：写入最终执行轨迹
- 参数：完整的execution-manifest.json
- 工具：文件系统写入
- 质量门禁：文件存在，JSON格式正确，包含所有执行记录

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| manifest格式 | JSON对象（dict） | [D1] workflow_preflight.py:107 | 必须是JSON对象，不能是数组或其他类型 |
| 预检退出码 | 0=通过，1=失败 | [D1] workflow_preflight.py:144 | manifest缺失或无效时返回1 |
| 文件位置 | task_artifact_dir/execution-manifest.json | [D1] workflow_preflight.py:98 | 必须在任务产物目录根下 |
| 必填字段完整性 | 所有字段非空 | [D3] task_execute.md:18 | 记录完整执行轨迹 |

### 校准数值（任务专属值）

以下数值来自OneScience框架内部实现，供量级校准；其他框架需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| evidence_version | "1.0" | [D1] workflow_preflight.py:113 | 预检证据版本号 |
| task_binding.catalog_exact_match | true | [D1] workflow_preflight.py:118 | 任务必须精确匹配场景目录 |
| execution_manifest.present | true | [D1] workflow_preflight.py:132 | manifest必须存在 |
| execution_manifest.valid_json | true | [D1] workflow_preflight.py:133 | manifest必须是有效JSON |

## 边界与分流

### 前提条件
1. 场景目录（catalog）存在且包含当前任务定义
2. 任务产物目录（task_artifact_dir）可写
3. workflow_preflight.py脚本可执行

### 分流条件
- **前提1不成立**（catalog缺失）：任务无法执行，返回错误"Task id/name does not exactly match the scenario catalog"
- **前提2不成立**（目录不可写）：预检失败，返回错误"Artifact directory does not exist"
- **前提3不成立**（脚本不可执行）：预检系统错误，需要修复执行环境

### 降级策略
- manifest字段不完整：记录缺失字段，标记为warning，仍可继续执行（partial状态）
- manifest格式错误：修复JSON格式后重新验证
- manifest完全缺失：创建空manifest模板，标记为需要填充

## 质量检查

### 验证点
1. **文件存在性检查**：execution-manifest.json必须存在于task_artifact_dir根目录
2. **JSON格式检查**：文件必须是有效的JSON格式
3. **对象类型检查**：JSON解析后必须是对象（dict），不能是数组或其他类型
4. **字段完整性检查**：必填字段（task_id, workflow_steps等）必须存在且非空
5. **步骤一致性检查**：workflow_steps必须与Global Plan中的步骤一致

### 阈值
- 预检通过：所有检查点通过，退出码=0
- 预检警告：部分检查点失败但不影响执行，退出码=0（partial状态）
- 预检失败：关键检查点失败，退出码=1

### 失败处理
- manifest缺失：创建空模板，标记为需要填充
- manifest格式错误：尝试修复JSON格式，失败则创建新文件
- 字段不完整：记录缺失字段，标记为warning

## 回退策略

### 策略1：空模板回退
当manifest完全缺失时，创建包含最小必填字段的空模板：
```json
{
  "task_id": "<from task binding>",
  "task": "<from task binding>",
  "workflow_steps": [],
  "status": "pending"
}
```

### 策略2：部分字段回退
当必填字段不完整时，保留已有字段，添加缺失字段的默认值：
- workflow_steps: []（空数组）
- executor_skill: null
- input_output_contract: {}
- dependencies: []
- resource_bindings: []

### 策略3：格式修复回退
当JSON格式错误时：
1. 尝试修复常见格式问题（缺少逗号、引号不匹配等）
2. 修复失败则创建备份并生成新文件
3. 记录原始错误信息到manifest的_errors字段

## 资源召回建议

### 何时应召回本卡片
- 编排器（orchestrator）生成Global Plan后需要创建执行清单
- 预检（preflight）检查发现execution-manifest.json缺失
- 需要理解execution-manifest.json的必填字段和格式要求
- 调试预检失败问题，特别是manifest相关的错误

### 配套资源
- `onescience-orchestrator`：负责生成Global Plan和提取执行清单
- `onescience-runtime`：消费执行清单进行预检验证
- `workflow_preflight.py`：执行预检验证的脚本
- `task_state_contract.md`：定义global_plan和resource_bindings的schema

## 补充证据（内部文档）

[D1] workflow_preflight.py - Preflight validation script, OneScience Framework, v1.0, local://workflow_preflight.py（accessed_at 2026-09-17，内部验证逻辑）

[D2] onescience-orchestrator SKILL.md, OneScience Framework, v1.0, local://skills/onescience-orchestrator/SKILL.md（accessed_at 2026-09-17，Global Plan生成逻辑）

[D3] task_execute.md - Task execution prompt, OneScience Framework, v1.0, local://prompts/task_execute.md（accessed_at 2026-09-17，执行清单用途说明）

[D4] task_state_contract.md - Task State schema, OneScience Framework, v1.0, local://skills/onescience-orchestrator/references/task_state_contract.md（accessed_at 2026-09-17，global_plan字段定义）

## 证据来源

本文档基于OneScience框架内部文档和代码分析，未检索到外部学术论文证据。证据来源为框架内部实现：
- [D1] workflow_preflight.py：预检验证脚本，定义了manifest的验证逻辑
- [D2] onescience-orchestrator SKILL.md：编排器技能文档，定义了Global Plan结构
- [D3] task_execute.md：任务执行提示词，定义了manifest的用途
- [D4] task_state_contract.md：任务状态契约，定义了global_plan的schema

**注意**：由于外部学术文献检索受限（OpenAlex API rate limit），本卡片内容主要基于框架内部文档。建议后续补充关于科学工作流执行规范、工作流管理系统执行清单标准等方面的外部文献证据。
