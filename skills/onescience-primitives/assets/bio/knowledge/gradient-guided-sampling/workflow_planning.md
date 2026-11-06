# 规划决策

## when to use

需要对无条件/条件扩散做属性定向采样（如 QED/SA/亲和力引导）时

## procedure

1. 【概念】TAGMol 框架：生成(p_θ)与属性(p_φ)解耦；guide 在含噪分子上预测属性，推理时梯度引导去噪（§1+§3）
2. 【数学】单目标引导：采样 X_{t-1} 时叠加 s·β̃·∇_X log p_φ(y|M_t,P,t)；详细系数见 Eq.12/ Eq.16
3. 【数学】多目标引导：各属性独立 guide，梯度按权重 w_y 求和（p=∏_y p_y 因子化，Eq.13-15）
4. 【实现】guide 网络：SE(3)-invariant GNN（k-NN 图、距离嵌入、时间步条件），回归/分类均可（Eq.7-9）
5. 【实现】guide 训练：用去噪过程同一步的噪声分子 + 真实属性标签回归（RMSE/NLL），与扩散模型时间步对齐（§4.4）
6. 【决策】backbone 选择：优先用 TargetDiff，不用 DecompBF（DecompBF 依赖外部 AlphaFold2 提取口袋；引导可替代该外部工具）
7. 【失败模式】引导强度 s 过大→生成扰动主导/mode collapse；过小无效；建议 4 个蛋白网格小幅搜索

## constraints

- 按 source_refs 回溯原始论文，避免断章。

## fallback

- 目标方法不满足条件时，退回生成式深度分子模型（targetdiff/genscore primitive）或咨询对应论文。