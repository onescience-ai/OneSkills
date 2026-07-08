# launch
Python API 启动示例：

``` sh
python -c "from onescience.modules.embedding.unified_pos_embedding import unified_pos_embedding; print(unified_pos_embedding([32,32], ref=4, batchsize=2, device='cpu').shape)"
```

# input_schema
从配置或数据张量分辨率生成 `shapelist`；根据显存预算选择 `ref`；无 GPU 或调试时显式使用 CPU。

# runtime_interfaces
- `unified_pos_embedding(shapelist, ref, batchsize=1, device='cuda')`：返回距离型统一位置编码。

# main_functions
- `unified_pos_embedding`

# execution_resources
CPU/GPU 均可；2D/3D 高分辨率和较大 ref 会产生大矩阵，建议提前估算内存。

# operation_limits
仅支持 1D/2D/3D 规则归一化笛卡尔网格；不处理非结构坐标、周期边界或球面测地距离。
