# JSON Schema报告交付契约验证

## 适用范围
适用于所有需要以结构化JSON格式交付结果报告的场景，特别是科学计算任务、自动化测试、数据分析流水线与API响应。本卡片提供完整的JSON Schema契约验证框架，确保交付物符合预定义的格式规范、字段约束与业务规则，防止因格式错误导致的下游处理失败。

## 输入
- JSON Schema定义文件（.json/.schema.json）
- 待验证的JSON报告文件
- 业务规则约束（可选）
- 验证级别（严格/宽松）

## 输出
- 验证结果（通过/失败）
- 详细错误报告（缺失字段、类型错误、格式违规）
- 修复建议（针对每个验证失败点）

## 流程节点
1. 加载JSON Schema → 2. 解析待验证JSON → 3. 执行Schema验证 → 4. 分析错误详情 → 5. 生成修复建议

### 步骤1：加载JSON Schema
- **操作**：读取并解析JSON Schema文件
- **参数**：Schema路径、版本兼容性设置
- **工具**：JSON Schema解析器（如jsonschema库）
- **质量门禁**：确保Schema语法正确且可解析

### 步骤2：解析待验证JSON
- **操作**：读取并解析待验证的JSON文件
- **参数**：JSON路径、编码格式
- **工具**：JSON解析器
- **质量门禁**：确保JSON语法正确且可解析

### 步骤3：执行Schema验证
- **操作**：使用Schema验证JSON数据
- **参数**：验证级别、格式检查选项
- **工具**：JSON Schema验证器
- **质量门禁**：确保验证过程无异常

### 步骤4：分析错误详情
- **操作**：解析验证错误，提取错误位置和原因
- **参数**：错误格式、详细程度
- **工具**：错误分析器
- **质量门禁**：确保错误信息准确无误

### 步骤5：生成修复建议
- **操作**：根据错误类型生成具体的修复指导
- **参数**：修复模板、最佳实践
- **工具**：建议生成器
- **质量门禁**：确保建议可执行且有效

## 关键参数

### 通用判据（方法层，同类体系可参考）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| required字段 | 必填 | JSON Schema规范 | 缺失必填字段导致验证失败 |
| type约束 | 严格 | JSON Schema规范 | 数据类型必须匹配定义 |
| 数组边界 | minItems/maxItems | JSON Schema规范 | 数组长度必须在指定范围内 |
| 字符串格式 | format约束 | JSON Schema规范 | 如date-time、email、uri等 |
| 嵌套对象 | $ref引用 | JSON Schema规范 | 支持Schema复用和模块化 |
| 条件验证 | if/then/else | JSON Schema规范 | 支持条件逻辑验证 |
| 附加属性 | additionalProperties | JSON Schema规范 | 控制未知字段的处理方式 |

### 校准数值（体系专属值，供量级校准）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 最大嵌套深度 | 10层 | 通用经验 | 防止无限递归验证 |
| 最大字符串长度 | 10MB | 通用经验 | 防止内存溢出 |
| 最大数组长度 | 10000项 | 通用经验 | 性能优化阈值 |
| 验证超时 | 30秒 | 通用经验 | 防止验证过程卡死 |
| 错误消息最大数量 | 100条 | 通用经验 | 防止错误报告过大 |

## 边界与分流

### 关键前提不成立时的改道方案
1. **前提：Schema文件语法正确**
   - 不成立时 → 转向Schema修复工具（如ajv-cli）
2. **前提：JSON文件可解析**
   - 不成立时 → 转向JSON修复工具（如jq、json_repair）
3. **前提：验证器支持Schema版本**
   - 不成立时 → 转向版本转换工具（如schema-dts）
4. **前提：验证过程无性能问题**
   - 不成立时 → 转向增量验证或采样验证

### 异常处理
- **Schema语法错误**：使用Schema校验工具修复
- **JSON解析错误**：使用JSON修复工具或手动修正
- **验证超时**：简化Schema或分块验证
- **内存不足**：使用流式验证或降低验证深度

## 质量检查
1. **Schema语法**：使用JSON Schema验证器验证Schema本身
2. **JSON语法**：使用JSON解析器验证JSON格式
3. **字段完整性**：检查所有required字段是否存在
4. **类型一致性**：验证每个字段的数据类型
5. **格式合规性**：检查format约束（如日期格式）
6. **业务规则**：验证自定义业务逻辑约束
7. **性能测试**：验证大规模数据的处理能力

## 回退策略
1. **主要验证失败** → 使用简化Schema验证核心字段
2. **性能问题** → 采用采样验证或异步验证
3. **格式不兼容** → 使用格式转换器预处理数据
4. **版本冲突** → 使用多版本验证器并行验证

## 资源召回建议
**何时应召回本卡片**：
- CLI程序输出JSON格式报告
- 自动化测试结果需要结构化交付
- API响应需要符合特定Schema
- 科学计算任务生成JSON格式结果
- 数据分析流水线输出结构化数据

**配套资源**：
- `general-cli-fault-classification`：用于诊断CLI执行失败问题
- `general-data-serialization`：用于处理数据序列化格式
- `general-api-contract-testing`：用于API契约测试

## 补充证据（开源文档/用户自有，可选）
[D1] JSON Schema Specification, JSON Schema Organization, Draft 2020-12, URL: https://json-schema.org/specification（accessed_at，权威规范）
[D2] Understanding JSON Schema, JSON Schema Organization, 2024, URL: https://json-schema.org/understanding-json-schema/（accessed_at，权威文档）

## 证据来源
[1] JSON Schema Organization. JSON Schema Specification. https://json-schema.org/specification
[2] JSON Schema Organization. Understanding JSON Schema. https://json-schema.org/understanding-json-schema/