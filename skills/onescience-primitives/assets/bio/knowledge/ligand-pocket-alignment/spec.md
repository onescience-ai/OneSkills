# 配体-口袋空间对齐与 CoM 重定位（生成后处理）

## scope

生成配体与靶标蛋白空间错位导致的子结构/亚袋提取失败；CoM 重定位方法论

## condition

配体分子已生成，需要把骨架/子结构与蛋白口袋对齐再做下游（打分/优化）

## 知识正文

- 【失败模式】配体不贴近蛋白→无法识别蛋白结合口袋/配体子结构（arms 依赖近邻坐标）→组件提取失败，结果失真（§3.3 Challenges）
- 【流程】将生成配体的 CoM 移动到 docking pose 的 CoM（去除非重原子的 clean CoM），保持分子结构与构象不变地完成空间对齐与近邻处理（CoM Relocation）
- 【失败模式/反模式】直接用 Vina docking 输出替换原配体会改键型/增删原子（加 H），导致子结构提取错误；应保留原配体仅平移 CoM（Initial Solution）

## source_refs（可回溯）

| kid | uri | version | locator |
|---|---|---|---|
| KNOW-P-BD-003 | papers/2501.15631.pdf | v1 | §3.3 / Data Preparation / CoM Relocation |
| KNOW-BD-007 | papers/2501.15631.pdf | v1 | §3.3 / Data Preparation / Challenges |
| KNOW-BD-008 | papers/2501.15631.pdf | v1 | §3.3 / Data Preparation / Initial Solution |

## 来源条目原文（kid -> body）

### KNOW-P-BD-003 (procedure)

> CoM重定位: 将生成配体质心移动到docking pose质心(去除非重原子后的clean CoM), 保持分子结构并使之接近蛋白; 同时用修改版Alphaspace2动态调整Cutoff/Radius最小阈值提取最近口袋/亚结构。

### KNOW-BD-007 (failure_mode)

> 失败模式: 生成配体不贴近蛋白→无法提取蛋白口袋/亚结构(arms依赖近距)→子组件提取失败, 结果失真。解决: docking pose附近重定位(CoM)。

### KNOW-BD-008 (failure_mode)

> 反模式: 直接用Vina重对接pose替换原配体会改键/增删原子(如加H), 导致子结构提取错或分子改变。故保留原配体仅移动CoM。
