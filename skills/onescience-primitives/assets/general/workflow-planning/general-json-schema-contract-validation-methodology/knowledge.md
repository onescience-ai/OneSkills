# JSON Schema 数据契约验证方法论

## 适用范围
面向结构化JSON输出验证场景，提供基于JSON Schema的数据契约定义、验证执行与质量保证的方法论框架。适用于API测试、数据集成、元数据管理、研究数据管理（RDM）等需要确保数据格式一致性和质量保证的场景，不涉及特定科学领域的数据模型。

## 输入
- **JSON Schema定义**：数据结构规范、字段类型、必填/可选约束、格式规则
- **JSON数据实例**：待验证的JSON文档或数据流
- **验证配置**：验证严格度、错误处理策略、性能要求

## 输出
- **验证结果**：通过/失败状态、详细错误信息、警告信息
- **质量报告**：数据类型准确性、字段完整性、结构一致性评估
- **修复建议**：不符合Schema的数据修正方案

## 流程节点
1. **Schema解析** → 解析JSON Schema定义，提取验证规则
2. **数据预处理** → 清洗和标准化待验证数据
3. **验证执行** → 应用Schema规则进行逐字段验证
4. **结果分析** → 分析验证错误，识别问题模式
5. **质量评估** → 计算数据质量指标，生成质量报告

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 验证维度 | 数据类型准确性、必填字段、多类型支持、集合结构、实体关系、时间演化 | [论文1] | 六维度Schema质量评估框架 |
| 验证阈值 | 置信度≥0.8，提升度≥1.2 | [论文1] | 依赖关系验证的经验阈值 |
| 性能指标 | 验证时间≤100ms/文档 | [论文2] | 实时验证的性能要求 |

### 校准数值
以下数值来自JSON Schema验证实践，供量级校准；其他体系需以自身证据重新锚定：
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema版本 | Draft 4/7/2020-12 | [论文3] | JSON Schema规范版本 |
| 错误信息粒度 | 字段级错误定位 | [论文3] | 便于问题定位和修复 |
| 支持的类型 | string, number, integer, boolean, array, object, null | [论文3] | JSON Schema基本类型 |

## 边界与分流
- **语法错误**：JSON格式错误、Schema定义无效 → 检查JSON语法和Schema规范
- **类型错误**：字段类型不匹配 → 调整数据类型或修改Schema定义
- **约束错误**：必填字段缺失、格式不符合 → 补充数据或调整约束条件
- **结构错误**：嵌套结构不正确、数组格式错误 → 修正数据结构
- **性能问题**：验证超时、内存不足 → 优化Schema复杂度或分批验证

## 质量检查
- JSON Schema是否符合规范版本
- 验证规则是否覆盖所有业务需求
- 错误信息是否清晰可操作
- 性能是否满足实时性要求

## 回退策略
- 使用宽松验证模式，只检查关键字段
- 分阶段验证，先验证核心结构再验证细节
- 创建简化版Schema进行快速验证
- 参考官方JSON Schema文档或社区最佳实践

## 资源召回建议
- 当需要验证JSON数据格式一致性时召回本卡
- 配套资源：`general-cli-fault-classification-methodology`（用于CLI执行故障处理）
- 适用于API测试、数据集成、元数据管理、研究数据管理等场景

## 证据来源
[1] Schema validation and evaluation framework for extracted schemas in JSON databases, Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6
[2] Improving Api Test Accuracy through Schema Validation and Real-time Json Assertions in Jenkins Pipelines, International Journal on Science and Technology, 2025, DOI: 10.71097/ijsat.v16.i3.10656
[3] Adamant: a JSON schema-based metadata editor for research data management workflows, F1000Research, 2022, DOI: 10.12688/f1000research.110875.2