# launch
Python API 启动示例：

``` sh
python -c "import torch; from onescience.modules.embedding.timestep_embedding import timestep_embedding; print(timestep_embedding(torch.arange(4), dim=128).shape)"
```

# input_schema
从 batch 中提取 timestep、噪声 level 或 rollout index，转成与模型同设备的一维张量；dim 与后续条件投影层保持一致。

# runtime_interfaces
- `timestep_embedding(timesteps, dim, max_period=10000, repeat_only=False)`：返回正弦时间步嵌入。

# main_functions
- `timestep_embedding`

# execution_resources
CPU/GPU 均可，计算量很小；输出设备跟随 `timesteps.device`。

# operation_limits
仅生成固定正弦特征，不学习时间语义；当前实现对奇数维存在潜在索引风险。
