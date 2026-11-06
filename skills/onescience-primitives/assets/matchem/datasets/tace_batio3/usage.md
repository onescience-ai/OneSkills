## access
优先显式 `TACE_BATIO3_FILE`；否则 `${ONESCIENCE_DATASETS_DIR}/matchem/TACE/BaTiO3.xyz`，未设根变量时回退 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/TACE/BaTiO3.xyz`。本卡绑定文件，不自动扩展为整个 TACE 数据库。

## data_schema
基础 batch 为 `atomic_numbers,pos,cell,pbc,energy,forces,stress`；扩展目标保持 `born_effective_charges(N,9或3,3),polarization(3),polarizability(9或3,3)`，条件为 `electric_field(3)`，来源为 `original_dataset_index`。shape 转换须显式登记轴序，逐字段保留有效性 mask。

## task_usage
用于 TACE 或其它支持电响应向量/张量输出的模型接入、小样本多任务拟合、极化/Born 有效电荷预测及电场条件化数据准备。普通能量/力 MLIP 只能消费其支持的目标，不能因此宣称已使用完整响应信息。

## integration_paths
`ASE extxyz -> 标签位置解析 -> 基础结构batch + 电场条件 + 向量/张量target adapter`。确认模型的 E(3)/旋转约定、张量轴定义、损失归一化和极化分支；若输出格式只支持能量/力，响应字段需保留为配套元数据或选择兼容模型，不静默丢弃。

## preparation_requirements
抽查并统计各帧字段有效性、shape、原子数和 electric_field 覆盖，保留 original_dataset_index。取得响应单位、Born 张量轴序、极化分支及应力/电场下能量协议；审计近重复和分组划分，确定多目标 mask/权重与仅从 train 估计的尺度。

## consumption_interfaces
```python
from ase.io import iread
def get_field(atoms, key):
    result = atoms.calc.results if atoms.calc is not None else {}
    for mapping in (result, atoms.arrays, atoms.info):
        if key in mapping:
            return mapping[key]
    raise KeyError(key)

for atoms in iread(dataset_file, format='extxyz'):
    born = get_field(atoms, 'born_effective_charges')
    polarization = get_field(atoms, 'polarization')
    polarizability = get_field(atoms, 'polarizability')
    field = get_field(atoms, 'electric_field')
    # 保留原始shape，取得源轴序/单位协议后再转换为目标模型张量。
```
此接口适配 ASE 标签存放差异，不替代单位、分支和张量语义核实；模型不能消费的字段应明确登记。

## evaluation_protocol
按保留的分组 test 或交叉验证逐折报告有效帧数、energy/force/stress MAE/RMSE，以及 Born 张量、polarization、polarizability 各自的分量误差、单位和归一化。极化误差必须在约定的周期分支/对齐协议下计算，不能直接比较不一致分支。分场条件/来源组报告，不把 59 帧本地误差外推为长时稳定性。

## resource_profile
文件约 2.10 MB、59 个 135 原子结构，读取开销小；张量目标、图邻居和模型规模决定训练内存。适合先在小批中检验 shape 和变换一致性；不需要为了蒸馏启动 DFT、电场计算或训练。

## operation_limits
不覆盖源文件，不把 response 缺失填零，不猜张量轴序/单位/极化分支。结构增广必须同步更新所有相关向量/张量；不支持该变换的 pipeline 应关闭增广并登记限制。
