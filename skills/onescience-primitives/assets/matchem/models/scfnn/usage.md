## launch

从头拟合 SCFNN，使用同一次训练生成的权重和尺度；训练与诊断入口见 `tools/scfnn-train-test`。

```yaml
resource_locations: []
weight_requirement:
  status: not_applicable
  reason: 不读取外部预训练权重；同一次拟合的完整状态与描述符和训练尺度一起用于冷加载。
```

## input_schema

`POTENTIAL_CONFIG` 绑定 s01 放行的训练文件、数据与分组摘要、模型构造和工具提交、描述符/导数、场和单位、实际种子与超参数。预测使用已冻结的同次配置、尺度和合法核坐标/晶胞/场。

## runtime_interfaces

Python 以相同类构造和配置加载同次 `state_dict`：`wannier_GT.pth`、`wannier_peturb.pth`、`force_peturb_O.pth`、`force_peturb_H.pth`、`trained_force_model_statedict.pth`。部件接收按训练尺度处理的特征及相应导数；`test_networks.py` 的 GT 中心诊断另直接读取 `wannier_GT_target_scale.txt` 恢复中心坐标的目标均值。严格持出预处理须复用训练尺度，不能重新拟合。

作者 C++ MD 从运行目录的 `models/` 加载同次的 `traced_wannier_GT.pt`、`traced_wannier_peturb.pt`、`force_peturb_O.pt`、`force_peturb_H.pt`、`traced_trained_model.pt`。同目录必须有四个训练尺度文件：`xO_scalefactor.txt`、`xH_scalefactor.txt`（O/H 中心的 GT 力描述符统计量，分别为 30×3 和 27×3）、`wannier_GT_feature_scale.txt`（GT Wannier 中心的输入描述符统计量，36×3）和 `wannier_GT_target_scale.txt`（恢复中心输出所用的 12 个分量均值）。三个统计量表的列为均值、最小值和最大值。固定提交的 `main_final_twobath.cpp` 启动时无条件读取四表，缺失、不可读或与同次描述符/权重不匹配时不能放行 C++ 消费，即使程序没有明确报告读错。

交接各入口所需状态、同次描述符参数、训练尺度和有效配置，逐项核对文件摘要、整套摘要及数据/模型身份，从冷进程实际加载并保存/重开输出；不能拼接别次或演示权重。

## main_functions

训练入口生成五部件和尺度；同条件下可运行组件诊断。独立自洽预测所需的接口应以预测中心形成周期场，记录停止阈值、迭代上限、残差及非有限处理，返回总力和中心。作者 `main_test.py` 用参考中心计算场，是条件化诊断；C++ MD 是动力学入口，两者均不等同于有界静态单构型自洽预测。

## execution_resources

对小量真实组，1 CPU 线程、0 GPU/DCU 是待测起点，CPU 路线不计显存。float32 核和中心输入下界按实体数×3×场数×组数×4 字节估算，另计描述符导数元素×4、Ewald 中间阵列、参数/梯度及自动微分峰值。磁盘按原始组、特征/导数、五组件、缩放和日志实测；加速时另核设备内存和传输。测量须注明规模、精度和并行度，不外推整库或 MD 窗口。

## operation_limits

参考条件化、部分组件、冷加载失败、不收敛、非有限输出或缺合法 E/F/应力配对都不能作为完整交接。仅有中心收敛的 MD 循环不等于静态入口，也不证明 E/应力可验证。
