# Materials Project 数据获取工作流

## 适用范围

**触发条件**：
- 需要获取真实材料数据集进行机器学习训练或高通量筛选
- 需要查询特定元素组成、带隙范围或材料属性的材料
- 需要下载Materials Project数据库中的结构、能量、电子结构等数据

**适用场景**：
- CO2光催化剂材料的高通量数据筛选
- 材料属性预测模型的训练数据获取
- DFT计算验证的初始结构获取
- 材料基因组计划的数据基础建设

**不适用场景**：
- 需要实时实验数据的场景（Materials Project为计算数据）
- 需要有机分子或聚合物数据的场景（MP主要为无机材料）
- 需要非公开数据的场景（需申请特殊访问权限）

## 输入

**必要输入**：
- Materials Project API密钥（从 https://next-gen.materialsproject.org/dashboard 获取）
- Python环境（建议使用conda或virtualenv）
- mp-api包（`pip install mp_api`）

**可选输入**：
- 目标元素列表（如 `["Ti", "O"]`）
- 带隙范围（如 `(0.5, 3.0)` 单位eV）
- 材料ID列表（如 `["mp-149", "mp-13"]`）
- 属性字段列表（如 `["material_id", "band_gap", "structure"]`）

## 输出

**主要输出**：
- 结构化材料数据集（JSON/CSV格式）
- 包含字段：material_id, formula_pretty, band_gap, structure, energy, volume等
- 可直接用于机器学习训练的特征矩阵

**验证标准**：
- 数据来源标记为Materials Project
- 字段完整性检查（关键字段不为空）
- 与文献报道的材料属性一致性验证

## 流程节点

### Step 1：环境配置
- **操作**：安装mp-api包并配置API密钥
- **参数**：`pip install mp_api`，设置环境变量`MP_API_KEY`
- **工具**：pip, 环境变量配置
- **质量门禁**：API密钥验证成功，可连接Materials Project服务器

### Step 2：构建查询
- **操作**：根据研究需求构建API查询条件
- **参数**：元素列表、带隙范围、材料属性字段
- **工具**：MPRester客户端
- **质量门禁**：查询条件语法正确，返回有效结果

### Step 3：执行查询
- **操作**：调用API获取材料数据
- **参数**：分页参数、字段选择、结果限制
- **工具**：mpr.materials.summary.search()
- **质量门禁**：返回结果数量符合预期，无API错误

### Step 4：数据处理
- **操作**：清洗、转换、格式化查询结果
- **参数**：输出格式、字段映射、异常值处理
- **工具**：pandas, json
- **质量门禁**：数据完整性100%，格式统一

### Step 5：质量验证
- **操作**：验证数据与文献一致性
- **参数**：参考文献值、允许误差范围
- **工具**：统计分析
- **质量门禁**：关键属性偏差<10%

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| API密钥 | 用户专属 | [1] | 从Materials Project账户获取 |
| 包名 | mp_api | [1] | Materials Project API客户端 |
| 查询端点 | /materials/summary | [1] | 材料摘要数据接口 |
| 带隙单位 | eV | [1] | 电子伏特 |
| 结构格式 | pymatgen Structure | [1] | 晶体结构对象 |
| 分页限制 | 1000 | [2] | 单次查询最大结果数 |
| 并发请求 | 5 | [2] | 建议并发数避免限流 |

## 边界与分流

**异常处理**：
- API密钥无效 → 重新获取密钥
- 网络连接失败 → 检查网络或使用代理
- 查询超时 → 减少单次查询数量或增加超时时间
- 数据不存在 → 调整查询条件或选择替代材料

**降级策略**：
- API不可用时 → 使用AWS Open Data备份
- 数据缺失时 → 标记为"待补充"并记录

## 质量检查

**验证点**：
1. API连接测试：成功获取示例材料数据
2. 数据字段完整性：关键字段（material_id, formula, band_gap）非空
3. 数据类型正确性：数值字段为float，结构字段为pymatgen对象
4. 与文献对比：带隙值与已发表数据偏差<0.2eV

**失败处理**：
- 连接失败 → 重试3次后报告错误
- 数据异常 → 记录异常值并跳过
- 格式错误 → 自动修复或标记

## 回退策略

**替代方案**：
1. 使用AWS Open Data的Parquet格式数据
2. 下载Materials Project数据库快照
3. 使用其他数据库（如ICSD、COD）补充
4. 手动构建小型验证数据集

## 资源召回建议

**何时召回本卡片**：
- 用户需要获取真实材料数据进行机器学习
- 任务涉及材料高通量筛选
- 需要DFT计算的初始结构
- 验证材料属性预测模型

**配套资源**：
- matchem-vasp-dft-workflow（DFT计算验证）
- matchem-co2-photocatalysis-ml-model（机器学习模型）
- matchem-data-driven-screening-workflow（筛选工作流）

## 证据来源

[1] Materials Project Documentation - Getting Started, Materials Project, 2026, https://docs.materialsproject.org/downloading-data/using-the-api/getting-started.md
[2] Materials Project Documentation - Querying Data, Materials Project, 2026, https://docs.materialsproject.org/downloading-data/using-the-api/querying-data.md
[3] Materials Project Documentation - Tips for Large Downloads, Materials Project, 2026, https://docs.materialsproject.org/downloading-data/using-the-api/tips-for-large-downloads.md