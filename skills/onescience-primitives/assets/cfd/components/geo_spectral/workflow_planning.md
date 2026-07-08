# description
GeoSpectral 是非结构几何进入谱域神经算子的桥接层，规划时必须同时考虑坐标质量、modes 截断和输出采样点。

# when_to_use
当 CFD 数据在不规则点、变形网格或需要点到规则潜网格映射时使用；规则网格标准 FNO 可优先使用普通 SpectralConv。

# inputs
- 输入特征通道与点数。
- `x_in/x_out` 坐标维度和归一化范围。
- 目标输出是规则网格还是非结构点。
- modes 与显存预算。
- 是否需要 IPHI 条件映射。

# outputs
- 2D 或 3D GeoSpectralConv 配置。
- `s*` 或 `x_out` 输出策略。
- 可选 IPHI 配置。
- 显存风险评估。

# procedure
1. 判断是否确实需要非结构谱卷积。
2. 归一化坐标并确认维度。
3. 选择 modes 与输出网格尺寸。
4. 先用小 batch 运行 forward 检查 shape 和显存。
5. 再接入 FNO 主干或 decoder。

# constraints
坐标维度必须匹配 2D/3D 实现；modes 不能脱离输出分辨率设置；显式 DFT 不适合无限增大点数。

# next_phase_recommendation
为目标数据集做 modes-sweep 和显存 profiling，必要时引入分块点集或改用图/局部算子。

# fallback
显存不足时降低 modes、降低点数、输出到规则潜网格，或回退到标准 FNO/图神经网络；坐标映射不稳定时暂时移除 IPHI。
