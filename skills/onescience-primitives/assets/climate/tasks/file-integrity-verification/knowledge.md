# 文件完整性校验规范

## 适用范围
适用于科研任务中需要确保交付物文件完整性和可追溯性的场景，包括SHA-256哈希计算、哈希值记录和验证。

## 输入
- 需要校验的文件列表
- 文件存储路径
- 校验要求

## 输出
- 文件完整性校验报告，包含：
  - 每个文件的SHA-256哈希值
  - 哈希值记录格式
  - 验证结果

## 流程节点
1. **文件列表获取** → 获取需要校验的文件列表
2. **哈希计算** → 使用SHA-256算法计算每个文件的哈希值
3. **哈希记录** → 将哈希值记录到元数据中
4. **验证执行** → 执行哈希验证
5. **结果报告** → 生成完整性校验报告

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 哈希算法 | SHA-256 | [1] | 安全哈希算法 |
| 哈希格式 | sha256:<hash> | [2] | 标准记录格式 |
| 文件编码 | UTF-8 | [3] | 统一编码格式 |
| 验证频率 | 每次交付前 | [4] | 确保完整性 |

## 边界与分流
- 当文件过大时，可使用分块计算哈希值
- 当文件编码不一致时，统一转换为UTF-8后计算
- 当哈希值不匹配时，记录不匹配详情并标记验证失败

## 质量检查
- 验证哈希值计算是否正确
- 检查哈希值记录格式是否正确
- 确认验证结果是否合理

## 回退策略
- 当哈希计算失败时，记录失败原因并标记相关文件为未验证
- 当验证失败时，记录失败原因并标记相关文件为不完整

## 资源召回建议
- 当任务需要确保交付物文件完整性时召回本卡片
- 配套使用气象产品质控规范卡片
- 配套使用最小干运行验证规范卡片

## 证据来源
[1] Secure Hash Standard (SHS), FIPS PUB 180-4, National Institute of Standards and Technology, 2015, URL: https://csrc.nist.gov/publications/detail/fips/180/4/final
[2] JSON Data Hashing and Verification, JSON Schema Validation, 2020, URL: https://json-schema.org/understanding-json-schema/reference/string.html#format
[3] UTF-8: A syntax for Unicode, The Unicode Standard, 2020, URL: https://unicode.org/utf8/
[4] Best practices for scientific computing, Wilson et al., PLoS Biology, 2014, DOI: 10.1371/journal.pbio.1001745