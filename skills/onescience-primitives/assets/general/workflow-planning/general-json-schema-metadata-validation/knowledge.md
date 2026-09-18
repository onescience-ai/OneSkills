# JSON Schema元数据验证

## 适用范围
适用于需要通过JSON Schema进行元数据验证与管理的场景，当需要创建、编辑和验证结构化元数据时，提供Schema定义、表单渲染、输入验证和API集成等方法。

## 输入
- JSON Schema定义文件
- 元数据表单数据
- 验证选项（严格/宽松模式）
- API集成配置

## 输出
- 验证结果（通过/失败）
- 错误详情（字段路径、错误类型、错误描述）
- 渲染后的表单界面
- API集成结果

## 流程节点

### 1. Schema定义与解析
定义JSON Schema的核心字段：
- **type**：字段类型（string, number, integer, boolean, array, object）
- **required**：必填字段列表
- **properties**：字段属性定义
- **additionalProperties**：是否允许额外字段

### 2. 表单渲染
将JSON Schema渲染为可编辑的表单：
- **递归渲染**：支持嵌套对象的递归渲染
- **字段类型映射**：根据type字段渲染对应的表单控件
- **注解关键字**：使用title、description等注解关键字增强表单可读性
- **文件上传**：支持base64编码的文件上传功能

### 3. 输入验证
使用Ajv库进行JSON Schema验证：
- **类型检查**：验证字段类型是否匹配
- **约束检查**：验证minLength、maxLength、pattern等约束
- **必填检查**：验证必填字段是否存在
- **错误报告**：生成详细的错误报告

### 4. API集成
通过API与外部系统集成：
- **POST方法**：发送数据到后端服务
- **GET方法**：从后端服务获取数据
- **错误处理**：处理API调用失败的情况

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| JSON Schema版本 | draft 4, draft 7, draft 2020-12 | [1] | 支持多种Schema版本 |
| 字段类型 | string, number, integer, boolean, array, object | [1] | JSON Schema支持的字段类型 |
| 验证库 | Ajv v8.8.2 | [1] | 使用Ajv进行JSON Schema验证 |
| 表单框架 | ReactJS v17.0.2 | [1] | 使用ReactJS构建表单界面 |

### 校准数值
以下数值来自Adamant工具实现，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 文件上传大小限制 | 500KB | [1] | 建议的文件上传大小限制 |
| 浏览器兼容性 | Firefox 91+, Chrome 97+ | [1] | 已测试的浏览器版本 |
| 部署要求 | 64位CPU，4核，8GB RAM | [1] | 推荐的部署配置 |

## 边界与分流
- **Schema版本不兼容**：尝试降级校验或更新Schema定义
- **文件上传失败**：检查文件大小和格式，必要时压缩文件
- **API调用失败**：检查网络连接和API配置，使用重试机制
- **表单渲染错误**：检查Schema定义是否正确，修复格式问题
- **验证规则冲突**：调整Schema定义，避免冲突的约束条件

## 质量检查
- 验证Schema定义是否符合JSON Schema规范
- 检查表单渲染是否正确显示所有字段
- 确认输入验证是否正确捕获错误
- 验证API集成是否正常工作

## 回退策略
- 使用简化Schema进行基本验证
- 手动检查关键字段
- 记录验证失败原因供后续分析
- 使用本地存储作为API调用的备选方案

## 资源召回建议
当遇到以下情况时召回本卡片：
- 需要创建JSON Schema定义文件
- 需要渲染JSON Schema为可编辑表单
- 需要验证JSON数据是否符合Schema
- 需要将元数据管理系统与外部系统集成

## 证据来源
[1] Adamant: a JSON schema-based metadata editor for research data management workflows, F1000Research, 2022, DOI: 10.12688/f1000research.110875.2