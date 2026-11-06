# 规划决策

## when to use

在科研/论文复现中规划 SBDD 分子工作（生成/排序/评估）时；安装动作由 installer 处理，本卡仅作资源与依赖清单

## procedure

1. 【依赖】RDKit（化学结构/QED/SA 计算）、AutoDock Vina（对接打分，多配对）、AlphaFold2/ AlphaSpace 类（子口袋提取，DecompDiff 配套）
2. 【模型】DecompDiff / TargetDiff 预训练权重（GitHub 公开）
3. 【能力】PyTorch Geometric 等图学习栈（引导分子用 guide 网络）

## constraints

- 按 source_refs 回溯原始论文，避免断章。

## fallback

- 目标方法不满足条件时，退回生成式深度分子模型（targetdiff/genscore primitive）或咨询对应论文。