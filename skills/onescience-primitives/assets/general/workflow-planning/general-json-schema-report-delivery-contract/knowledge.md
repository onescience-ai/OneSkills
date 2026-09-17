# JSON Schema报告交付契约通用方法

## 适用范围
面向任何需要通过JSON格式交付报告、结果或数据产品的场景，包括自动化分析流水线、API响应、配置文件、测试报告等。适用于需要确保JSON结构符合预定义Schema的验证需求。不适用于非JSON格式的数据交换。

## 输入
- JSON Schema定义文件（.json）
- 待验证的JSON报告/数据
- 任务身份信息（task_id, task名称等）
- 校验规则（必填字段、类型约束、格式要求）

## 输出
- 校验结果（通过/失败）
- 错误详情（缺失字段、类型不匹配、格式错误等）
- 修正建议
- 校验报告（可选）

## 流程节点
1. **Schema加载** → 读取并解析JSON Schema定义
2. **数据加载** → 读取待验证的JSON数据
3. **结构校验** → 验证JSON结构是否符合Schema定义
4. **字段校验** → 检查必填字段是否存在，字段类型是否正确
5. **约束校验** → 验证数组长度、字符串格式、数值范围等约束
6. **身份一致性校验** → 检查task_id、task名称等身份字段是否匹配
7. **错误收集** → 汇总所有校验错误，生成错误报告
8. **结果输出** → 输出校验结果和修正建议

每步含：操作、参数、工具、质量门禁

## 关键参数
### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| required | 字段名数组 | [D1] | Schema中定义的必填字段列表 |
| type | 字符串 | [D1] | 字段类型约束，如"string", "number", "array", "object" |
| properties | 对象 | [D1] | 定义对象字段的结构和约束 |
| items | 对象/数组 | [D1] | 定义数组元素的类型和约束 |
| minLength/maxLength | 整数 | [D1] | 字符串长度约束 |
| minimum/maximum | 数值 | [D1] | 数值范围约束 |
| pattern | 正则表达式 | [D1] | 字符串格式约束 |
| enum | 数组 | [D1] | 枚举值约束 |
| additionalProperties | 布尔/对象 | [D1] | 是否允许额外字段 |

### 校准数值
以下数值来自JSON Schema实践，供量级校准；其他系统需以自身证据重新锚定。
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 典型必填字段数 | 3-5个 | [D1] | 报告通常包含task_id, summary, issues等核心字段 |
| 数组最小长度 | 0或1 | [D1] | issues数组通常允许为空，但必须存在 |
| 字符串最小长度 | 1 | [D1] | 非空字符串字段通常要求至少1个字符 |
| 版本号格式 | 语义化版本 | [D1] | 如"1.0.0"，符合SemVer规范 |

## 边界与分流
- **Schema缺失时的降级策略**：当没有定义Schema时，应基于经验规则进行基本校验（如检查顶层字段存在性、类型检查）。
- **部分校验模式**：当严格校验失败时，可降级为警告模式，允许非关键字段缺失。
- **版本兼容性**：Schema版本升级时，需确保向后兼容，新字段应为可选。
- **性能考虑**：对于大型JSON报告，考虑流式校验或分块校验。
- **错误处理策略**：决定是立即终止校验还是收集所有错误后统一报告。

## 质量检查
- **Schema有效性**：确保Schema本身符合JSON Schema规范。
- **字段覆盖**：验证所有必要字段都已定义约束。
- **错误信息清晰**：校验错误应包含具体字段路径和错误描述。
- **可重复性**：校验过程应确定性，相同输入产生相同结果。
- **性能基准**：校验时间应在可接受范围内。

## 回退策略
- **Schema不可用**：使用基础校验规则（字段存在性、类型检查）。
- **校验工具故障**：回退到手动检查或简化校验。
- **格式不兼容**：尝试格式转换或适配器模式。
- **性能瓶颈**：优化Schema定义，减少不必要的约束检查。

## 资源召回建议
当遇到以下场景时召回本卡片：
- 需要验证自动化工具生成的JSON报告
- API响应需要符合预定义Schema
- 配置文件需要结构验证
- 测试报告需要格式标准化
- 数据交换需要确保结构一致性

## 补充证据（开源文档/用户自有，可选）
[D1] JSON Schema, JSON Schema Organization, 2026, URL: https://json-schema.org/（accessed_at 2026-09-17，权威文档）

## 证据来源
[D1] JSON Schema, JSON Schema Organization, 2026, URL: https://json-schema.org/

## 批次补充：JSON Schema验证扩展知识

### Schema组合模式

使用布尔代数关键字处理复杂报告结构 [D9]：

| 关键字 | 语义 | 说明 |
|--------|------|------|
| allOf | AND | 必须通过所有子Schema验证 |
| anyOf | OR | 必须通过至少一个子Schema验证 |
| oneOf | XOR | 必须通过恰好一个子Schema验证 |
| not | NOT | 必须不通过给定Schema验证 |

注意：避免逻辑不可能的情况（如allOf同时要求string和number类型）。

### 条件验证

用于报告中包含条件字段的场景 [D10]：

| 关键字 | 说明 |
|--------|------|
| dependentRequired | 基于其他属性存在性条件性要求属性 |
| dependentSchemas | 属性存在时条件性应用子Schema |
| if/then/else | 基于条件应用不同验证规则 |

示例：
```json
{
  "if": {"properties": {"type": {"const": "business"}}},
  "then": {"required": ["department"]},
  "else": {"required": ["home_address"]}
}
```

### 严格报告验证模式

确保JSON结构完全符合预定义Schema [D11]：

```json
{
  "type": "object",
  "properties": {
    "report_id": {"type": "string"},
    "data": {"type": "array"}
  },
  "required": ["report_id", "data"],
  "additionalProperties": false
}
```

关键区别：
- `properties` 本身不要求属性存在（需配合`required`使用）
- `additionalProperties: false` 仅识别同一Schema对象中的属性
- 使用 `unevaluatedProperties`（Draft 2019-09+）进行跨Schema属性验证

### CLI验证工具

#### ajv-cli（JavaScript/Node.js）
```bash
# 基本验证
ajv validate -s schema.json -d output.json

# 多文件验证
ajv -s schema.json -d "output/*.json"

# 错误报告格式
ajv validate -s schema.json -d output.json --errors=json
```
[D12]

#### check-jsonschema（Python/Pre-commit）
```bash
# 安装
pipx install check-jsonschema

# 基本用法
check-jsonschema --schemafile schema.json instance.json

# Pre-commit集成
- repo: https://github.com/python-jsonschema/check-jsonschema
  hooks:
    - id: check-github-workflows
```
[D13]

#### Python jsonschema库
```python
from jsonschema import validate, Draft202012Validator

# 基本验证
validate(instance=data, schema=schema)

# 收集所有错误
v = Draft202012Validator(schema)
errors = sorted(v.iter_errors(data), key=lambda e: e.path)
```
[D14]

### 常见验证失败模式与修复

| 问题 | 原因 | 修复方案 |
|------|------|----------|
| 空对象通过验证 | properties不阻止空对象 | 始终配合required使用 |
| 复合关键字中额外属性 | additionalProperties在anyOf/oneOf中失效 | 使用unevaluatedProperties: false |
| format验证未生效 | format默认仅为注释 | 显式启用格式检查 |
| 递归Schema性能问题 | 递归处理导致指数级时间 | 使用$ref限制递归深度 |
| 类型强制转换混淆 | 数字可能被强制转换为字符串 | 使用严格类型检查 |

### 错误处理模式

#### ValidationError属性
| 属性 | 说明 |
|------|------|
| message | 人类可读的错误描述 |
| validator | 失败的关键字名称（如"type", "required"） |
| path | 实例中错误发生的位置 |
| schema | 导致错误的Schema |
| context | 嵌套Schema的子错误（anyOf, oneOf） |

#### ErrorTree用于程序化错误查询
```python
from jsonschema.exceptions import ErrorTree
tree = ErrorTree(v.iter_errors(instance))
if "required" in tree.errors:
    print("Missing required field")
```

#### best_match函数
当多个验证失败时，使用best_match()找到最相关的错误：
```python
from jsonschema.exceptions import best_match
best_error = best_match(errors)
```
[D15]

### 报告交付契约推荐模式

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "report-contract-v1",
  "type": "object",
  "properties": {
    "report_type": {"enum": ["summary", "detailed", "error"]},
    "metadata": {"$ref": "#/$defs/metadata"},
    "data": {"type": "array"},
    "summary": {
      "if": {"properties": {"report_type": {"const": "summary"}}},
      "then": {"required": true}
    }
  },
  "required": ["report_type", "metadata", "data"],
  "unevaluatedProperties": false,
  "$defs": {
    "metadata": {
      "type": "object",
      "properties": {
        "generated_at": {"type": "string", "format": "date-time"},
        "version": {"type": "string"}
      },
      "required": ["generated_at", "version"]
    }
  }
}
```

验证命令：
```bash
check-jsonschema --schemafile report-schema.json report-output.json
```

## 批次补充证据
[D9] Understanding JSON Schema — Combining schemas, JSON Schema Organization, URL: https://json-schema.org/understanding-json-schema/reference/combining
[D10] Understanding JSON Schema — Conditionals, JSON Schema Organization, URL: https://json-schema.org/understanding-json-schema/reference/conditionals
[D11] Understanding JSON Schema — Object, JSON Schema Organization, URL: https://json-schema.org/understanding-json-schema/reference/object
[D12] ajv-cli — CLI validation tool, Ajv, URL: https://ajv.js.org/packages/ajv-cli.html
[D13] check-jsonschema — Python CLI tool, python-jsonschema, URL: https://github.com/python-jsonschema/check-jsonschema
[D14] jsonschema — Python library, python-jsonschema, URL: https://python-jsonschema.readthedocs.io/en/stable/
[D15] jsonschema errors — Error handling, python-jsonschema, URL: https://python-jsonschema.readthedocs.io/en/stable/errors/

## 批次补充：合并JSON Schema报告验证卡片知识（2026-09-17）

### 论文证据补充

从arXiv论文中抽取以下知识，丰富JSON Schema验证体系：

**[1] Validation of Modern JSON Schema: Formalization and Complexity (arXiv:2307.10034)**

| 概念 | 描述 | 来源 | 说明 |
|------|------|------|------|
| 形式化验证 | 将JSON Schema验证问题形式化为逻辑问题 | [1] | 提供严格的理论基础 |
| 复杂度分析 | 分析不同Schema特性的验证复杂度 | [1] | 帮助优化验证性能 |
| 验证算法 | 基于形式化的高效验证算法 | [1] | 提高验证效率 |

**[2] Blaze: Compiling JSON Schema for 10x Faster Validation (arXiv:2503.02770)**

| 概念 | 描述 | 来源 | 说明 |
|------|------|------|------|
| 编译优化 | 将JSON Schema编译为验证代码 | [2] | 显著提高验证性能 |
| 性能提升 | 验证速度提升10倍 | [2] | 适用于高性能验证场景 |
| 代码生成 | 自动生成优化的验证代码 | [2] | 减少运行时开销 |

**[3] Decision Trace Schema for Governance Evidence in Real-Time Risk Systems (arXiv:2604.09296)**

| 概念 | 描述 | 来源 | 说明 |
|------|------|------|------|
| 决策追踪Schema | 用于记录AI决策过程的Schema | [3] | 支持治理和审计需求 |
| 实时风险系统 | 在实时系统中应用Schema验证 | [3] | 确保决策过程可追溯 |
| 证据收集 | 通过Schema验证收集治理证据 | [3] | 满足合规要求 |

**[4] Validating API Design Requirements for Interoperability (S.E.O.R.A) (arXiv:2511.17836)**

| 概念 | 描述 | 来源 | 说明 |
|------|------|------|------|
| API设计验证 | 验证API设计是否符合互操作性要求 | [4] | 确保API兼容性 |
| 互操作性标准 | 定义API互操作性的标准 | [4] | 促进系统集成 |
| 需求验证 | 验证API需求是否被正确实现 | [4] | 提高API质量 |

### 补充边界与分流

- **性能优化**：对于高频验证场景，考虑使用编译优化技术（如Blaze）[2]
- **治理合规**：对于需要审计的决策系统，应实现决策追踪Schema[3]
- **API互操作性**：设计API时，应验证其符合互操作性标准[4]
- **复杂度控制**：对于复杂Schema，应分析其验证复杂度并优化[1]

### 补充质量检查

- 验证Schema的复杂度是否在可接受范围内
- 检查验证性能是否满足实时性要求
- 确保决策追踪Schema记录完整
- 验证API设计符合互操作性标准

### 补充回退策略

- **性能不足时**：使用编译优化或简化Schema
- **复杂度过高时**：分解Schema或使用分层验证
- **合规失败时**：补充缺失的治理证据
- **互操作性问题时**：调整API设计以符合标准

### 合并证据来源
[1] Validation of Modern JSON Schema: Formalization and Complexity, arXiv:2307.10034, 2023
[2] Blaze: Compiling JSON Schema for 10x Faster Validation, arXiv:2503.02770, 2025
[3] Decision Trace Schema for Governance Evidence in Real-Time Risk Systems, arXiv:2604.09296, 2026
[4] Validating API Design Requirements for Interoperability (S.E.O.R.A), arXiv:2511.17836, 2025