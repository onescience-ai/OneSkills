# launch

```sh
python {onescience_path}/onescience/examples/biosciences/RFdiffusion/scripts/run_inference.py inference.output_prefix=outputs/rfdiffusion/sample inference.num_designs=1 contigmap.contigs=[100-100] diffuser.T=50
```

# input_schema

准备 Hydra override、可选 input PDB、contig map、hotspot residue、partial diffusion 参数、symmetry 和 guiding potentials。partial diffusion 时 contig 长度必须与输入结构长度一致。

# runtime_interfaces

- `Sampler`: 初始化模型、配置、contig、diffuser、denoiser。
- `SelfConditioning`: 支持自条件采样。
- `RoseTTAFoldModule.forward`: 神经网络主体去噪。
- `Diffuser.diffuse_pose`: 对 backbone 坐标和 frame 加噪。

# main_functions

- `forward`
- `sample_init`
- `diffuse_pose`
- `denoise_step`

# execution_resources

需要 RFdiffusion 权重、Hydra 配置、可选 IGSO3 schedule cache 和 GPU。首次运行可能生成 schedule cache；复杂 binder/motif/symmetry 任务会增加内存和时间。

# operation_limits

`contract_only` 表示不可直接假设 `OneDiffusion(style="RFdiffusionSampler")` 可运行。RFdiffusion 输出骨架，不等于完成序列和侧链设计；通常需要接 ProteinMPNN 或其他设计/relax 工具。
