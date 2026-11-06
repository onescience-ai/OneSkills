# 梯度引导扩散采样（TAGMol 引导数学与实现）

## scope

TAGMol：把分子生成与属性预测解耦，训练 guide 模型 p_φ(y|M_t,P,t)，推理时用 ∇ 引导扩散采样

## condition

需要对无条件/条件扩散做属性定向采样（如 QED/SA/亲和力引导）时

## 知识正文

- 【概念】TAGMol 框架：生成(p_θ)与属性(p_φ)解耦；guide 在含噪分子上预测属性，推理时梯度引导去噪（§1+§3）
- 【数学】单目标引导：采样 X_{t-1} 时叠加 s·β̃·∇_X log p_φ(y|M_t,P,t)；详细系数见 Eq.12/ Eq.16
- 【数学】多目标引导：各属性独立 guide，梯度按权重 w_y 求和（p=∏_y p_y 因子化，Eq.13-15）
- 【实现】guide 网络：SE(3)-invariant GNN（k-NN 图、距离嵌入、时间步条件），回归/分类均可（Eq.7-9）
- 【实现】guide 训练：用去噪过程同一步的噪声分子 + 真实属性标签回归（RMSE/NLL），与扩散模型时间步对齐（§4.4）
- 【决策】backbone 选择：优先用 TargetDiff，不用 DecompBF（DecompBF 依赖外部 AlphaFold2 提取口袋；引导可替代该外部工具）
- 【失败模式】引导强度 s 过大→生成扰动主导/mode collapse；过小无效；建议 4 个蛋白网格小幅搜索

## source_refs（可回溯）

| kid | uri | version | locator |
|---|---|---|---|
| KNOW-TM-001 | papers/2406.01650.pdf | v1 | §1 + §3 |
| KNOW-TM-002 | papers/2406.01650.pdf | v1 | §3.2 / Eq.12 + Eq.16 |
| KNOW-TM-003 | papers/2406.01650.pdf | v1 | §3.3 / Eq.13-15 |
| KNOW-TM-004 | papers/2406.01650.pdf | v1 | §3.1 / Eq.7-9 |
| KNOW-TM-005 | papers/2406.01650.pdf | v1 | §3.1 / Eq.10 + §4.4 |
| KNOW-TM-006 | papers/2406.01650.pdf | v1 | §4.4 / Experimental setup |
| KNOW-TM-009 | papers/2406.01650.pdf | v1 | §3.2 + §4.4 |

## 来源条目原文（kid -> body）

### KNOW-TM-001 (concept)

> TAGMol将分子生成与属性预测解耦: 训练时刻知觉的guide模型p_phi(y|M_t,P,t), 推理时用其梯度引导扩散采样(目标感知+属性感知)。

### KNOW-TM-002 (concept)

> 引导采样: p_theta,phi(M_{t-1}|M_t,P,y) proportional p_theta(·)p_phi(y|M_{t-1},P,t); 近似X_{t-1}~N(mu_tilde + s·beta_tilde·∇_x log p_phi(y|M,P,t) , beta_tilde I), V不变。s=引导强度; delta=s·beta_tilde·∇_x log p_phi。

### KNOW-TM-003 (concept)

> 多目标: 每个属性独立训练guide, 各属性梯度加权和 delta=sum_y w_y·s_y·beta_t·∇_x log p_y, sum w=1, 可引导多属性同时(如QED+SA+亲和)。

### KNOW-TM-004 (concept)

> guide为SE(3)-invariant GNN: 点在x, 距离embedding d_ij, 用k-NN图(k依赖属性), 预测属性y∈R; 训练用NLL/RMSE; 采样时仅对坐标引导, 对类型通过隐式隐含影响。

### KNOW-TM-005 (concept)

> guide训练: 与去噪过程同 noising, 用保持样本(分子+蛋白+时间步t)回归目标属性; 损失RMSE(NLL); 每属性独立小GNN即可, 不重训扩散模型。

### KNOW-TM-006 (concept)

> 骨干: 用TargetDiff(而非DecompDiff)作为生成backbone, 因DecompDiff依赖外部计算工具(AlphaSpace2提取口袋), TAGMol引导能力自身可替代该工具。

### KNOW-TM-009 (failure_mode)

> 失败模式: 引导强度s过大→生成噪声主导、属性极端、构型崩坏; s过小无收益。需在验证集网格搜索s与权重w; 引导只显式作用坐标, 原子类型以隐式间接影响。
