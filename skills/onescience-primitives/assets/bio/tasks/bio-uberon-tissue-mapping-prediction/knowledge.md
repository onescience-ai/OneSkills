# UBERON 本体映射与组织特异变异预测

## 适用范围

**触发条件**：
- 需要将组织名称（如 liver、brain）映射为 UBERON 本体标识符
- 需要通过 AlphaGenome 的 ontology_terms 参数指定组织特异性
- 需要对预测结果执行反向互补一致性检查

**适用场景**：
- 小鼠增强子变异的肝脏/大脑组织特异调控预测
- 基于 UBERON 本体的多组织比较分析
- 变异效应预测的方向一致性验证

**不适用场景**：
- 非标准本体体系的组织映射（如 Cell Ontology）
- 无组织特异性要求的通用预测

## 输入

| 输入 | 格式 | 说明 |
|------|------|------|
| 组织名称 | 字符串（英文） | 如 "liver"、"brain" |
| UBERON 映射表 | 预定义映射 | 名称→本体标识符 |
| 变异序列 | DNA 序列（ATCGN） | 参考和替代等位基因 |

## 输出

| 输出 | 格式 | 说明 |
|------|------|------|
| UBERON 本体项 | 字符串列表 | 如 ["UBERON:0002107"] |
| 组织条件预测轨迹 | NumPy 数组 | 特定组织的基因组轨迹预测 |
| 反向互补检查结果 | JSON | 方向一致性日志 |

## 流程节点

### Step 1：组织名称→UBERON 映射
- **操作**：查找预定义映射表，将组织名称转换为 UBERON 本体标识符
- **参数**：常用映射见关键参数表
- **工具**：Python 字典查找或 UBERON API
- **质量门禁**：映射成功、本体标识符格式正确（UBERON:XXXXXXXX）

### Step 2：构建 ontology_terms 参数
- **操作**：将 UBERON 本体项列表传递给 predict_variant 接口
- **参数**：ontology_terms=[list of UBERON IDs]
- **工具**：AlphaGenome API
- **质量门禁**：参数格式正确、至少包含一个 UBERON 项

### Step 3：执行组织条件预测
- **操作**：使用 ontology_terms 参数调用 predict_variant
- **参数**：requested_outputs=[ATAC, CAGE, RNA_SEQ]（标准三种轨迹）
- **工具**：AlphaGenome predict_variant 接口
- **质量门禁**：输出包含组织特异轨迹、无 NaN 值

### Step 4：反向互补检查
- **操作**：对 DNA 序列执行 reverse-complement 后重新预测，对比结果一致性
- **参数**：互补碱基映射 A↔T、C↔G，序列反转
- **工具**：自定义 reverse_complement 函数
- **质量门禁**：正反向预测的方向一致性日志记录

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| UBERON:0002107 | liver（肝脏） | [1] | 小鼠肝脏组织本体项 |
| UBERON:0000955 | brain（大脑） | [1] | 小鼠大脑组织本体项 |
| UBERON:0002107 对应小鼠 | liver, hepatic lobe | [1] | MUS_MUSCULUS 肝脏 |
| UBERON:0000955 对应小鼠 | brain, cerebrum | [1] | MUS_MUSCULUS 大脑 |
| 标准 requested_outputs | [ATAC, CAGE, RNA_SEQ] | [1] | 三种核心输出轨迹 |
| 反向互补映射 | A↔T, C↔G | [1] | DNA 双链互补规则 |
| ontology_terms 参数类型 | List[str] | [1] | UBERON ID 字符串列表 |

## 常用 UBERON 映射表

| 组织名称 | UBERON ID | 说明 |
|----------|-----------|------|
| liver | UBERON:0002107 | 肝脏 |
| brain | UBERON:0000955 | 大脑（泛指） |
| heart | UBERON:0000948 | 心脏 |
| kidney | UBERON:0002113 | 肾脏 |
| lung | UBERON:0002048 | 肺 |
| muscle | UBERON:0001630 | 骨骼肌 |
| adipose | UBERON:0001013 | 脂肪组织 |
| skin | UBERON:0002099 | 皮肤 |
| blood | UBERON:0000178 | 血液 |

## 反向互补检查原理

DNA 序列具有双链对称性：正链序列的反向互补序列应产生一致的调控信号预测。反向互补检查验证模型是否正确处理了链方向信息。

```python
def reverse_complement(seq):
    comp = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}
    return ''.join(comp[b] for b in reversed(seq))

# 检查逻辑
ref_rc = reverse_complement(ref_seq)
alt_rc = reverse_complement(alt_seq)
pred_ref = model.predict(ref_seq)
pred_ref_rc = model.predict(ref_rc)
# 方向一致性 = pred_ref ≈ pred_ref_rc（允许数值容差）
```

## 边界与分流

- **UBERON 映射失败**：使用文本模糊匹配或提示用户确认组织名称
- **requested_outputs 包含非标准轨迹**：记录警告但继续执行
- **反向互补不一致**：记录差异到 quality_report，不阻塞流程
- **组织不在模型支持范围内**：检查 Supplementary Table 1/2 中的可用组织列表

## 质量检查

| 检查项 | 阈值 | 失败处理 |
|--------|------|----------|
| UBERON 映射成功 | 100% | 报告未映射的组织名称 |
| ontology_terms 格式 | 符合 UBERON:XXXXXXXX 模式 | 格式修正 |
| requested_outputs 一致性 | 与标准列表匹配 | 记录偏差 |
| 反向互补方向一致性 | Pearson r > 0.99 | 记录到 quality_report |

## 回退策略

- UBERON API 不可用 → 使用本地预定义映射表
- 反向互补检查计算量大 → 可选跳过，但在报告中标注

## 资源召回建议

- 当任务需要组织特异的变异效应预测时召回本卡
- 配套资源：AlphaGenome 模型配置卡（bio-alphagenome-regulatory-variant-model）

## 证据来源

[1] "Advancing regulatory variant effect prediction with AlphaGenome", Avsec et al., Nature, 2026, DOI: 10.1038/s41586-025-10014-0
[2] "Tissue-specific atlas of trans-models for gene regulation elucidates complex regulation patterns", Dagostino & Gottlieb, BMC Genomics, 2024, DOI: 10.1186/s12864-024-10317-y
[3] "Enhancer DNA methylation: implications for gene regulation", Angeloni & Bogdanovic, Essays in Biochemistry, 2019, DOI: 10.1042/ebc20190030
