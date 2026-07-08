# launch

Python API 启动示例：

```sh
python -c "import torch; from onescience.models.fengwu import Fengwu; model=Fengwu(img_size=(721,1440), pressure_level=37, embed_dim=192, patch_size=(4,4), num_heads=(6,12,12,6), window_size=(2,6,12)); surface=torch.randn(1,4,721,1440); z=torch.randn(1,37,721,1440); r=torch.randn(1,37,721,1440); u=torch.randn(1,37,721,1440); v=torch.randn(1,37,721,1440); t=torch.randn(1,37,721,1440); y=model(surface,z,r,u,v,t); print([o.shape for o in y])"
```

# input_schema

- 准备 6 个张量，分别对应地表变量和 `z/r/u/v/t` 五类高空变量。
- 默认参数：`img_size=(721, 1440)`，`pressure_level=37`，`embed_dim=192`，`patch_size=(4, 4)`，`num_heads=(6, 12, 12, 6)`，`window_size=(2, 6, 12)`。
- 默认输入 shape：`surface=(Batch, 4, 721, 1440)`，`z/r/u/v/t=(Batch, 37, 721, 1440)`。
- 所有张量必须共享同一批大小、纬向网格数和经向网格数。
- 高空变量应预先按变量族拆分，每个张量通道数等于 `pressure_level`。
- 输入值应已完成归一化、缺测处理和网格对齐。

# runtime_interfaces

- `forward(surface, z, r, u, v, t)`：执行一次多变量天气场预测。

# main_functions

- `forward`

# execution_resources

- 推荐 GPU 推理或训练，默认全球分辨率与多分支结构显存占用较高。
- 可使用混合精度推理；元数据中标记支持 GPU ONNX runtime 与 cuda graphs。
- 运行环境需具备 OneScience 模块及其气象网络组件。

# operation_limits

- 不直接负责数据读取、归一化、反归一化或滚动预报调度。
- 默认仅覆盖 4 个地表通道和 5 类高空变量分支。
- 变量顺序、压力层顺序、空间网格必须与训练时一致。
- 常见失败模式包括通道数不匹配、不同分支空间尺寸不一致、patch 配置导致恢复尺寸异常。
