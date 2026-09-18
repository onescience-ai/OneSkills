# Python JSON文件编码规范

## 适用范围
当需要在Python中生成包含非ASCII字符（如中文、日文、特殊符号）的JSON文件时使用本知识。适用于数据序列化、配置文件生成、数据交换等场景。不适用于二进制文件处理或非JSON格式的文本文件。

## 输入
- Python字典或列表对象，包含非ASCII字符串
- 目标文件路径
- 编码需求：UTF-8编码，非ASCII字符直接显示而非转义

## 输出
- 符合UTF-8编码的JSON文件
- 非ASCII字符（如中文）直接显示，而非Unicode转义序列
- 文件可被标准JSON解析器正确读取

## 流程节点
1. 导入json模块 → 2. 准备数据对象 → 3. 配置编码参数 → 4. 写入文件 → 5. 验证文件内容

每步含：
- **操作**：具体函数调用和参数设置
- **参数**：ensure_ascii=False, encoding='utf-8'
- **工具**：json.dump()或json.dumps()
- **质量门禁**：文件内容可正确解析，中文显示正常

## 关键参数

### 通用判据（方法层，同类体系可参考）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| ensure_ascii | False | [D1] | 禁用ASCII转义，允许非ASCII字符直接输出 |
| encoding | 'utf-8' | [D1] | 文件编码设置为UTF-8 |
| indent | None或正整数 | [D1] | 控制JSON格式化输出 |

### 校准数值（体系专属值）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认ensure_ascii | True | [D1] | Python默认设置，所有非ASCII字符被转义 |
| 推荐ensure_ascii | False | [D1] | 对于包含中文的JSON文件推荐设置 |

以下数值来自Python官方文档，供量级校准；其他体系需以自身证据重新锚定。

## 边界与分流
- **文件编码错误**：确保文件以UTF-8编码写入，避免使用系统默认编码
- **JSON解析错误**：确保数据对象可被JSON序列化（无自定义对象、无循环引用）
- **性能考虑**：大文件写入时使用流式写入，避免内存溢出
- **跨平台兼容性**：Windows/Linux/macOS均支持UTF-8编码

## 质量检查
1. 文件内容验证：使用json.load()读取文件，确认无解析错误
2. 中文显示验证：检查中文字符是否正确显示而非转义序列
3. 编码验证：使用文本编辑器打开文件，确认编码为UTF-8
4. 兼容性测试：在不同操作系统上测试文件读取

## 回退策略
- 如果ensure_ascii=False不生效，检查Python版本和json模块版本
- 如果文件编码错误，尝试使用io.TextIOWrapper明确指定编码
- 如果JSON格式错误，使用json.tool命令行工具验证

## 资源召回建议
当遇到以下情况时召回本卡片：
1. 生成的JSON文件中文显示为Unicode转义序列
2. JSON文件包含非ASCII字符但无法正确解析
3. 需要生成人类可读的JSON配置文件
4. 跨平台数据交换需要统一编码

配套资源：Python官方文档、json模块文档、编码标准RFC 7159

## 补充证据（开源文档/用户自有，可选）
[D1] json — JSON encoder and decoder, Python Software Foundation, Python 3.14.7 documentation, URL: https://docs.python.org/3/library/json.html (accessed_at: 2026-09-17T19:05:00Z, 交叉验证：官方文档)

## 证据来源
[1] json — JSON encoder and decoder, Python Software Foundation, Python 3.14.7 documentation, URL: https://docs.python.org/3/library/json.html