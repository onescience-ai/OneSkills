## architecture_overview
OneScience 软件提供 `onescience.models.mace.mace.ScaleShiftMACE`、`onescience.modules.block.mace_block.RealAgnosticResidualInteractionBlock` 及周期图/自动微分工具。它负责原生构造与加载接口；模型物理规格、完整参数与权重由 [models/mace](../../models/mace/spec.md) 承载，算法组件保留原职责。本卡记录已有安装树及其调用边界，不另造模型或复制算法实现。

## input_schema
构造输入为同身份 companion 的完整 model_config：hidden_irreps/MLP_irreps 还原为 e3nn.o3.Irreps，interaction 类名从原生 mace_block 解析，gate=silu 还原为 torch.nn.functional.silu，atomic_energies 保持数值可转 NumPy 数组。用 float64 构造，传完整 state_dict 并 strict=True 加载；完整数值表见模型卡，不在此重复。

forward 输入为周期邻居图：positions (N,3)、node_attrs (N,元素数)、edge_index (2,E)、batch (N,)、cell、shifts/unit_shifts、head，保留原子顺序与位置梯度。坐标 Å、能量 eV、力 eV/Å 的解释仍须与具体模型/原始数据核对；连续张量 dtype 对齐 float64，图索引为整数。

## output_schema
构造返回原生模型对象；load_state_dict 成功返回 missing_keys/unexpected_keys 信息，strict=True 对不匹配应拒绝而非容错。forward 返回 energy（按图及 head）、forces (N,3) 及按开关请求的应力等；具体 shape 和单位沿模型卡及输入标签验证。文件可读、导入、构造、strict、forward 和科学精度分别判定，导入失败不生成后续成功产物。

## key_dependencies
已观察到 OneScience 模块 0.3.0、发行 0.3.1，Python 3.11.15、PyTorch 2.5.1+das.opt1.dtk25042、e3nn 0.5.8、NumPy 1.26.3、ASE 3.29.0。该组合提供身份和排错依据，不是已通过的兼容推荐。完整安装树及 PyTorch/e3nn 等外部依赖必须保留；位置块所列源码是入口身份清单，不能当作完整可独立安装包。

## implementation_risks
func_utils 包入口急切导入 pangu_utils，后者连至 Megatron，再到 TransformerEngine 的顶层 GPU 属性查询。已有 CPU 原生导入实际报 `RuntimeError: No HIP GPUs are available`，发生于模型构造/strict/forward 之前。1 CPU 线程、0 可见 GPU 的反序列化成功不证明原生 CPU 可运行。发布修复应由工具所有者延迟可选天气/分布式功能导入及设备查询，并验证 CPU 与实际 GPU 分支；目前修复发布与部署尚未完成。

不能用伪 GPU、包级 shadow 模块、strict=False、其他权重或 EMT 绕过所选模型的加载/科学验收。实际 GPU 分支及原生输出未验证，不能把源码核对当执行通过。

## code_references
- 运行环境 `onescience` 包中的 `__init__.py`：OneScience模块版本与包入口。
- 运行环境 `onescience` 包中的`models/mace/mace.py`：MACE/ScaleShiftMACE构造与forward。
- 运行环境 `onescience` 包中的`modules/block/mace_block.py`：interaction类与基本块。
- 运行环境 `onescience` 包中的`modules/func_utils/__init__.py`：可选依赖的实际急切导入边界。
- 运行环境 `onescience` 包中的`modules/func_utils/pangu_utils.py`：天气工具到Megatron的导入边界。
- 运行环境 `onescience` 包中的`modules/func_utils/mace_func_utils.py`：MACE周期图与物理量自动微分。
- 运行环境 `onescience` 包中的`modules/func_utils/mace_irreps_tools.py`：irreps及head处理。
- 运行环境 `onescience` 包中的`modules/layer/mace_radial.py`：径向基与cutoff。
- 运行环境 `onescience` 包中的`modules/equivariant/mace_wrapper_ops.py`：等变操作及可选加速器接口。

软件版本依据包 __init__.py 与既有环境记录；已观察的导入错误、反序列化与重开状态沿 [models/mace 的限制](../../models/mace/spec.md#implementation_risks) 解释。未确认安装包 URL、修复版本或独立发布来源，不从 Python 模块名猜测 pip 产品名。
