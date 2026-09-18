# JSON Schema报告交付契约

## 适用范围
面向JSON数据结构的验证与契约定义，使用JSON Schema确保数据在系统间传输时的正确性、完整性和安全性。适用于API请求/响应验证、配置文件校验、数据交换格式验证、报告交付契约等场景。不适用于二进制数据格式或非结构化数据验证。

## 输入
- JSON Schema定义文件（Draft 2019-09或更新版本）
- 待验证的JSON数据
- 验证选项（如严格模式、附加错误信息）

## 输出
- 验证结果（通过/失败）
- 详细错误信息（路径、消息、预期类型）
- 验证性能指标（时间、内存使用）

## 流程节点
1. **Schema解析** → 加载并解析JSON Schema定义
2. **数据准备** → 预处理待验证JSON数据
3. **验证执行** → 应用Schema规则进行验证
4. **错误收集** → 收集并格式化验证错误
5. **结果输出** → 返回验证结果和详细信息

每步含：操作、参数、工具、质量门禁

## 关键参数
### 通用判据（方法层，同类体系可参考）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填字段验证 | required数组 | [D1] | 确保指定字段存在 |
| 类型验证 | type关键字 | [D1] | 验证字段数据类型 |
| 数组约束 | items/minItems/maxItems | [D1] | 验证数组结构和长度 |
| 字符串模式 | pattern关键字 | [D1] | 使用正则表达式验证字符串格式 |
| 数值范围 | minimum/maximum | [D1] | 验证数值在指定范围内 |
| 嵌套验证 | properties/$ref | [D1] | 验证嵌套对象结构 |

### 校准数值（体系专属值）
以下数值来自JSON Schema验证研究，供量级校准；其他体系需以自身证据重新锚定。
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 经典JSON Schema验证复杂度 | PTIME | [1] | Draft-07及之前版本的验证复杂度 |
| 现代JSON Schema验证复杂度 | PSPACE-complete | [1] | Draft 2019-09及之后版本的验证复杂度 |
| Blaze编译器加速比 | 10x | [3] | 相比现有验证器的平均加速比 |
| 动态引用复杂度影响 | 指数级 | [2] | 消除注释依赖可能导致模式大小指数增长 |

## 边界与分流
- **Schema版本不兼容**：检查Draft版本，必要时转换Schema
- **验证性能瓶颈**：考虑使用编译器优化（如Blaze）或简化Schema
- **动态引用导致复杂度爆炸**：避免过度使用动态引用，考虑静态替代方案
- **自定义关键字不支持**：扩展验证器或使用预处理转换

## 质量检查
- 验证Schema本身是否有效（meta-schema验证）
- 确认所有必填字段都被检查
- 检查错误信息是否清晰可定位
- 验证性能是否满足实时性要求

## 回退策略
- Schema验证失败时提供详细错误定位
- 性能不足时降级到简化验证或异步验证
- 版本不兼容时提供迁移指南

## 资源召回建议
当遇到以下情况时召回本卡片：
- 设计API数据契约
- 验证配置文件格式
- 实现数据导入/导出验证
- 优化JSON Schema验证性能
- 解决JSON Schema版本兼容性问题

## 补充证据（开源文档/用户自有）
[D1] JSON Schema reference, JSON Schema, 2020-12, URL: https://json-schema.org/understanding-json-schema/ (accessed_at: 2026-09-17, 交叉验证)

## 证据来源
[1] Validation of Modern JSON Schema: Formalization and Complexity, Lyes Attouche et al., arXiv, 2024, DOI: 10.48550/arXiv.2307.10034
[2] Elimination of annotation dependencies in validation for Modern JSON Schema, Lyes Attouche et al., arXiv, 2025, DOI: 10.48550/arXiv.2503.11288
[3] Blaze: Compiling JSON Schema for 10x Faster Validation, Juan Cruz Viotti et al., arXiv, 2025, DOI: 10.48550/arXiv.2503.02770