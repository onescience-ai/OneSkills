## access
传给 `source.data_dir` 的是直接包含两个 pickle 的目录。使用 OneScience 挂载配置时为 `${ONESCIENCE_DATASETS_DIR}/DeepCFD/data`；共享挂载位置如下。另行解包时使用实际包含两文件的目录，不依赖固定层数。

```yaml
resource_locations:
  - resource_id: deepcfd-paired-flow-grids
    resource_version: unverified
    kind: dataset
    availability: ready
    local_path: null
    shared_path: /public/share/sugonhpcapp01/onestore/onedatasets/DeepCFD/data
    planned_path: null
    required_files:
      - {path: dataX.pkl, role: 几何输入和流动区域, format: pickle, bytes: 159958102}
      - {path: dataY.pkl, role: 对应速度和压力场, format: pickle, bytes: 159958102}
    scope: 981 个成对网格样本，仅数据文件，不含模型权重。
    source: [https://zenodo.org/record/3666056/files/DeepCFD.zip?download=1]
```

## data_schema
`dataX.pkl` 是输入张量，`dataY.pkl` 是目标张量；当前均为 981 个样本、3 通道、`172 x 79` 网格。

## task_usage
适用于 DeepCFD、CNN/UNet 规则网格回归、二维流场 surrogate 和通道加权损失测试。

## integration_paths
使用 `cfd/datapipes/deepcfd` 直接读取 pickle；自定义 reader 应保持 `x/y` 样本顺序一致，并按 split_ratio 划分。

## preparation_requirements
仅反序列化可信 pickle；检查样本数、输入输出网格尺寸和通道顺序，不分别打乱输入与标签。

## consumption_interfaces
batch 为 `{"x": tensor, "y": tensor}`。OneScience 示例的 `get_loss_weights()` 返回目标场各通道的 RMS，示例损失用它除速度平方误差与压力绝对误差。现有 datapipe 从完整 `dataY`（不是仅训练段）计算 RMS；严格留出验证场景应从训练段单独估计并固定使用，不能声称与复现版统计口径相同。

## evaluation_protocol
按任务协议报告指标，并注明分母。若使用每样本网格平方误差，先按通道加总所有样本和空间点的平方误差，再除样本总数；它不同于逐像素 MSE，也不同于训练的加权混合损失。若使用独立 val，需要显式拆分。

## resource_profile
两个解码后 `float32` 数组合计约 305 MiB（按 shape 计算，仅负载）。现有 datapipe 会全量读取，拆分副本、张量转换和训练需额外主存；实际峰值、GPU 显存和吞吐取决于加载器、模型与 batch，未实测。

## operation_limits
无坐标、mask、case 参数；val 不是独立 split；大规模扩展时需改为懒加载。
