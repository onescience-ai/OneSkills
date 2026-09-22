# JSON Schema 报告交付契约验证

## 适用范围
在自动化工作流中校验 JSON 格式输出是否符合预定义的 Schema 契约。适用于科研计算中需要验证 CLI 工具输出、API 响应、结构化报告等 JSON 产物的场景，确保数据完整性、类型正确性和结构一致性。不适用于非 JSON 格式（XML、CSV）的验证。

## 输入
- 待验证的 JSON 数据（文件或字符串）
- JSON Schema 定义文件（Draft 2019-09 或更新版本）
- 验证配置（严格模式/宽松模式、自定义错误处理器）

## 输出
- 验证结果：valid（全部通过）/ invalid（存在违规）
- 错误详情：违规字段路径、错误类型、期望值与实际值
- 质量评分：各维度得分及综合 Schema Quality Score（可选）

## 流程节点
1. **Schema 加载与解析** → 读取 JSON Schema 文件，解析为内部表示
2. **JSON 数据加载** → 解析待验证的 JSON 数据
3. **基础结构校验** → 检查 JSON 顶层结构是否符合 Schema 定义
4. **必填字段检查** → 验证 required 数组中声明的所有字段是否存在
5. **数据类型验证** → 对每个字段检查其类型是否符合 type 声明
6. **嵌套结构校验** → 递归验证 objects、arrays、嵌套 schema
7. **枚举与约束检查** → 验证 enum、minimum、maximum、pattern 等约束
8. **错误聚合与报告** → 收集所有违规项，生成结构化错误报告

## 关键参数

### 通用判据
| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| Schema 版本 | Draft 2019-09+ | [2] | 支持 dynamicRef 和 annotation-dependent 验证 |
| 必填字段检查 | 严格模式必须全部存在 | [1] | 缺失必填字段应返回 invalid |
| 类型验证 | 支持 string/number/boolean/array/object/null | [1] | 多类型字段使用 anyOf/oneOf |
| 嵌套深度限制 | ≤10 层 | [1] | 防止递归验证栈溢出 |
| 错误信息格式 | JSON Path + 错误类型 + 期望值 | [1] | 便于定位问题字段 |

### 校准数值（SVEF 框架六维度）
以下数值来自 JSON Schema 验证框架研究，供量级校准；其他体系需以自身证据重新锚定：
| 维度 | 指标 | 来源 | 说明 |
|------|------|------|------|
| Data Type Accuracy (DTA) | Type Conformance(p) = \|PT_obs ∩ PT_inf\| / \|PT_obs ∪ PT_inf\| | [1] | 原始类型一致性，得分 0-1 |
| Required/Optional Fields | Presence Accuracy = (1/\|P\|) Σ 1[R_inf = R_ref] | [1] | 必填字段识别准确率 |
| Multiple Type Support (MTS) | MTS(p) = \|T_obs ∩ T_inf\| / \|T_obs\| - λ·max(0, \|T_inf\|-\|T_obs\|)/\|T_inf\| | [1] | 多类型支持，惩罚过度泛化 |
| Collection Structure Consistency (CSC) | CSC = α·Homogeneity(a) + (1-α)·DepthConformance(a) | [1] | 数组结构一致性 |
| Entity Relationships Recovery (ERR) | ERR = β·F1 + (1-β)·GED_norm | [1] | 实体关系恢复，β=0.7 |
| Temporal Evolution Detection | 版本差异检测 | [1] | Schema 演化追踪 |

## 边界与分流
- **Schema 文件不存在**：不可恢复，应检查配置路径
- **JSON 解析失败**：不可恢复，应检查输出格式是否为合法 JSON
- **Schema 版本不兼容**：可尝试降级验证或更新 Schema 定义
- **嵌套深度超限**：可增加深度限制或简化数据结构
- **自定义关键字不支持**：可尝试忽略或降级到基础验证

## 质量检查
- 所有必填字段（required 数组）必须在 JSON 中存在
- 每个字段的类型必须符合 type 声明（或 anyOf/oneOf 组合）
- 数组字段的 items 类型必须一致
- 嵌套 object 必须递归验证其内部字段
- 错误报告必须包含完整的 JSON Path 定位

## 回退策略
- Schema 验证失败时：尝试宽松模式验证（忽略额外字段）
- Schema 版本不兼容时：使用基础 JSON 解析库做简单结构检查
- 自定义关键字不支持时：降级到标准关键字子集验证

## 资源召回建议
当任务涉及以下场景时应召回本卡片：
- 验证 CLI 工具的 JSON 输出是否符合契约
- 检查 API 响应的数据结构完整性
- 自动化测试中的输出格式校验
- 科研工作流中的结构化报告验证

## 证据来源
[1] Schema validation and evaluation framework for extracted schemas in JSON databases, Belefqih et al., Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6
[2] Validation of Modern JSON Schema: Formalization and Complexity, Attouche et al., Proc. ACM Programming Languages, 2024, DOI: 10.1145/3632891
[3] Adamant: a JSON schema-based metadata editor for research data management workflows, Siffa et al., F1000Research, 2022, DOI: 10.12688/f1000research.110875.2
