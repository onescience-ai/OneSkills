# Conditional Diffusion 复现知识卡

本卡适用于条件扩散、随机下采样/超分辨率、生成式天气和其它 denoising/sampling 论文。它只提供
提取与核验框架，不能把 DDPM、EDM 或常见 U-Net 默认设置写成当前论文事实。

## 先确定参数化和变量角色

必须区分：

- clean state `x0`、noisy state `xt`、sampled noise `epsilon`、condition `c`、timestep/noise level；
- 模型预测的是 `epsilon`、`x0`、`v`、score、residual 还是 preconditioned output；
- condition 是低分辨率场、确定性预报、历史状态、静态特征还是多源组合；
- 训练 target、模型输出、sample state 和评估 target 的关系；
- DDPM 离散 schedule、EDM sigma parameterization 或其它连续时间协议。

不能因为论文称为“denoiser”就默认 noise-prediction MSE，也不能把 `timestep` 和连续 `sigma` 混用。

## 模型六视图提取

- noisy input projection、condition projection 和 timestep/noise embedding 是否独立；
- condition 在输入、各 block、cross-attention 或调制层中的注入位置；
- residual/attention/down-up blocks 的顺序、数量、skip 和分辨率变化；
- 输出 projection 与输入通道、预测参数化的对应关系；
- preconditioning、normalization、scaling 和 classifier-free guidance；
- 多阶段系统中 deterministic mean model 与 stochastic residual model 的边界。

## 训练协议

提取 noise/noise-level 采样分布、forward noising 公式、loss target、权重、reduction、optimizer、EMA、
precision 和更新对象。多阶段训练分别绑定数据、checkpoint 和参数，不能把第一阶段设置传播到
扩散阶段。

## 采样协议

提取：

- 初始噪声 shape 和分布；
- sampler、步数、时间/sigma 序列和更新方程；
- stochastic noise injection、generator/seed 和可重复范围；
- condition 在每一步是否重复使用；
- clipping、thresholding、boundary enforcement 和反归一化；
- ensemble 数量、输出单位和后处理。

## 可验证行为不变量

- forward 对应使用的 noisy state、condition 和 timestep/noise level 敏感；
- 固定 generator 在规格规定范围内可重复，不同 seed 产生合理差异；
- sample 实际迭代调用 denoiser，而不是一次 forward 或与 condition 无关的随机张量；
- 输出 shape/dtype/有限性与输入状态一致；
- loss 的 prediction 与 target 对应正确参数化；
- condition projection、time embedding、residual blocks 和 output projection 实际参与输出；
- 非法 channel、batch、grid、timestep 长度或 sample steps 按规格失败。

