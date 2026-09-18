# CFD工作流预检机制：execution-manifest.json知识

## 适用范围
适用于CFD工作流预检阶段，当执行preflight validation时，需要检查execution-manifest.json文件是否存在且格式正确。该知识帮助确保工作流预检不因清单缺失而失败。

## 输入
- 工作流执行环境
- 预检脚本（如workflow_preflight.py）
- 任务启动状态信息

## 输出
- execution-manifest.json文件（记录工作流执行状态）
- 预检通过/失败状态

## execution-manifest.json标准格式

```json
{
  "task_id": "CFD_S098",
  "status": "running",
  "created_at": "2026-09-17T23:04:00Z",
  "updated_at": "2026-09-17T23:04:00Z",
  "steps": [
    {
      "step_id": "s01",
      "name": "数据接入与契约核验",
      "status": "completed",
      "input_artifacts": ["dataset_path"],
      "output_artifacts": ["dataset_manifest.json", "data_contract.json", "data_audit.md"],
      "started_at": "2026-09-17T23:04:00Z",
      "completed_at": "2026-09-17T23:05:00Z"
    },
    {
      "step_id": "s02",
      "name": "预处理与数据切分",
      "status": "pending",
      "input_artifacts": ["data_contract.json"],
      "output_artifacts": ["train_manifest.json", "validation_manifest.json", "test_manifest.json", "normalization.json"],
      "started_at": null,
      "completed_at": null
    }
  ],
  "completed_steps": ["s01"],
  "active_step": "s02",
  "error_log": []
}

## 流程节点
1. 任务启动 → 2. 生成execution-manifest.json → 3. 预检脚本检查清单存在性 → 4. 预检通过/失败

### 步骤1：任务启动
- 操作：orchestrator或预检流程启动任务
- 参数：任务ID、工作流配置
- 工具：OneScience orchestrator技能
- 质量门禁：任务启动成功

### 步骤2：生成execution-manifest.json
- 操作：在任务启动时生成execution-manifest.json文件
- 参数：任务ID、工作流步骤列表、初始状态
- 工具：orchestrator技能或预检流程
- 质量门禁：文件生成成功，格式正确

### 步骤3：预检脚本检查清单存在性
- 操作：运行预检脚本（如workflow_preflight.py），检查execution-manifest.json是否存在
- 参数：文件路径、预期格式
- 工具：预检脚本
- 质量门禁：文件存在且可解析

### 步骤4：预检通过/失败
- 操作：根据检查结果决定是否继续工作流
- 参数：预检结果
- 工具：工作流引擎
- 质量门禁：预检通过后继续执行

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 清单文件名 | execution-manifest.json | 归因报告 | 预检脚本期望的文件名 |
| 生成时机 | 任务启动时 | 归因报告 | 应在预检前生成 |
| 生成组件 | orchestrator或预检流程 | 归因报告 | 负责生成清单的组件 |

### 校准数值
以下数值来自CFD_S049任务，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 预检脚本 | workflow_preflight.py | 归因报告 | 实际使用的预检脚本 |
| 缺失后果 | 预检失败，任务被阻止 | 归因报告 | 清单缺失的后果 |

## 边界与分流
- 如果execution-manifest.json不存在，预检脚本应返回错误码（如exit code 1）
- 如果execution-manifest.json格式不正确，预检脚本应返回解析错误
- 如果预检失败，工作流应停止并报告错误，不继续执行后续步骤

## 质量检查
- 验证execution-manifest.json文件存在
- 验证文件可被JSON解析
- 验证文件包含必要的工作流状态字段

## 回退策略
- 如果无法生成execution-manifest.json，应记录错误并终止任务
- 如果预检脚本无法检查清单，应使用备用验证方法（如直接文件检查）

## 资源召回建议
- 当执行CFD工作流预检时召回本卡片
- 当预检脚本报告execution-manifest.json缺失时召回本卡片
- 配套资源：CFD工作流步骤序列知识、CFD数据接入步骤知识

## 补充证据（开源文档/用户自有，可选）
无

## 证据来源
证据有限：本卡片内容基于归因报告中的知识缺口描述，未检索到直接相关的论文证据。卡片内容为基于任务经验的推断，需进一步验证。