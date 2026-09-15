# 实例任务：序列窗口与模型准备 @ B64

- domain: bio
- 骨架: tk-bio-69ee987b
- 场景: sc-9c3a83c8 (B64)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- B64
- 关联论文: Caduceus: Bi-Directional Equivariant Long-Range DNA Sequence Modeling | doi:; DNABERT-2: Efficient Foundation Model and Benchmark For Multi-Species Genome | doi:

## 本实例步骤描述
加载权重并构造满足上下文长度的正反链输入。

## 本实例执行 prompt
加载{CHECKPOINT}，按{CONTEXT_LENGTH}构造序列窗口，并按{REVERSE_COMPLEMENT}生成方向增强特征。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=caduceus.ckpt
- {CONTEXT_LENGTH} | required=False | type=int | var_name=上下文长度 | hint=设置DNA窗口碱基数 | default=131072
- {REVERSE_COMPLEMENT} | required=False | type=bool | var_name=反向互补增强 | hint=是否加入反向互补序列 | default=True

## 本实例产出
- 序列窗口
- 方向映射
- 模型加载记录

## 本实例质量门禁
- 窗口长度符合模型要求
- 中心坐标未偏移
- 反向映射可恢复

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
