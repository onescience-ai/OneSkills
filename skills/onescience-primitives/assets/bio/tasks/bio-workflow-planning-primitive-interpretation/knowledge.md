# workflow planning primitive的内容解读与应用方法

## 适用范围
适用于解读和应用workflow planning primitive的任务，包括从primitive的metadata推断数据来源、从workflow_nodes提取标准步骤结构、从parameters获取默认配置。用于在资源检索后增加primitive内容解析步骤，提取数据来源、步骤结构和参数配置。

## 输入
- workflow planning primitive的metadata.json和knowledge.md
- 任务需求描述

## 输出
- 数据来源信息（如source_papers）
- 标准步骤结构（如s01-s04）
- 默认参数配置
- 解读报告

## 流程节点
1. 解析primitive的metadata
   - 提取source_papers（数据来源线索）
   - 提取tags（工具和模型标识）
   - 提取tier（质量等级）
2. 解析primitive的knowledge.md
   - 提取workflow_nodes（标准步骤结构）
   - 提取parameters（默认配置）
   - 提取质量门禁和依赖关系
3. 建立从primitive到执行决策的映射规则
4. 记录解读结果

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| metadata关键字段 | source_papers, tags, tier | primitive | 用于推断数据来源和质量 |
| knowledge关键章节 | 工作流、关键参数、质量门禁 | primitive | 用于提取步骤结构和参数 |

## 边界与分流
- 如果primitive缺少关键字段，则记录缺失并跳过
- 如果primitive内容与任务需求不匹配，则选择其他primitive

## 质量检查
- 确认提取了source_papers、tags、tier
- 确认提取了workflow_nodes和parameters
- 确认解读报告完整

## 回退策略
- 如果primitive无法解读，则使用通用工作流结构

## 资源召回建议
当需要解读和应用workflow planning primitive时召回本卡片。

## 补充证据（开源文档/用户自有，可选）
[D1] OneScience官方文档（假设存在），发布机构：OneScience，版本：latest，访问日期：2026-09-21（单源参考）

## 证据来源
[1] REVOLUTIONIZING ANTIBODY DISCOVERY INDUSTRY WITH HIGHLY EFFICIENT AND ACCURATE AI-BASED EPITOPE-SPECIFIC ANTIBODY DE NOVO DESIGN WORKFLOW, Antibody Therapeutics, 2023, DOI: 10.1093/abt/tbad014.024