# launch

Python API 启动示例：

```sh
python -c "import torch; from types import SimpleNamespace; from onescience.models.xihe import Xihe; cfg=SimpleNamespace(img_size=(2041,4320), patch_size=(6,12), mask='mask.npy', out_chans=94, in_chans=96, num_groups=32, embed_dim=192); model=Xihe(config=cfg, img_size=(2041,4320), patch_size=(6,12), window_size=(6,12), embed_dim=192, num_heads=(6,12,12,6), in_chans=96, depth=1, mask_full=None, out_chans=94, num_groups=32); x=torch.randn(1,96,2041,4320); y=model(x); print(y.shape)"
```

# input_schema

- 输入为海洋变量二维场，通常形状 `(Batch, in_chans, Height, Width)`。
- 构造函数默认参数：`img_size=(2041, 4320)`，`patch_size=(6, 12)`，`window_size=(6, 12)`，`embed_dim=192`，`num_heads=(6, 12, 12, 6)`，`in_chans=96`，`depth=1`，`mask_full=None`，`out_chans=94`，`num_groups=32`。
- 实际运行以 `config` 字段覆盖为准；示例默认配置为 `config.img_size=(2041, 4320)`，`config.patch_size=(6, 12)`，`config.mask="mask.npy"`，`config.out_chans=94`，`config.in_chans=96`，`config.num_groups=32`，`config.embed_dim=192`。
- 默认输入 shape：`(Batch, 96, 2041, 4320)`。
- 配置对象必须提供模型所需尺寸、通道和掩膜路径。
- 掩膜文件应为二维数组，海洋区域为正值或大于 0.5。
- 输入变量需预先完成归一化和网格对齐。

# runtime_interfaces

- `forward(x)`：执行海洋变量预测。
- `change_mask(mask_full, x, h_out, w_out)`：将全分辨率掩膜降采样到当前 token 网格。

# main_functions

- `forward`
- `change_mask`

# execution_resources

- 默认高分辨率海洋网格显存需求很高，推荐 GPU。
- 掩膜聚合在 CPU/GPU 张量之间转换，需注意设备和 dtype。
- 依赖外部 mask 文件和 OneScience 的 Xihe 组件。

# operation_limits

- 启动示例中的 `mask.npy` 必须替换为真实可读掩膜文件。
- 当前实现高度依赖配置对象字段。
- 不内置海洋数据读取、陆地区域后处理或物理守恒修正。
- 高分辨率默认网格可能不适合直接在小显存设备运行。
