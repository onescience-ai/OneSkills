# RNA 结构方法边界

## 常见分析模式

- MFE folding：给出最低自由能结构，适合快速候选筛选。
- Partition function：给出 ensemble 和 base-pair probability，比单个 MFE 更适合评估不确定性。
- RNA-RNA cofold：用于 siRNA/sgRNA target accessibility、lncRNA interaction、duplex 形成评估。
- Consensus folding：需要多序列比对，适合保守结构 ncRNA。
- SHAPE/DMS constraints：需要先检查 reactivity 分布、coverage、replicate concordance。

## 解释边界

- dot-bracket 不表达 pseudoknot 或复杂三维互作。
- 体外 folding 不一定等于细胞内结构，RNA binding protein、修饰和翻译都会改变结构。
- 比较不同序列的能量时，需要长度、条件和约束一致。
