# 固态锂离子导体无监督发现工作流

## 适用范围

**触发条件**：
- 需要在材料空间中探索性搜索新型固态锂离子导体（SSLC）
- 用户未指定具体材料，要求"无监督发现"或"探索性发现"
- 需要在大数据库（ICSD/Materials Project）中筛选高离子电导率候选

**适用场景**：
- 新型固态电解质材料发现
- 材料空间探索性筛选
- 基于无监督学习的材料聚类分析

**不适用场景**：
- 已知材料的性能验证（应使用AIMD/DFT验证流程）
- 材料性能预测（应使用监督学习）
- 单一材料的结构优化

## 输入

- **材料数据库**：ICSD（无机晶体结构数据库）或Materials Project中的含锂化合物
- **筛选条件**：可选排除过渡金属化合物（基于固态电解质应用考虑）
- **无标记属性数据**：不需要预先标注的离子电导率数据

## 输出

- **候选材料列表**：经无监督聚类筛选的高概率SSLC候选
- **聚类结果**：材料按阴离子结构特征分组
- **AIMD验证结果**：候选材料的离子电导率预测值

## 流程节点

### Step 1：数据准备与筛选
- **操作**：从ICSD/Materials Project导出含锂化合物结构数据
- **参数**：排除含过渡金属的化合物，保留代表性结构
- **工具**：pymatgen, ASE
- **质量门禁**：数据库条目数 ≥ 2000，代表性结构 ≥ 500

### Step 2：材料表示生成（mXRD）
- **操作**：将晶体结构转换为modified XRD表示
- **参数**：仅保留阴离子亚晶格，统一为S阴离子，体积归一化至40 Å³/anion
- **工具**：pymatgen（XRD计算）
- **质量门禁**：mXRD向量维度=900（2θ范围0-89.98°，步长0.1°）

### Step 3：无监督聚类
- **操作**：对mXRD表示进行聚类分析
- **参数**：
  - 层次聚类(AHC)：欧氏距离 + Ward linkage
  - 谱聚类：递归二分（K=2）
- **工具**：SciPy（层次聚类）、kernlab（谱聚类）
- **质量门禁**：至少使用2种不同聚类方法验证一致性

### Step 4：候选筛选
- **操作**：从聚类结果中提取高概率SSLC候选
- **参数**：选择多个聚类方法结果的交集
- **工具**：Python/NumPy
- **质量门禁**：候选数量 < 100（相对于原始数千化合物大幅缩减）

### Step 5：AIMD模拟验证
- **操作**：对候选材料进行从头算分子动力学模拟
- **参数**：VASP，NVT系综，Nosé-Hoover热浴，2 fs时间步长
- **工具**：VASP
- **质量门禁**：模拟时间 ≥ 100 ps，扩散系数收敛

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 材料来源 | ICSD数据库 | [1] | 无机晶体结构数据库 |
| 数据筛选 | 排除过渡金属化合物 | [1] | 基于固态电解质应用考虑 |
| 表示方法 | mXRD（modified XRD） | [1] | 仅阴离子亚晶格，900维向量 |
| 聚类方法 | AHC + 谱聚类 | [1] | 至少2种方法验证一致性 |
| 验证方法 | AIMD模拟 | [1] | VASP，NVT系综，2 fs时间步 |
| 离子电导率阈值 | > 10⁻⁴ S/cm | [1] | 候选材料的最低要求 |
| 高导电阈值 | > 10⁻² S/cm | [1] | 与已知最佳SSLC相当 |

## 边界与分流

**异常处理**：
- 若数据库中含锂化合物 < 2000，考虑扩展到Materials Project
- 若聚类结果不一致，增加第三种聚类方法验证
- 若AIMD模拟不收敛，延长模拟时间至1000 ps

**降级策略**：
- 若无法获取ICSD数据，使用Materials Project API
- 若AIMD计算资源不足，使用DFT静态计算估算迁移能垒

## 质量检查

- **聚类一致性**：不同聚类方法对已知SSLC的分组一致率 ≥ 80%
- **候选筛选率**：从数千化合物缩减至 < 100候选
- **AIMD验证成功率**：预测SSLC中实际显示高离子电导率的比例 ≥ 20%

## 回退策略

- 若无监督方法失效，回退到基于规则的筛选（如bcc阴离子堆积规则）
- 若AIMD验证全部失败，检查mXRD表示是否捕捉到正确的结构特征

## 资源召回建议

**何时应召回本卡片**：
- 任务目标为"无监督发现"、"探索性搜索"或"材料空间筛选"
- 用户未提供具体材料，要求系统自主发现候选
- 需要在大数据库中识别新型固态离子导体

**配套资源**：
- `matchem-vasp-aimd-ionic-conductivity`：AIMD模拟验证
- `matchem-materials-project-api`：Materials Project数据获取
- `matchem-blocked-trigger-rules`：输入缺失时的BLOCKED规则

## 证据来源

[1] "Unsupervised discovery of solid-state lithium ion conductors", Ying Zhang et al., Nature Communications, 2019, DOI: 10.1038/s41467-019-13214-1

[2] "Recent advances and applications of machine learning in solid-state materials science", Jonathan Schmidt et al., npj Computational Materials, 2019, DOI: 10.1038/s41524-019-0221-0

[3] "A database of experimentally measured lithium solid electrolyte conductivities evaluated with machine learning", Cameron J. Hargreaves et al., npj Computational Materials, 2023, DOI: 10.1038/s41524-022-00951-z
