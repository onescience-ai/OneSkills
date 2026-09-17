# SAbDab抗体结构数据库

## 适用范围
适用于需要获取真实抗体结构数据的场景，包括：
- 抗体设计任务的数据输入
- 结构预测模型的验证参考
- 抗体序列-结构关系研究
- 治疗性抗体分析

不适用场景：
- 需要序列数据而非结构数据（使用OAS数据库）
- 需要抗体-抗原复合物结构（需额外筛选）

## 输入
- **查询条件**：PDB ID、抗体名称、序列相似性、分辨率范围
- **数据格式**：REST API查询或批量下载
- **筛选参数**：物种、抗体类型、实验方法

## 输出
- **结构文件**：PDB格式抗体结构
- **元数据**：分辨率、实验方法、物种来源、CDR编号
- **序列信息**：重链/轻链序列、CDR区域序列

## 流程节点
1. 数据查询 → 2. 数据筛选 → 3. 数据下载 → 4. 数据解析 → 5. 质量验证
   - 步骤1：使用SAbDab API或网站查询抗体结构
   - 步骤2：根据需求筛选分辨率、物种等参数
   - 步骤3：下载PDB结构文件和元数据
   - 步骤4：解析PDB文件，提取抗体区域
   - 步骤5：验证结构完整性和质量

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| resolution_cutoff | 3.0Å | [1] | 高分辨率结构质量更好 |
| experimental_method | X-ray/Cryo-EM | [1] | 实验方法影响结构质量 |
| antibody_type | IgG/Nanobody | [1] | 不同抗体类型结构差异 |
| cdr_numbering | IMGT | [1] | CDR区域编号方案 |

## 边界与分流
- **结构缺失**：标记为无结构数据，使用序列数据替代
- **低质量结构**：警告并建议使用高质量结构
- **多链复合物**：提取抗体链，忽略抗原链

## 质量检查
- 验证PDB文件格式正确性
- 检查分辨率和实验方法
- 确认CDR区域定义完整

## 回退策略
- SAbDab不可用时：使用PDB直接查询
- 数据下载失败时：使用缓存数据或模拟数据
- 结构质量问题时：降低筛选标准或选择替代结构

## 资源召回建议
- 当任务需要真实抗体结构数据时召回
- 当需要验证生成抗体质量时召回
- 配套资源：ANARCD编号工具、CDR-RMSD计算方法

## 证据来源
[1] Schneider C, et al. SAbDab in the age of biotherapeutics: updates including SAbDab-nano, the nanobody structure tracker. Nucleic Acids Research. 2021;49(D1):D1368-D1374. DOI: 10.1093/nar/gkab1050
[2] Raybould MIJ, et al. Thera-SAbDab: the Therapeutic Structural Antibody Database. Nucleic Acids Research. 2019;47(D1):D383-D389. DOI: 10.1093/nar/gkz827