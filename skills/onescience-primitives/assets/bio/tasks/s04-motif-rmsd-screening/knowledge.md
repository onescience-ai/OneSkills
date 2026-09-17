# s04 候选结构筛选与质控

## 输入契约

| 输入项 | 来源 | 格式 | 必填 | 说明 |
|--------|------|------|------|------|
| 设计候选 | s03输出 | PDB文件（多个） | 是 | 生成的蛋白骨架结构 |
| 参考基序 | s01输出 | PDB文件 | 是 | 包含功能基序的输入结构 |
| 筛选阈值 | 任务prompt或默认 | float | 否 | 默认0.6Å |
| 保留多样候选 | 任务prompt或默认 | bool | 否 | 默认true |

## 操作步骤

### 步骤1：基序RMSD计算

1. **计算原理**：
   基序RMSD衡量生成骨架中基序区域原子坐标与输入基序的偏差：
   ```
   RMSD = sqrt(1/N * sum_i ||x_i^gen - x_i^ref||^2)
   ```
   其中：
   - N：基序原子数量
   - x_i^gen：生成结构中第i个原子坐标
   - x_i^ref：参考基序中第i个原子坐标

2. **计算脚本**：
   ```python
   import numpy as np
   from Bio.PDB import PDBParser, Superimposer
   
   def calculate_motif_rmsd(gen_pdb, ref_pdb, motif_residues):
       parser = PDBParser(QUIET=True)
       gen_structure = parser.get_structure('gen', gen_pdb)
       ref_structure = parser.get_structure('ref', ref_pdb)
       
       # 提取基序区域原子
       gen_atoms = []
       ref_atoms = []
       for res_id in motif_residues:
           for atom_name in ['CA', 'CB', 'N', 'C', 'O']:
               try:
                   gen_atom = gen_structure[0][(' ', res_id, ' ')][atom_name]
                   ref_atom = ref_structure[0][(' ', res_id, ' ')][atom_name]
                   gen_atoms.append(gen_atom)
                   ref_atoms.append(ref_atom)
               except KeyError:
                   continue
       
       # 最小二乘叠合
       sup = Superimposer()
       sup.set_atoms(ref_atoms, gen_atoms)
       sup.apply(gen_atoms)
       
       return sup.rms
   ```

3. **批量计算**：
   ```python
   def batch_calculate_rmsd(candidates_dir, ref_pdb, motif_residues):
       results = []
       for pdb_file in glob.glob(os.path.join(candidates_dir, "*.pdb")):
           rmsd = calculate_motif_rmsd(pdb_file, ref_pdb, motif_residues)
           results.append({
               "file": os.path.basename(pdb_file),
               "motif_rmsd": rmsd
           })
       return results
   ```

### 步骤2：筛选执行

1. **核心指标筛选**：
   ```python
   def screen_by_motif_rmsd(results, threshold=0.6):
       passed = [r for r in results if r["motif_rmsd"] <= threshold]
       failed = [r for r in results if r["motif_rmsd"] > threshold]
       return passed, failed
   ```

2. **辅助指标计算**（可选）：
   - sc（self-consistency）：结构自洽性分数
   - ptm（predicted TM-score）：预测的TM分数
   - 这些指标可作为辅助参考，但不能替代基序RMSD

3. **指标区别说明**：
   | 指标 | 含义 | 用途 | 阈值 |
   |------|------|------|------|
   | 基序RMSD | 基序区域原子坐标偏差 | 核心筛选指标 | ≤0.6Å |
   | sc | 结构自洽性分数 | 辅助质量评估 | >0.5 |
   | ptm | 预测的TM分数 | 整体结构质量 | >0.7 |

### 步骤3：序列去冗余（可选）

1. **序列聚类**：
   ```python
   from Bio import SeqIO
   from Bio.Seq import Seq
   from Bio.SeqRecord import SeqRecord
   
   def cluster_sequences(sequences, threshold=0.9):
       # 使用CD-HIT或类似工具进行序列聚类
       # 返回去冗余后的序列列表
       pass
   ```

2. **多样性保留**：
   - 保留代表不同聚类的候选
   - 确保序列多样性

### 步骤4：约束质控

1. **硬约束检查**：
   ```python
   def check_hard_constraints(candidate, constraints):
       checks = {
           "fixed_residues_unchanged": True,
           "motif_preserved": True,
           "geometry_valid": True
       }
       
       # 检查固定残基是否改变
       # 检查基序是否保持
       # 检查几何是否有效
       
       return checks
   ```

2. **质控报告生成**：
   ```json
   {
     "total_candidates": 64,
     "passed_screening": 45,
     "failed_screening": 19,
     "motif_rmsd_stats": {
       "mean": 0.45,
       "std": 0.12,
       "min": 0.21,
       "max": 0.89
     },
     "constraint_violations": []
   }
   ```

## 输出产物

| 产物 | 格式 | 说明 |
|------|------|------|
| 入选设计 | PDB文件（多个） | 通过筛选的候选结构 |
| 基序RMSD汇总表 | CSV/JSON | 每个候选的RMSD值 |
| 约束质控报告 | JSON | 硬约束检查结果 |
| 筛选日志 | JSON | 筛选参数和结果统计 |

## 质量门禁

### 必须通过

- [ ] 基序RMSD已计算
- [ ] 阈值≤0.6Å
- [ ] 汇总表已生成
- [ ] 质控报告已生成
- [ ] 硬约束检查完成

### 失败处理

| 失败类型 | 处理方式 |
|----------|----------|
| RMSD计算失败 | 检查PDB格式，重新计算 |
| 无候选通过 | 降低阈值或增加生成数量 |
| 硬约束违反 | 记录违规项，排除候选 |

## 回退策略

- 基序RMSD不达标 → 降低温度重试生成
- 无候选通过 → 增加生成数量
- 质控报告缺失 → 补充生成报告

## 边界说明

**本任务负责**：
- 基序RMSD计算和筛选
- 约束质控检查
- 汇总表和报告生成

**本任务不负责**：
- 输入文件解析（s01）
- 模型权重加载（s02）
- 候选结构生成（s03）

## 证据来源

[1] Watson JL, et al. De novo design of protein structure and function with RFdiffusion. Nature, 2023, 620:1089-1100. DOI: 10.1038/s41586-023-06415-8
