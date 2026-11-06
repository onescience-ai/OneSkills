# 规划决策

## when to use

配体分子已生成，需要把骨架/子结构与蛋白口袋对齐再做下游（打分/优化）

## procedure

1. 【失败模式】配体不贴近蛋白→无法识别蛋白结合口袋/配体子结构（arms 依赖近邻坐标）→组件提取失败，结果失真（§3.3 Challenges）
2. 【流程】将生成配体的 CoM 移动到 docking pose 的 CoM（去除非重原子的 clean CoM），保持分子结构与构象不变地完成空间对齐与近邻处理（CoM Relocation）
3. 【失败模式/反模式】直接用 Vina docking 输出替换原配体会改键型/增删原子（加 H），导致子结构提取错误；应保留原配体仅平移 CoM（Initial Solution）

## constraints

- 按 source_refs 回溯原始论文，避免断章。

## fallback

- 目标方法不满足条件时，退回生成式深度分子模型（targetdiff/genscore primitive）或咨询对应论文。