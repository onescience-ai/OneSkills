# description

CMEMSDatapipe 的规划决策重点是判断一套海洋预报数据是否已经满足当前 OneScience CMEMS 年份 HDF5 协议，并决定应直接复用、做路径/元数据适配，还是先新增数据转换流程。它适合把已整理好的 CMEMS 规则经纬度海洋场切分为连续时间窗口，输出给海洋预测模型的训练、验证、测试或推理流程；它不承担原始 NetCDF/Zarr 清洗、质量控制、单位统一、空间重网格和数据集划分策略生成。

# when_to_use

- 任务目标是 CMEMS 或 CMEMS 风格的全球/区域海洋场预测。
- 数据已经整理为按年份存储的 HDF5，且每个文件包含 `fields` 四维数组。
- 需要按 `used_variables` 筛选海洋变量通道。
- 需要用 `input_steps` 与 `output_steps` 构造连续时间窗口样本。
- 需要用全局统计量做 NaN 均值填补和可选标准化。
- 需要为预测时间步生成太阳天顶角余弦特征。
- 训练、验证、测试的年份集合已经由上游配置或规划逻辑确定，可通过 `used_years` 显式传入。

不建议直接使用的场景：

- 数据仍是 NetCDF、Zarr、GRIB、逐时刻散文件或其他未转换为当前 HDF5 协议的格式。
- 任务需要复杂质量控制、缺失值插值、异常值剔除、单位换算、时间重采样或空间重网格。
- 下游模型要求单步样本也必须保留时间维，但当前返回协议会对单步时间维执行压缩。
- 数据目录缺少 `stats/` 统计量，且无法在接入前补齐。

# inputs

- 数据目录决策输入：
  - `dataset_dir`
  - 年份 HDF5 文件是否位于 `dataset_dir/data/<year>.h5`
  - 统计量是否位于 `dataset_dir/stats/global_means.npy` 与 `global_stds.npy`
  - 是否存在可选 `metadata.json`
- 数据内容决策输入：
  - `fields` shape
  - `fields.attrs["variables"]` 或 `metadata.json["variables"]`
  - `fields.attrs["time_step"]`
  - `global_means/global_stds` shape
- 任务配置决策输入：
  - train/val/test 对应的 `used_years`
  - `used_variables`
  - `input_steps`
  - `output_steps`
  - `normalize`
  - `batch_size`
  - `distributed`
- 下游约束决策输入：
  - 模型期望的变量通道数和顺序
  - 模型是否接受单步样本的 squeezed shape
  - 训练入口是否已经初始化分布式环境
  - 训练或推理阶段是否依赖 `cos_zenith`

# outputs

规划阶段应输出以下结构化决策：

```text
datapipe_choice:
  name: CMEMSDatapipe
  action: reuse | adapt_path | adapt_metadata | build_converter | reject

data_contract:
  dataset_dir: <resolved path>
  year_files: dataset_dir/data/<year>.h5
  stats_source: stats_npy
  variables: <selected variables>
  input_steps: <int>
  output_steps: <int>

split_plan:
  train_years: [...]
  val_years: [...]
  test_years: [...]

runtime_plan:
  mode: train | val | test
  distributed: true | false
  batch_size: <int>
  num_workers: <int>

risk_flags:
  - path_layout_mismatch
  - missing_year_files
  - missing_variables
  - missing_time_step
  - missing_stats
  - nonuniform_time_axis
  - squeezed_time_dimension
```

# procedure

1. 确认任务是否属于 CMEMS 或 CMEMS 风格的规则经纬度海洋预测数据读取。
2. 检查数据是否已经转换为按年份 HDF5，并确认每个目标年份存在对应文件。
3. 对齐路径结构：
   - 若已有 `dataset_dir/data/<year>.h5`，可直接复用。
   - 若是按年份目录、逐时刻文件或其他命名方式，先规划转换脚本、软链接策略或轻量 adapter。
4. 打开一个样例 HDF5 文件，检查 `fields` 是否为 `[TimeSteps, Channels, Height, Width]`。
5. 检查变量名来源；优先使用 `fields.attrs["variables"]`，缺失时确认 `metadata.json["variables"]` 可用。
6. 比对 `used_variables` 与可用变量名，必要时生成变量映射或要求上游修复元数据。
7. 检查 `fields.attrs["time_step"]` 是否存在，并确认它能代表均匀小时级时间轴。
8. 检查 `stats/global_means.npy` 和 `stats/global_stds.npy` 是否存在，且 shape 能覆盖所选通道。
9. 根据任务阶段配置 `used_years`，不要期望 datapipe 内部自动拆分 train/val/test。
10. 根据下游模型输入协议评估 `input_steps/output_steps` 与 squeezed shape 是否需要外层 adapter。
11. 构造 `CMEMSDatapipe`，调用 `get_dataloader(mode)`，在小样本上验证 batch 五元组的 shape、dtype 和时间索引。
12. 再接入训练、验证、测试或推理主流程。

# constraints

- 不要在未检查变量元数据的情况下猜测通道顺序。
- 不要把 train/val/test 划分逻辑塞进 datapipe；应由外部配置明确传入 `used_years`。
- 不要让模型层处理数据路径不一致问题；路径适配应在数据目录、数据卡或 datapipe adapter 层完成。
- 不要假设 `normalize=False` 可以跳过统计量准备；源码初始化仍依赖统计量文件。
- 若下游要求多步时间维始终存在，需要在外层封装或调整 datapipe 返回协议，避免单步 `squeeze(0)` 引发隐式 shape 漂移。
- 若启用分布式采样，训练入口必须已经完成分布式初始化；datapipe 只负责 sampler 构造。
- `cos_zenith` 的时间假设来自年份 UTC 起点和固定 `time_step`；若数据有非均匀时间轴或非 UTC 定义，必须先修正数据或替换时间特征生成逻辑。

# next_phase_recommendation

- 若目标是训练海洋预测模型，下一阶段应生成变量列表、年份划分、模型输入通道映射、loss/metric 配置和训练脚本中的 dataloader 初始化代码。
- 若目标是接入新的 CMEMS 派生数据，下一阶段应先编写数据转换与校验脚本，把原始数据整理成 `fields + variables + time_step + stats` 协议。
- 若目标是模型适配，下一阶段应验证 batch 中 `invar/outvar/cos_zenith` 的 shape 是否与模型 forward 和训练 loop 匹配，再决定是否增加 adapter。
- 若目标是大规模训练，下一阶段应做 I/O 吞吐测试，调节 `num_workers`、batch size、本地缓存策略和分布式 sampler 设置。

# fallback

- 年份文件缺失：重新解析 `used_years`，检查数据目录；若数据在其他目录结构中，创建路径适配或先执行转换。
- 变量缺失：从 HDF5 属性或 metadata 生成可用变量清单，修正 `used_variables` 或重建数据元数据。
- 时间步缺失：补写 `fields.attrs["time_step"]`，或在转换阶段显式生成均匀时间轴协议。
- 统计量缺失：重新计算并保存 `stats/global_means.npy` 与 `stats/global_stds.npy`；在补齐前不要直接进入训练。
- shape 不符合下游模型：在 datapipe 外层添加 adapter，统一补回时间维或重排维度。
- 太阳天顶角不可用或不可信：临时禁用依赖 `cos_zenith` 的模型分支，或用真实时间轴重写时间戳生成逻辑。
- HDF5 并发读取不稳定：降低 `num_workers`，切换本地缓存，或在训练前做数据分片与 I/O 压测。
