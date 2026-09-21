# JSON Schema报告交付契约

## 适用范围

**触发条件**：
- 需要通过JSON Schema校验结构化报告的完整性与格式一致性
- 需要定义报告必填字段、类型约束和嵌套对象结构
- 需要在CLI工具或API服务之间建立报告交付的验证协议

**适用场景**：
- 归因分析报告的结构化输出校验（如report.json的字段完整性检查）
- CI/CD流水线中API响应的Schema验证
- 科研数据管理中元数据报告的格式化校验
- 多系统间数据交换的契约定义与验证

**不适用场景**：
- 非JSON格式的报告（XML、YAML等需用对应Schema语言）
- 纯展示型报告（无需机器校验的文档输出）

## 输入

- JSON Schema定义文件（Draft 2019-09或更新版本）
- 待校验的JSON报告数据
- 校验选项（严格模式/宽松模式、错误收集策略）

## 输出

- 校验结果：通过（PASS）/ 未通过（FAIL）
- 校验错误详情列表：每个错误包含路径（JSON Pointer）、错误类型、预期值、实际值
- 可选：校验后的规范化报告数据

## 流程节点

### Step 1：Schema加载与解析
- **操作**：读取JSON Schema文件，解析为内部表示
- **参数**：Schema文件路径、draft版本（自动检测）
- **工具**：JSON Schema解析库（如jsonschema、ajv）
- **质量门禁**：Schema本身合法、无循环引用、draft版本已识别

### Step 2：顶层字段校验
- **操作**：检查报告是否包含所有required字段
- **参数**：required字段列表、额外字段策略（allowAdditionalProperties）
- **工具**：Schema required关键字校验
- **质量门禁**：所有必填字段存在、无缺失顶层字段

### Step 3：类型与约束校验
- **操作**：逐字段检查类型、枚举值、嵌套结构
- **参数**：字段类型映射（string/number/array/object/boolean）、enum约束、pattern约束
- **工具**：Schema type/enum/pattern/minimum/maximum关键字校验
- **质量门禁**：类型匹配、枚举值在允许范围内、数组元素类型正确

### Step 4：任务身份一致性验证
- **操作**：检查报告中的任务ID和任务名称是否与预期一致
- **参数**：预期task_id、预期task名称
- **工具**：自定义字段匹配函数
- **质量门禁**：task_id与任务索引一致、task与任务name一致

### Step 5：嵌套对象与数组深度校验
- **操作**：递归校验嵌套对象结构和数组元素
- **参数**：最大嵌套深度、数组最小/最大长度
- **工具**：Schema递归校验
- **质量门禁**：嵌套结构完整、数组元素符合items Schema

### Step 6：校验结果汇总与报告
- **操作**：收集所有校验错误，生成结构化校验报告
- **参数**：错误收集策略（fail-fast/collect-all）
- **工具**：错误聚合函数
- **质量门禁**：错误报告完整、路径定位准确

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema draft版本 | Draft 2019-09+ | [1] | 支持dynamicRef和annotation-dependent validation |
| 必填字段校验 | required关键字 | [1] | 缺失必填字段即判定FAIL |
| 类型校验 | type关键字 | [1] | 支持string/number/integer/array/object/boolean/null |
| 额外字段策略 | additionalProperties | [1] | 默认禁止额外顶层字段 |
| 嵌套深度限制 | 建议≤10层 | [2] | 防止递归校验栈溢出 |
| 校验性能目标 | <100ms/报告 | [3] | 编译型Schema可实现10x加速 |

### 校准数值（报告特定值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必填顶层字段 | task_id, task, summary, issues | [归因报告] | 以下数值来自归因分析报告体系，其他报告需以自身证据重新锚定 |
| issues类型约束 | array | [归因报告] | issues必须为数组类型 |
| summary约束 | 非空字符串 | [归因报告] | summary不能为空 |
| task_id一致性 | 与任务索引匹配 | [归因报告] | task_id字段值须与任务编号一致 |

## 边界与分流

- **Schema本身不合法**：跳过校验，输出Schema解析错误，建议修复Schema后再校验
- **报告非JSON格式**：先尝试JSON解析，失败则报格式错误，建议检查输出编码
- **严格模式vs宽松模式**：严格模式下任何校验失败即终止；宽松模式收集所有错误后统一报告
- **循环引用Schema**：检测到循环引用时设置最大递归深度限制，超限部分标记为未校验

## 质量检查

- Schema解析成功率：100%（合法Schema必须能被解析）
- 校验覆盖率：所有required字段必须被校验
- 错误路径准确性：JSON Pointer路径必须精确定位到错误字段
- 校验性能：单份报告校验时间<100ms（编译型Schema）或<1s（解释型Schema）

## 回退策略

- 若Schema解析库不可用，退化为简单的required字段检查（仅校验必填字段存在性）
- 若嵌套校验超时，跳过深层嵌套部分，标记为"部分校验"
- 若校验库版本不兼容当前Schema draft，降级到基础校验模式

## 资源召回建议

当遇到以下场景时应召回本卡片：
- 归因报告JSON校验失败（缺失字段、类型错误、字段不一致）
- 需要定义或修复CLI工具的输出Schema契约
- API响应需要Schema验证确保格式一致性
- 多系统间数据交换需要统一的Schema约束

## 证据来源

[1] "Validation of Modern JSON Schema: Formalization and Complexity", Attouche et al., Proceedings of the ACM on Programming Languages, 2024, DOI: 10.1145/3632891
[2] "Adamant: a JSON schema-based metadata editor for research data management workflows", Siffa et al., F1000Research, 2022, DOI: 10.12688/f1000research.110875.2
[3] "Blaze: Compiling JSON Schema for 10x Faster Validation", Viotti & Mior, Proceedings of the VLDB Endowment, 2025, DOI: 10.14778/3773749.3773764
[4] "Improving Api Test Accuracy through Schema Validation and Real-time Json Assertions in Jenkins Pipelines", Verma, International Journal on Science and Technology, 2025, DOI: 10.71097/ijsat.v16.i3.10656
[5] "Schema validation and evaluation framework for extracted schemas in JSON databases", Belefqih et al., Scientific Reports, 2026, DOI: 10.1038/s41598-026-45554-6
