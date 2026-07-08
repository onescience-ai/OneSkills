# description

用于规划 ProToken 蛋白结构编码阶段，把结构输入转换为可量化的 single/pair latent 表征。

# when_to_use

- 输入是蛋白结构或 template 特征。
- 需要生成 ProToken latent。
- LaProteina 类任务需要结构 token 化参考。

# inputs

- residue、template、torsion、affine 特征。
- mask 和 residue_index。
- encoder 配置与 checkpoint。

# outputs

- single/pair 表征。
- 编码链路适配建议。
- 是否接 bottleneck 的决策。

# procedure

1. 准备 ProToken 预处理特征。
2. 调用 feature initializer。
3. 执行 encoder 更新。
4. 将输出接入 bottleneck 或 inverse folding head。

# constraints

- 输入字段较多且必须一致。
- pair 表征长度平方增长。
- 不直接输出离散 code。

# next_phase_recommendation

接 ProToken bottleneck 生成离散 token，或接 decoder 做重建检查。

# fallback

缺少完整结构特征时，先运行 ProToken 预处理；若过长，裁剪或分块处理。
