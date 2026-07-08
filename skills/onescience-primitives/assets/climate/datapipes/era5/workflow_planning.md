# description

ERA5Datapipe 的规划决策重点是判断一套气象数据是否已经满足 OneScience ERA5 年份 HDF5 协议，并决定应直接复用、做路径/元数据适配，还是新增更上层的数据转换流程。它适合把已整理好的 ERA5 全球规则网格数据切分为连续时间窗，输出给天气预测模型训练、验证、测试或推理流程；不承担原始 GRIB/NetCDF 清洗、变量单位统一、时间轴重采样和数据集划分策略生成。

# when_to_use

- 任务目标是全球或区域规则网格天气预报，且数据已经整理为按年份存储的 HDF5。
- 需要从 ERA5 数据中按 `used_variables` 筛选变量通道。
- 需要用 `input_steps` 与 `output_steps` 构造连续时间窗样本。
- 需要标准化输入/目标，并为预测步生成太阳天顶角特征。
- 训练、验证、测试的年份集合已经由配置或上游规划确定，可以通过 `used_years` 显式传入。

不建议直接使用的场景：

- 数据仍是 GRIB、NetCDF、Zarr 或其他未转 HDF5 的格式。
- 任务需要复杂质量控制、缺失值填补、时间重采样或单位换算。
- 下游模型要求固定保留时间维，但当前 `squeeze(0)` 行为会改变单步样本形状。
- 数据目录只能提供 `data_merged/`，而调用环境无法调整为源码期望的 `data/`。

# inputs

- 数据目录决策输入：
  - `dataset_dir`
  - 年份 HDF5 文件是否位于 `dataset_dir/data/<year>.h5`
  - 统计量是否位于 HDF5 内部，或位于 `dataset_dir/stats/`
- 数据内容决策输入：
  - `fields` shape
  - `fields.attrs["variables"]`
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
  - 模型期望的变量通道数
  - 模型是否接受单步样本的 squeezed shape
  - 训练脚本是否已初始化分布式环境

# outputs

规划阶段应输出以下结构化决策：

```text
datapipe_choice:
  name: ERA5Datapipe
  action: reuse | adapt_path | adapt_metadata | build_converter | reject

data_contract:
  dataset_dir: <resolved path>
  year_files: dataset_dir/data/<year>.h5
  stats_source: embedded_h5 | stats_npy
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
  - missing_variables
  - missing_stats
  - time_axis_assumption
  - squeezed_time_dimension
```

# procedure

1. 确认任务是否属于 ERA5 或 ERA5 风格的规则经纬度天气预测数据读取。
2. 检查数据是否已转为按年份 HDF5，并确认每个目标年份存在对应文件。
3. 对齐路径结构：
   - 若已有 `dataset_dir/data/<year>.h5`，可直接复用。
   - 若只有数据卡中的 `data_merged/<year>.h5`，先规划目录调整、软链接或轻量 adapter。
4. 打开一个样例 HDF5 文件，检查 `fields` 维度、变量属性和 `time_step`。
5. 比对 `used_variables` 与 HDF5 变量名，必要时生成变量映射或要求上游修复数据元数据。
6. 检查统计量来源；若没有 HDF5 内嵌统计量，则确认 `stats/global_means.npy` 和 `global_stds.npy` 可用。
7. 根据任务阶段配置 `used_years`，不要指望 datapipe 内部自动划分 train/val/test。
8. 根据下游模型输入协议评估 `input_steps/output_steps` 与 squeezed shape 是否需要外层 collate/adapter。
9. 构造 `ERA5Datapipe`，调用 `get_dataloader(mode)`，在小样本上验证 batch 五元组的 shape、dtype 和时间索引。
10. 再接入训练或推理主流程。

# constraints

- 不要在没有检查 `fields.attrs["variables"]` 的情况下猜测通道顺序。
- 不要把 train/val/test 划分逻辑塞进 datapipe；应由外部配置明确传入 `used_years`。
- 不要把路径不一致问题交给模型层处理；应在数据目录、数据卡或 datapipe adapter 层解决。
- 若下游模型要求多步时间维始终存在，需要在外层封装或修改 datapipe 返回协议，避免单步 `squeeze(0)` 引发隐式 shape 漂移。
- 若启用分布式采样，训练入口必须已完成分布式初始化；datapipe 只负责 sampler 构造。
- `cos_zenith` 的时间假设来自年份起点和固定 `time_step`，若数据文件内部存在非均匀时间轴或非 UTC 时间定义，必须先修正数据或替换时间特征生成逻辑。

# next_phase_recommendation

- 若目标是训练天气模型，下一阶段应生成变量列表、年份划分、模型输入通道映射、loss/metric 配置和训练脚本中的 dataloader 初始化代码。
- 若目标是新增 ERA5 派生数据，下一阶段应先写数据转换/校验脚本，把原始数据整理成 `fields + variables + time_step + stats` 协议。
- 若目标是模型适配，下一阶段应验证 batch 中 `invar/outvar/cos_zenith` 的 shape 是否与模型 forward 和训练 loop 匹配，再决定是否加 adapter。
- 若目标是大规模训练，下一阶段应做 I/O 吞吐测试，调整 `num_workers`、batch size、缓存策略和分布式 sampler 设置。

# fallback

- 年份文件缺失：重新解析 `used_years`，检查数据目录；若数据在 `data_merged/`，创建路径适配或修改配置中的 `dataset_dir`。
- 变量缺失：从 HDF5 `variables` 属性生成可用变量清单，修正 `used_variables` 或重建数据元数据。
- 统计量缺失：优先检查 HDF5 是否可内嵌 `global_means/global_stds`；否则生成 `stats/global_means.npy` 与 `global_stds.npy`。
- shape 不符合下游模型：在 datapipe 外层添加 adapter，统一补回时间维或重排维度。
- 时间特征不可信：暂时禁用依赖 `cos_zenith` 的模型分支，或用真实时间轴重写时间戳生成逻辑。
- HDF5 并发读取不稳定：降低 `num_workers`，切换本地缓存，或在训练前做数据分片与 I/O 压测。
