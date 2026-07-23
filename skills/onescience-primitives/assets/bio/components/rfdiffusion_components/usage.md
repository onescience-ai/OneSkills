# launch

该原语描述 RFdiffusion 的加噪器、embedding/recycling、迭代结构模拟器与采样 runner。神经网络组件由 `RoseTTAFoldModule` 编排；完整反向扩散由 `Sampler`/`SelfConditioning` 维护状态。

```sh
python -c "from onescience.models.rfdiffusion.diffusion import Diffuser; from onescience.models.rfdiffusion.Embeddings import Recycling; from onescience.models.rfdiffusion.Track_module import IterativeSimulator; from onescience.utils.rfdiffusion.inference.model_runners import Sampler, SelfConditioning; import inspect; print(inspect.signature(Diffuser)); print(inspect.signature(Diffuser.diffuse_pose)); print(inspect.signature(Recycling)); print(inspect.signature(IterativeSimulator)); print(inspect.signature(Sampler.sample_init)); print(inspect.signature(Sampler.sample_step)); print(inspect.signature(SelfConditioning.sample_step))"
```

# input_schema

- `Diffuser` 配置位置/旋转扩散时间表、总步数和 IGSO3 cache；`diffuse_pose` 接受 backbone 坐标、序列、原子 mask 与固定 motif mask。
- embedding 组件读取 MSA、序列、残基索引、模板 `t1d/t2d/xyz_t/alpha_t` 和 recycling 状态。
- `IterativeSimulator` 输入 MSA/pair/state、坐标、残基索引与 motif mask，输出更新轨迹。
- `Sampler` 还需要模型 checkpoint、contig 映射、扩散/去噪配置和可选 guiding potentials。

# runtime_interfaces

- `Diffuser.diffuse_pose(...)`：对 backbone 坐标和 frame 前向加噪。
- `MSA_emb`、`Extra_emb`、`Templ_emb`、`Recycling`：输入与回收组件。
- `IterativeSimulator.forward(...)`：SE(3) 结构更新主干。
- `Sampler.sample_init()`、`Sampler.sample_step(...)`：初始化并执行反向扩散步骤。
- `SelfConditioning`：在 `Sampler` 上增加自条件状态。

# main_functions

- `Diffuser.diffuse_pose`
- `Recycling.forward`
- `IterativeSimulator.forward`
- `Sampler.sample_init`
- `Sampler.sample_step`

# execution_resources

- 依赖 PyTorch、SE(3) 网络、RFdiffusion checkpoint 和 IGSO3 时间表/cache。
- 扩散步数、链长、模板/MSA 特征和 guiding potentials 决定计算量。
- 首次生成旋转扩散 cache 需要可写目录；运行时配置应显式传入该位置。

# operation_limits

- `Diffuser` 只执行前向加噪，不能代替反向采样器。
- `Sampler` 是模型工作流组件，不等同于 `RoseTTAFoldModule` 本身。
- partial diffusion 的 contig 长度、输入结构和 motif mask 必须严格对齐。
- RFdiffusion 组件输出骨架状态，不负责最终序列和侧链设计。
