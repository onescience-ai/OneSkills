# 生物信息学可视化规范

## 常用图表类型

### 基因表达分析
- **热图（Heatmap）**：基因表达矩阵，行为基因，列为样本
- **火山图（Volcano Plot）**：差异表达基因，x轴log2FC，y轴-log10(p-value)
- **MA图**：表达差异可视化

### 序列分析
- **序列标识图（Sequence Logo）**：保守序列motif展示
- **多序列比对可视化**：碱基/氨基酸比对结果
- **系统发育树**：进化关系树状图

### 通路与网络
- **通路富集图**：GO/KEGG富集条形图或气泡图
- **蛋白互作网络**：节点-边网络图
- **和弦图（Chord Diagram）**：基因集关系

### 组学数据
- **PCA/tSNE降维图**：样本分群可视化
- **箱线图/小提琴图**：组间表达量比较
- **Venn图**：集合交集关系

## 三维分子结构

PDB、mmCIF、CIF、蛋白质单体和多分子复合物不使用通用统计图规范。执行器必须通过 `onescience-primitives` 获取 `complex_structure_visualization` 的 content，并按该 primitive 处理：

- 蛋白质单体和多聚体 ribbon/cartoon。
- 蛋白-蛋白、蛋白-核酸、蛋白-配体和混合复合物。
- 默认 protein ribbon、DNA/RNA tube+slab、ligand sticks、metal spheres、water hidden，以及可靠的 pLDDT 视图和组合式自定义视图。
- PyMOL 的 PNG/PML/PSE 或 3Dmol.js、Mol*、NGL 的交互 HTML。

本文件只负责路由提示，不复制 primitive 中的阈值、场景或质量门禁，避免两份规范漂移。

## 配色方案

- **热图**：RdYlBu_r（红-黄-蓝）或viridis
- **差异表达**：显著上调（红）、下调（蓝）、不显著（灰）
- **分组数据**：Set2, Set3（区分不同组）
- **通路图**：按p-value或富集度梯度着色

## 标注规范

- 基因名：斜体（如 *TP53*）
- p-value：科学计数法，标注显著性（*p* < 0.05）
- 表达倍数：log2 Fold Change
- 通路名称：全称或标准缩写（如 KEGG pathway）

## 常用Python库

- `seaborn`：统计可视化
- `matplotlib`：基础绘图
- `scanpy`：单细胞数据
- `biopython`：序列处理
- `networkx`：网络图
- `pymol`：高质量静态结构图、PML 和 PSE
- `3Dmol.js`：轻量交互式 Web 结构视图
- `Mol*`：大型 mmCIF 和复杂结构交互
- `NGL`：浏览器内分子结构渲染
