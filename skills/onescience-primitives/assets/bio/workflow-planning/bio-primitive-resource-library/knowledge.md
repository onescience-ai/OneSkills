# 生物信息学原语资源库构建

## 适用范围
- **触发条件**：需要构建生物信息学领域原语资源库时使用
- **适用场景**：
  - OneSkills体系的知识基础建设
  - 肽设计领域原语资源库构建
  - 生物信息学工具集成
- **不适用场景**：
  - 非生物信息学领域
  - 已有完整资源库的场景

## 输入
- **领域知识**：生物信息学相关模型、工具和工作流
- **需求规格**：资源库的结构和内容要求
- **现有资源**：已有的原语资源

## 输出
- **资源库结构**：按领域组织的目录结构
- **原语文件**：metadata.json、spec.md和使用示例
- **索引文件**：资源索引和搜索接口

## 流程节点
1. **领域分析** → 识别生物信息学领域的关键原语
2. **结构设计** → 设计资源库的目录结构
3. **原语创建** → 创建各类原语的metadata和spec
4. **索引构建** → 构建资源索引和搜索接口
5. **验证测试** → 验证资源库的完整性和可用性

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 目录结构 | skills/onescience-primitives/assets/bio/ | [1] | 按领域组织 |
| 原语类型 | workflow-planning | [1] | 工作流规划类原语 |
| 文件格式 | metadata.json + spec.md | [1] | 标准格式 |
| 命名规范 | kebab-case | [1] | 统一命名风格 |
| 版本管理 | semantic versioning | [1] | 语义化版本控制 |

## 边界与分流
- **异常处理**：
  - 当原语文件不完整时，提示补充
  - 当格式不符合规范时，自动修正
- **降级策略**：
  - 当完整原语不可用时，使用摘要版本
  - 当索引不可用时，使用文件系统搜索
- **分支条件**：
  - 根据领域选择不同的资源库路径
  - 根据原语类型选择不同的文件结构

## 质量检查
- **验证点**：
  - 原语文件完整性检查
  - 格式规范性验证
  - 索引可搜索性测试
- **阈值**：
  - 文件完整度 = 100%
  - 格式规范性 = 100%
  - 搜索成功率 > 95%
- **失败处理**：
  - 补充缺失文件
  - 修正格式错误
  - 重建索引

## 回退策略
- **失败时的替代方案**：
  - 使用简化版原语
  - 手动创建资源库
- **降级路径**：
  - 从完整原语降级到摘要版本
  - 从自动索引降级到手动搜索

## 资源召回建议
- **何时应召回本卡片**：
  - 当需要构建生物信息学领域原语资源库时
  - 当需要集成肽设计工具时
- **配套资源**：
  - 原语蒸馏工具
  - 资源库管理工具
  - 索引构建工具

## 证据来源
[1] 基于OneSkills体系原语资源库构建经验总结

## 使用示例
```python
# 生物信息学原语资源库构建示例
from bio_primitive_library import BioPrimitiveLibrary

# 初始化资源库
library = BioPrimitiveLibrary(domain="bio")

# 添加PepFlow模型原语
library.add_primitive(
    name="pepflow-model",
    type="workflow-planning",
    metadata={
        "description": "PepFlow模型原语",
        "tags": ["peptide-design", "flow-matching"]
    },
    spec="path/to/pepflow_spec.md"
)

# 添加肽设计工作流原语
library.add_primitive(
    name="peptide-design-workflow",
    type="workflow-planning",
    metadata={
        "description": "靶标特异性全原子肽类设计标准工作流",
        "tags": ["workflow", "standard", "s01-s04"]
    },
    spec="path/to/workflow_spec.md"
)

# 构建索引
library.build_index()

# 搜索原语
results = library.search("peptide design")
```