# scATAC-seq低质量细胞标记任务

## 适用范围

**触发条件**：
- 需要识别和标记低质量scATAC-seq细胞
- 需要在元数据中保留QC状态信息
- 需要支持分层评估和结果追溯

**适用场景**：
- scATAC-seq数据预处理阶段
- 质量控制和细胞过滤
- 分层评估（高质量vs低质量细胞）
- 结果追溯和可重复性分析

**不适用场景**：
- 无QC指标的数据（需要先计算QC指标）
- 已经完成过滤的数据
- 不需要保留QC状态的简单分析

## 输入

- **原始数据**：peak × cell稀疏计数矩阵
- **QC指标**：
  - peak检测数（n_features）
  - TSS富集分数（tss_enrichment）
  - FRiP（Fraction of Reads in Peaks）
- **可选输入**：
  - 原始测序数据（用于计算FRiP）
  - TSS注释文件（用于计算TSS富集）

## 输出

- **QC标记字段**：
  - `obs.qc_pass`：布尔值，True表示通过QC
  - `obs.qc_score`：综合QC分数（0-1）
  - `obs.qc_fail_reason`：失败原因（如适用）
- **过滤后数据**：仅包含通过QC的细胞
- **QC报告**：包含各指标的统计信息

## 流程节点

### Step 1：计算QC指标
- **操作**：计算每个细胞的QC指标
- **指标定义**：
  1. **peak检测数（n_features）**：检测到的peak数量
  2. **TSS富集分数（tss_enrichment）**：TSS区域的reads富集程度
  3. **FRiP（Fraction of Reads in Peaks）**：落在peak内的reads比例
- **实现**：
  ```python
  import numpy as np
  from scipy.sparse import issparse
  
  def calculate_qc_metrics(adata):
      """计算scATAC-seq QC指标"""
      X = adata.X
      if issparse(X):
          X = X.toarray()
      
      # 计算peak检测数
      adata.obs['n_features'] = (X > 0).sum(axis=1)
      
      # 计算总counts
      adata.obs['total_counts'] = X.sum(axis=1)
      
      # 计算FRiP（如果有原始counts）
      # FRiP = peak counts / total counts
      adata.obs['frip'] = adata.obs['total_counts'] / (adata.obs['total_counts'].sum() + 1e-10)
      
      return adata
  ```
- **质量门禁**：QC指标计算正确，无异常值

### Step 2：设定QC阈值
- **操作**：根据数据特征设定合理的QC阈值
- **推荐阈值**：
  | 指标 | 低质量阈值 | 高质量阈值 | 说明 |
  |------|------------|------------|------|
  | n_features | <500 | >1000 | peak检测数 |
  | tss_enrichment | <2 | >4 | TSS富集分数 |
  | frip | <0.1 | >0.3 | FRiP值 |
- **实现**：
  ```python
  def set_qc_thresholds(adata):
      """根据数据分布设定QC阈值"""
      # 使用中位数和标准差设定动态阈值
      n_features_median = adata.obs['n_features'].median()
      n_features_std = adata.obs['n_features'].std()
      
      thresholds = {
          'n_features_min': max(500, n_features_median - 2 * n_features_std),
          'n_features_max': n_features_median + 2 * n_features_std,
          'tss_enrichment_min': 2,
          'frip_min': 0.1
      }
      
      return thresholds
  ```
- **质量门禁**：阈值合理，不会过滤过多细胞

### Step 3：标记低质量细胞
- **操作**：根据阈值标记低质量细胞
- **实现**：
  ```python
  def mark_low_quality_cells(adata, thresholds):
      """标记低质量细胞"""
      qc_pass = (
          (adata.obs['n_features'] >= thresholds['n_features_min']) &
          (adata.obs['tss_enrichment'] >= thresholds['tss_enrichment_min']) &
          (adata.obs['frip'] >= thresholds['frip_min'])
      )
      
      adata.obs['qc_pass'] = qc_pass
      
      # 计算综合QC分数
      adata.obs['qc_score'] = (
          adata.obs['n_features'] / adata.obs['n_features'].max() * 0.4 +
          adata.obs['tss_enrichment'] / adata.obs['tss_enrichment'].max() * 0.3 +
          adata.obs['frip'] / adata.obs['frip'].max() * 0.3
      )
      
      # 记录失败原因
      fail_reasons = []
      for i in range(len(adata)):
          reasons = []
          if adata.obs.iloc[i]['n_features'] < thresholds['n_features_min']:
              reasons.append('low_peak_count')
          if adata.obs.iloc[i]['tss_enrichment'] < thresholds['tss_enrichment_min']:
              reasons.append('low_tss_enrichment')
          if adata.obs.iloc[i]['frip'] < thresholds['frip_min']:
              reasons.append('low_frip')
          fail_reasons.append(','.join(reasons) if reasons else 'pass')
      
      adata.obs['qc_fail_reason'] = fail_reasons
      
      return adata
  ```
- **质量门禁**：标记正确，fail_reason清晰

### Step 4：验证标记结果
- **操作**：检查QC标记的正确性
- **检查项**：
  1. qc_pass字段存在且为布尔值
  2. 通过QC的细胞比例合理（通常>50%）
  3. 失败原因记录清晰
  4. 无遗漏或重复标记
- **实现**：
  ```python
  def validate_qc_marking(adata):
      """验证QC标记结果"""
      # 检查字段存在
      assert 'qc_pass' in adata.obs.columns
      assert 'qc_score' in adata.obs.columns
      assert 'qc_fail_reason' in adata.obs.columns
      
      # 检查通过比例
      pass_ratio = adata.obs['qc_pass'].mean()
      print(f"QC pass ratio: {pass_ratio:.2%}")
      
      # 检查失败原因分布
      fail_reasons = adata.obs[~adata.obs['qc_pass']]['qc_fail_reason']
      print(f"Fail reason distribution:")
      for reason in fail_reasons.unique():
          count = (fail_reasons == reason).sum()
          print(f"  {reason}: {count}")
      
      return True
  ```
- **质量门禁**：所有检查项通过

### Step 5：生成QC报告
- **操作**：汇总QC统计信息
- **内容**：
  - 总细胞数、通过QC细胞数、未通过细胞数
  - 各QC指标的分布统计
  - 失败原因分布
  - 过滤前后数据对比
- **实现**：
  ```python
  def generate_qc_report(adata):
      """生成QC报告"""
      report = {
          'total_cells': len(adata),
          'qc_pass_cells': adata.obs['qc_pass'].sum(),
          'qc_fail_cells': (~adata.obs['qc_pass']).sum(),
          'pass_ratio': adata.obs['qc_pass'].mean(),
          'metrics_stats': {
              'n_features': {
                  'mean': adata.obs['n_features'].mean(),
                  'median': adata.obs['n_features'].median(),
                  'std': adata.obs['n_features'].std()
              },
              'tss_enrichment': {
                  'mean': adata.obs['tss_enrichment'].mean(),
                  'median': adata.obs['tss_enrichment'].median(),
                  'std': adata.obs['tss_enrichment'].std()
              },
              'frip': {
                  'mean': adata.obs['frip'].mean(),
                  'median': adata.obs['frip'].median(),
                  'std': adata.obs['frip'].std()
              }
          }
      }
      
      return report
  ```
- **质量门禁**：报告完整，信息准确

### Step 6：保存结果
- **操作**：保存标记后的AnnData对象
- **格式**：H5AD
- **内容**：
  - 原始数据
  - QC标记字段（qc_pass, qc_score, qc_fail_reason）
  - QC报告
- **质量门禁**：文件可正常加载，QC字段完整

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| peak检测数阈值 | >500 | [1] | 最低peak检测要求 |
| TSS富集阈值 | >2 | [1] | TSS区域富集程度 |
| FRiP阈值 | >0.1 | [1] | peak内reads比例 |
| QC分数权重 | 0.4/0.3/0.3 | [1] | n_features/tss/frip权重 |
| 最低通过比例 | >50% | [1] | 确保足够细胞用于分析 |

## 边界与分流

- **QC指标缺失**：跳过相应检查，使用其他指标
- **通过比例过低**：放宽阈值或检查数据质量
- **计算资源不足**：使用采样计算QC指标
- **数据格式不匹配**：检查输入数据格式

## 质量检查

- 验证点1：qc_pass字段存在且为布尔值
- 验证点2：通过QC的细胞比例>50%
- 验证点3：失败原因记录清晰
- 验证点4：QC分数计算正确（0-1范围）
- 验证点5：H5AD文件保存成功

## 回退策略

- **首选**：使用标准QC阈值（n_features>500, tss>2, frip>0.1）
- **备选1**：使用动态阈值（基于数据分布）
- **备选2**：仅使用n_features过滤（最简单）
- **最终方案**：跳过QC过滤，注明数据质量风险

## 资源召回建议

- **召回场景**：当需要质量控制和细胞过滤时
- **配套资源**：
  - scATAC-seq数据获取任务（提供原始数据）
  - TF-IDF归一化任务（预处理后数据）
  - 聚类评估任务（支持分层评估）

## 证据来源

[1] Stuart, T. et al. "Signac: Analysis of Single-Cell Chromatin Data". Bioconductor, 2024
[2] Granja, J. et al. "ArchR is a scalable software package for integrative single-cell chromatin accessibility analysis". Nature Genetics, 2021
