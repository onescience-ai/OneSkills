# JSON Schema验证工作流

## 适用范围
面向JSON数据结构的验证需求，提供基于JSON Schema的验证工作流。适用于API输入输出校验、数据质量管控、配置文件合规性检查、自动化测试流水线中的结构化数据验证。不适用于语义验证或业务逻辑校验。

## 输入
- JSON Schema定义文件（Draft 2020-12或兼容版本）
- 待验证的JSON实例数据
- 验证选项（严格模式、格式检查、注解收集）

## 输出
- 验证结果（通过/失败）
- 结构化错误报告（包含错误路径、错误类型、错误消息）
- 注解信息（如默认值、枚举匹配）

## 流程节点
1. **Schema加载与编译** → 解析JSON Schema，构建验证树，处理$ref引用和递归结构。
2. **实例验证** → 根据Schema关键字（type, required, properties, items等）逐项验证JSON实例。
3. **格式验证** → 对format关键字（date-time, email, uri等）进行语义验证（可选）。
4. **错误收集** → 收集所有验证错误，生成结构化错误报告（遵循标准输出格式）。
5. **注解提取** → 提取annotation关键字（如默认值、示例）供下游使用。
6. **报告生成** → 将验证结果序列化为JSON格式，包含元数据（Schema版本、验证时间戳）。

## 关键参数
### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema版本 | Draft 2020-12 | [D1] | 当前推荐版本，支持动态引用和注解依赖验证 |
| 验证复杂度 | PTIME（经典）/ PSPACE（现代） | [1] | 现代Schema功能可能显著增加验证复杂度 |
| 错误报告格式 | 标准化JSON结构 | [D2] | 包含error、path、message、schemaPath等字段 |
| 性能优化 | 编译时预处理 | [2] | 可将验证速度提升10倍 |

### 校准数值
以下数值来自JSON Schema研究，供量级校准；其他体系需以自身证据重新锚定。
- 经典Schema验证复杂度：PTIME [1]
- 现代Schema（动态引用）验证复杂度：PSPACE [1]
- Blaze编译优化加速比：10x [2]
- 格式验证覆盖率：约30%常用格式 [D2]

## 边界与分流
- **前提1：Schema符合规范** → 若Schema语法错误，转向"Schema调试"分支。
- **前提2：JSON实例可解析** → 若JSON格式错误（如缺少引号），转向"语法修复"分支。
- **前提3：验证器支持目标Schema版本** → 若使用旧版验证器处理现代Schema，转向"降级验证"分支（可能丢失新功能）。

## 质量检查
- Schema覆盖率：验证器应支持目标Schema版本的所有关键字
- 错误报告完整性：每个错误包含路径、类型、消息
- 性能基准：验证时间应在可接受范围内（如<100ms/实例）

## 回退策略
- Schema验证失败时，提供宽松模式（仅检查必需字段）
- 格式验证不支持时，跳过format关键字验证
- 性能瓶颈时，采用编译缓存或批处理优化

## 资源召回建议
- 当需要验证JSON数据结构时召回本卡片
- 配套资源：CLI故障分类诊断卡片（用于验证工具执行错误处理）
- 扩展场景：多Schema组合验证、Schema演化兼容性检查

## 补充证据（开源文档）
[D1] JSON Schema Specification (2020-12), JSON Schema Organization, URL: https://json-schema.org/specification (accessed_at 2026-09-16)
[D2] JSON Schema Validation: A Vocabulary for Structural Validation of JSON, IETF, draft-bhutton-json-schema-validation-01, URL: https://datatracker.ietf.org/doc/draft-bhutton-json-schema-validation/ (accessed_at 2026-09-16)

## 证据来源
[1] Validation of Modern JSON Schema: Formalization and Complexity, Attouche et al., arXiv 2023, DOI: 10.48550/arXiv.2307.10034
[2] Blaze: Compiling JSON Schema for 10x Faster Validation, Viotti & Mior, arXiv 2025, DOI: 10.48550/arXiv.2503.02770