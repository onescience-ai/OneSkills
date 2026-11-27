## architecture_overview

SCFNN（doi:10.1038/s41467-022-29243-2；实现 v1.0.0，提交 `5a9c68719e961ac958ea63a0d75e9f1f331578d7`）将短程基态贡献和长程电场响应分开建模。基态径向描述符截断是 12 Bohr；Ewald 场使用独立的平滑长度 `sigma=8` Bohr，不应用平滑长度替换截断。

## parameter_scale

参数规模按实际构建的五个组件分别统计并求和，注明版本与是否可训练；单个组件的参数量不代表整势。

## architecture_structure

五部件为 GT 力、GT Wannier 中心、Wannier 扰动、O 力扰动、H 力扰动。GT 部件用 D0 短程环境与原子描述符，扰动部件建模局域外场和长程响应。独立应用时，预测中心用于周期 Ewald 场计算，再用该场更新中心直至满足自洽条件；总核力须组合 GT 与场响应并恢复全局原子/坐标顺序。

## input_schema

训练用 `datasets/scfnn-water-reference-v2` 的三场同母组：O 坐标 `(64, 3, 3, n_group)`、H 坐标 `(128, 3, 3, n_group)`、中心 `(256, 3, 3, n_group)`，轴依次为实体、xyz、场、组；O/H 力与相应核坐标同形，立方盒长为 `(3, n_group)`。坐标和盒长统一为 Bohr；力与场的单位由来源和入口配置核对，不能把 V/Å 数值直接送作原子单位。独立推理的构型输入只包括核坐标、晶胞、外场与已拟合状态，不含持出中心和力。

## output_schema

部件输出为中心坐标/位移或 O/H 力项，均有三个笛卡尔分量，需复原尺度、方向和编号。完整预测才可交付 `(192, 3)` 总核力和 `(256, 3)` 中心及残差/收敛记录。所核对源码不提供经证实的直接总能量或应力推理契约；不能以力或应力零填替代。

## shape_transformations

作者由 NumPy 拼装字段转换为 float32，按 O/H 分开并在局部坐标系构造中心映射及特征。GT 描述符按构型、中心和特征排列；导数还含被微分原子和 xyz 轴。校验场轴与母组轴未串接，输出反旋转后按原始 O,H,H 排列并检查单位。

## key_dependencies

参见 `tools/scfnn-train-test`：NumPy/PyTorch、C++ 描述符生成、描述符参数表、训练尺度及同次状态。不依赖外部预训练权重；未核验的版本兼容或 C++ ABI 不能由包清单推断。

## common_modification_points

可配置项包括合法的训练组、有效种子、超参数及与验证范围相容的运行条件。改动描述符、物种/原子映射、截断、场/周期约定或模型构造会影响尺度、权重兼容及科学适用性，不能继续宣称与根源配置等价而不重验。

## implementation_risks

用持出 Wannier 中心算场得到的力是条件化诊断；以预测中心闭环才是独立预测。训练成功或有限损失不能证明闭环收敛和泛化。作者 C++ MD 的既有中心差条件并不构成带迭代上限和非有限检查的静态入口。

## code_references

固定实现见 doi:10.5281/zenodo.5919317 与 `andy90/SCFNN` v1.0.0 的 `train_test/{main.py,main_test.py,train_networks.py,test_networks.py,get_Ewald.py}`、`MDcode/SCFNN/main_final_twobath.cpp`。源码接口和论文 Methods 是不同层次的证据。
