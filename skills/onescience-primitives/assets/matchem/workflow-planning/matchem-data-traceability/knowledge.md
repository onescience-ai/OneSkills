# 材料科学任务数据可追溯性要求

## 适用范围

**触发条件**：
- 需要获取材料结构数据用于计算或分析
- 需要使用性能数据作为参考或验证
- 需要确保数据来源的可追溯性

**适用场景**：
- 所有OneScience材料科学任务的数据获取
- 材料结构数据的权威来源验证
- 性能数据的文献来源标注

**不适用场景**：
- 方法验证阶段可使用假设数据（需明确标注）
- 教学演示目的的示例数据（需明确标注）

## 输入

- **材料需求**：目标材料的化学组成或结构类型
- **数据源**：Materials Project、ICSD、文献DOI
- **验证要求**：数据来源的权威性级别

## 输出

- **结构数据**：带来源标识的材料结构（CIF/POSCAR）
- **来源证明**：Materials Project编号、ICSD编号或文献DOI
- **质量标记**：数据可信度等级（权威/文献/假设）

## 流程节点

### Step 1：确定数据来源优先级
- **操作**：按优先级选择数据来源
- **参数**：
  1. 用户上传（最高优先级）
  2. Materials Project API（MP-xxx）
  3. ICSD数据库
  4. 文献提取（DOI可追溯）
- **工具**：数据源配置
- **质量门禁**：来源优先级正确

### Step 2：获取结构数据
- **操作**：从权威来源获取材料结构
- **参数**：Materials Project API调用、ICSD查询
- **工具**：API客户端、数据库查询
- **质量门禁**：获取成功且格式正确

### Step 3：验证数据可追溯性
- **操作**：检查数据来源标识是否完整
- **参数**：MP编号、ICSD编号、文献DOI
- **工具**：验证脚本
- **质量门禁**：来源标识完整且可验证

### Step 4：标注数据质量
- **操作**：为数据添加质量标记
- **参数**：
  - 权威数据：MP/ICSD编号
  - 文献数据：DOI + 测量条件
  - 假设数据：明确标注"假设/典型值"
- **工具**：元数据生成
- **质量门禁**：质量标记准确

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Materials Project | MP-xxx编号 | [1] | 最权威的计算数据来源 |
| ICSD | 编号 | [1] | 实验晶体结构数据库 |
| 文献DOI | 10.xxxx/xxxxx | [1] | 可追溯的文献来源 |
| 测量条件 | 温度、方法等 | [2] | 性能数据必须标注 |
| 数据质量等级 | 权威/文献/假设 | [1] | 根据来源确定 |

## 边界与分流

**数据来源优先级**：
- **用户上传**：最高优先级，视为最可靠
- **Materials Project**：计算数据权威来源
- **ICSD**：实验数据权威来源
- **文献提取**：需DOI可追溯
- **假设数据**：仅用于方法验证，标注"假设/典型值"

**异常处理**：
- 无法获取权威数据时，标记PARTIAL而非PASS
- 假设数据不得作为正式结论依据
- 文献数据需验证DOI有效性

## 质量检查

- **来源标识**：每个结构数据必须有来源编号/DOI
- **格式验证**：CIF/POSCAR格式正确
- **可验证性**：来源编号可在对应数据库查询
- **质量标注**：假设数据明确标注

## 回退策略

- 若API不可用，使用本地缓存数据（需标注）
- 若文献DOI不可验证，标注"文献来源未验证"
- 若所有来源不可用，标记BLOCKED

## 资源召回建议

**何时应召回本卡片**：
- 获取材料结构数据用于计算
- 需要验证数据来源的权威性
- 需要确保数据可追溯性

**配套资源**：
- `matchem-materials-project-api`：Materials Project API访问
- `matchem-blocked-trigger-rules`：输入缺失处理
- `matchem-vasp-aimd-ionic-conductivity`：计算验证

## 证据来源

[1] "Unsupervised discovery of solid-state lithium ion conductors", Ying Zhang et al., Nature Communications, 2019, DOI: 10.1038/s41467-019-13214-1

[2] "A database of experimentally measured lithium solid electrolyte conductivities evaluated with machine learning", Cameron J. Hargreaves et al., npj Computational Materials, 2023, DOI: 10.1038/s41524-022-00951-z
