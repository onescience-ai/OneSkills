# description

TJDatapipe 的规划决策重点是判断一套中科天机气象数据是否已经满足 OneScience 当前 TJWeather 逐时间步 NetCDF 协议，并决定应直接复用、做路径/元数据适配，还是先新增转换流程。它适合把已经按年份和时间步整理好的 `.nc` 文件切分为多步输入和多步输出窗口，并输出给气象预报模型训练、验证、测试或推理流程；它不承担原始数据清洗、变量单位统一、时间重采样、空间重网格、自动年份划分和质量控制。

# when_to_use

- 任务目标是 TJWeather 或 TJWeather 风格的规则经纬度气象预报。
- 数据已经按 `data/<year>/*.nc` 组织，每个 `.nc` 文件对应一个时间步。
- 每个 NetCDF 文件中存在 `fields` 变量，且可以被规整为 `(Channels, Height, Width)`。
- 已有 `metadata.json` 描述可用年份和变量列表。
- 已有 `global_means.npy` 与 `global_stds.npy` 统计量。
- 需要用 `input_steps` 和 `output_steps` 构造连续时间窗口。
- 需要按显式年份列表组织 train/val/test 阶段。
- 下游模型接受返回的五元组结构，或可以通过轻量 adapter 适配。

不建议直接使用的场景：

- 数据仍是 GRIB、Zarr、单体长时间轴 NetCDF 或其他未拆分格式。
- 文件目录不是 `data/<year>/*.nc`，且暂时不能调整路径或添加 adapter。
- 变量名、通道坐标或统计量通道顺序无法与 `params.dataset.channels` 对齐。
- 任务需要复杂缺失值填补、质量控制、空间插值、单位换算或时间轴重采样。
- 下游模型不接受单步样本的 squeezed shape。

# inputs

- 数据目录决策输入：
  - `data_dir`
  - `stats_dir`
  - `metadata.json` 是否存在
  - `data/<year>/*.nc` 是否存在
- 数据内容决策输入：
  - `metadata.json["years"]`
  - `metadata.json["variables"]`
  - `.nc` 文件中的 `fields` 变量
  - `fields` 的通道、纬度、经度维度名
  - 通道维坐标是否给出变量名
  - `global_means/global_stds` shape
- 任务配置决策输入：
  - `channels`
  - `train_years`
  - `val_years`
  - `test_years`
  - `input_steps`
  - `output_steps`
  - `time_res`
  - `img_size`
  - `normalize`
  - `batch_size`
  - `num_workers`
  - `distributed`
- 下游约束决策输入：
  - 模型期望变量顺序
  - 模型是否依赖 `cos_zenith`
  - 模型是否要求单步样本保留时间维
  - 训练入口是否已经初始化分布式环境
  - 文件系统是否能承受并发 NetCDF 读取

# outputs

规划阶段应输出以下结构化决策：

```text
datapipe_choice:
  name: TJDatapipe
  action: reuse | adapt_path | adapt_metadata | build_converter | reject

data_contract:
  data_dir: <resolved path>
  stats_dir: <resolved path>
  file_layout: data/<year>/*.nc
  fields_variable: fields
  variables: <selected channels>
  input_steps: <int>
  output_steps: <int>
  time_res: <hours>

split_plan:
  train_years: [...]
  val_years: [...]
  test_years: [...]

runtime_plan:
  interface: train_dataloader | val_dataloader | test_dataloader
  distributed: true | false
  batch_size: <int>
  num_workers: <int>
  normalize: true | false

risk_flags:
  - path_layout_mismatch
  - missing_metadata
  - missing_years
  - missing_variables
  - channel_order_mismatch
  - missing_stats
  - unsorted_time_files
  - inconsistent_img_size
  - squeezed_time_dimension
  - netcdf_io_bottleneck
```

# procedure

1. 确认任务是否属于 TJWeather 或 TJWeather 风格的规则经纬度气象预测。
2. 检查数据是否已经整理为 `data/<year>/*.nc`；若不是，先规划转换或路径 adapter。
3. 读取 `metadata.json`，确认 `years` 与 `variables` 存在。
4. 校验 `train_years`、`val_years`、`test_years` 是显式非空年份列表，并且都在 `metadata.json["years"]` 中。
5. 比对 `channels` 与 `metadata.json["variables"]`，确认任务变量都存在。
6. 打开一个样例 `.nc` 文件，确认存在 `fields` 变量。
7. 推断或确认 `fields` 的 channel/lat/lon 维度；如果通道维带坐标，继续校验变量坐标与 `channels` 匹配。
8. 检查每个目标年份目录的 `.nc` 文件数量是否满足 `input_steps + output_steps`。
9. 检查文件名排序是否等价于时间顺序；必要时在转换阶段重命名或生成排序清单。
10. 检查 `global_means.npy` 和 `global_stds.npy` 是否存在，shape 是否可按 `channel_indices` 切片并广播。
11. 核对 `img_size[-2:]` 与样本裁剪后空间尺寸是否一致，避免 `cos_zenith` 与样本空间维不匹配。
12. 根据下游模型协议评估 `squeeze(0)` 行为是否需要外层补维 adapter。
13. 构造 `TJDatapipe` 并调用目标阶段 dataloader，在小样本上验证返回五元组的 shape、dtype 和时间索引。
14. 再接入训练、验证、测试或推理主流程。

# constraints

- 不要使用比例数字期望 datapipe 自动划分年份；源码要求显式年份集合。
- 不要在未检查 metadata 和文件通道坐标的情况下假设变量顺序。
- 不要让模型层承担路径布局、变量命名或统计量缺失问题；这些应在数据准备或 adapter 层解决。
- 不要假设 `normalize=False` 可以省略统计量文件；源码初始化仍读取统计量。
- 若 `img_size` 与文件实际空间尺寸不同，必须确认裁剪后尺寸与 `cos_zenith` 尺寸一致。
- 若启用分布式采样，训练入口必须先初始化分布式环境；datapipe 只构造 sampler。
- 若下游模型要求固定时间维，必须处理 `squeeze(0)` 引发的单步维度变化。
- 若文件系统无法支撑高并发 NetCDF 读取，应限制 `num_workers` 或先转换为更适合训练的存储格式。

# next_phase_recommendation

- 若目标是训练 TJWeather 气象模型，下一阶段应生成 channels、年份划分、模型输入通道映射、loss/metric 配置和 dataloader 初始化代码。
- 若目标是接入新的 TJWeather 子数据集，下一阶段应先编写转换和校验脚本，统一生成 `metadata.json`、`data/<year>/*.nc` 和 `stats/*.npy`。
- 若目标是模型适配，下一阶段应验证 `invar/outvar/cos_zenith` 的 shape 是否与 forward 和训练 loop 匹配，再决定是否补维、裁剪或重排维度。
- 若目标是大规模训练，下一阶段应做 NetCDF I/O 压测，评估 `num_workers`、batch size、本地缓存和数据格式转换策略。

# fallback

- `metadata.json` 缺失：从数据清单生成年份和变量列表，写回标准 metadata 后再加载。
- 年份目录或 `.nc` 文件缺失：修正 `train_years/val_years/test_years`，检查数据根目录，或建立路径适配。
- 变量缺失：从 `fields` 通道坐标提取可用变量清单，修正 `channels` 或重建数据变量元数据。
- 统计量缺失：按全量变量顺序重新计算 `global_means.npy` 与 `global_stds.npy`。
- 文件排序不可信：在转换阶段重命名为可排序时间戳，或修改外层 adapter 提供稳定排序。
- 空间尺寸不匹配：调整 `img_size`、`patch_size` 或外层裁剪逻辑，使样本和 `cos_zenith` 对齐。
- shape 不符合下游模型：在 datapipe 外层添加 adapter，补回时间维或重排维度。
- NetCDF 读取过慢：降低 `num_workers`，复制到本地高速盘，或离线转换为分片 HDF5/Zarr 等训练友好格式。
