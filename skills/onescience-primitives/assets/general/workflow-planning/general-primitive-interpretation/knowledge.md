# Workflow Planning Primitive内容解读与应用方法

## 适用范围

**触发条件**：
- 从onescience-primitives检索到workflow planning primitive
- 需要解读primitive内容指导执行
- 需要从primitive提取数据来源和步骤结构

**适用场景**：
- 资源检索后的内容解析
- 工作流规划中的primitive应用
- 执行决策基于primitive内容

**不适用场景**：
- primitive内容的修改或更新
- 非workflow-planning类型primitive的解读
- primitive的创建或删除

## 输入

**输入数据格式**：
- primitive的metadata.json内容
- primitive的knowledge.md内容
- 任务上下文信息

**来源**：
- onescience-primitives检索结果
- 任务状态文件
- 用户任务描述

**预处理要求**：
- 解析primitive的JSON结构
- 提取关键字段内容
- 验证primitive类型

## 输出

**输出产物**：
- primitive内容解析结果
- 数据来源信息
- 步骤结构描述
- 参数配置建议

**格式**：
- JSON格式的解析结果
- 文本格式的应用建议

**验证标准**：
- 解析结果完整准确
- 数据来源可追溯
- 步骤结构清晰

## 流程节点

### Step 1：metadata.json解析
- **操作**：从primitive的metadata中提取关键信息
- **参数**：source_papers, tags, tier
- **工具**：JSON解析器, 字段提取
- **质量门禁**：字段完整, 值有效

### Step 2：knowledge.md内容分析
- **操作**：从knowledge.md中提取工作流步骤和参数
- **参数**：工作流节点, 参数配置, 依赖关系
- **工具**：文本解析, 章节提取
- **质量门禁**：步骤完整, 参数明确

### Step 3：数据来源推断
- **操作**：从source_papers推断数据文件位置
- **参数**：论文DOI, 补充材料, 数据仓库
- **工具**：DOI解析, 数据源查询
- **质量门禁**：数据源可访问, 路径有效

### Step 4：执行决策生成
- **操作**：基于primitive内容生成执行计划
- **参数**：步骤结构, 参数配置, 数据来源
- **工具**：决策引擎, 计划生成
- **质量门禁**：决策合理, 计划可行

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| source_papers | DOI列表 | [metadata] | 数据来源论文 |
| tags | 标签数组 | [metadata] | 内容分类标识 |
| workflow_nodes | 步骤列表 | [knowledge.md] | 工作流结构 |
| parameters | 参数配置 | [knowledge.md] | 默认参数值 |
| dependencies | 依赖关系 | [knowledge.md] | 步骤间依赖 |

## 边界与分流

**异常处理**：
- metadata缺失：使用默认配置
- 内容解析失败：采用通用工作流
- 数据来源不明确：执行数据发现

**降级策略**：
- primitive内容不完整时，使用部分信息
- 数据来源不可用时，执行本地搜索
- 参数配置缺失时，使用最佳实践默认值

**分支条件**：
- primitive完整：基于内容决策
- primitive部分：结合其他信息
- primitive缺失：使用通用策略

## 质量检查

**验证点**：
- 解析完整性：所有关键字段都被提取
- 内容准确性：提取信息与primitive一致
- 决策合理性：执行计划符合任务需求
- 可追溯性：决策基于具体primitive内容

**阈值**：
- 字段提取率 > 90%
- 内容匹配率 100%
- 决策合理率 > 80%
- 可追溯性 100%

**失败处理**：
- 解析失败：记录错误，使用默认值
- 内容不匹配：标记不一致，人工审核
- 决策不合理：调整参数，重新生成

## 回退策略

**替代方案**：
1. 使用通用工作流模板
2. 基于任务描述手动规划
3. 参考类似任务的历史执行
4. 提示用户提供更多指导

**失败时的处理**：
- 记录解析过程和结果
- 提供详细的primitive分析报告
- 建议可能的改进方案

## 资源召回建议

**何时应召回本卡片**：
- 资源检索后需要解读primitive内容
- 工作流规划需要基于primitive信息
- 执行决策需要primitive支持
- primitive应用出现困惑时

**配套资源**：
- onescience-primitives：原始primitive资源
- general-standard-workflow-structure：标准工作流结构
- general-data-discovery-strategy：数据发现策略

## 证据来源

[证据有限] 本卡片基于OneScience系统设计和资源管理最佳实践生成，未检索到直接相关的学术论文证据。内容为系统设计知识，非实验研究成果。