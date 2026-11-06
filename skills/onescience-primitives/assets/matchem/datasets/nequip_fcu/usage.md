## access
优先显式 `NEQUIP_DATASET_DIR`；否则 `${ONESCIENCE_DATASETS_DIR}/matchem/NequIP`，未设根变量时回退 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/NequIP/`，入口为 `fcu.xyz`。

## data_schema
将 `species/pos` 映射到 `atomic_numbers/pos`，保留 `cell,pbc,energy,forces` 和新建的 frame_id。标签读取兼顾 `atoms.calc.results`，不能仅找 `atoms.info['energy']`；frame_id 仅作来源索引，不代表时间或 split。

## task_usage
适用于 NequIP 或其它原子势模型的含铜 C/H/O 单体系拟合、能量/力联合监督和小规模 reader 验证。训练前需取得单位和划分协议；本卡不保证与某个 NequIP 软件版本默认键名完全一致。

## integration_paths
`ASE extxyz -> 保留计算标签的 Atoms -> NequIP版本对应的dataset/AtomicData adapter`，也可映射到通用材料 datapipe。注册数据实际元素、cutoff 和标签映射，邻居截断由任务/模型确定，不能从晶胞长度反推。

## preparation_requirements
复核帧数、四元素覆盖、cell/PBC、标签形状/有限值与异常构型；取得单位和能量零点协议。建立可复现的轨迹/构型组 split，检查近重复，仅从 train 计算参考能量和归一化。

## consumption_interfaces
```python
from ase.io import iread
for frame_id, atoms in enumerate(iread(dataset_file, format='extxyz')):
    result = atoms.calc.results if atoms.calc is not None else {}
    if 'energy' not in result or 'forces' not in result:
        raise ValueError(f'missing energy/forces at frame {frame_id}')
    energy, forces = result['energy'], result['forces']
    # 保留 atoms.numbers/positions/cell/pbc，并按已核实单位构造目标 batch。
```
不要调用会覆盖原有计算结果的 calculator；转换输出需保留源文件和 frame_id。

## evaluation_protocol
在已保存的分组 test 上计算 energy 总能/每原子 MAE/RMSE、force 分量 MAE/RMSE，注明源单位、换算及能量参考；按 C/Cu/H/O 分别报告力误差和样本量。若仅完成随机帧划分或组来源未知，明确其评测边界，不报告未经验证的动力学稳定性。

## resource_profile
文件约 38 MB，可流式解析，或在内存允许时缓存 6,855 个 52 原子结构；建邻居图和多 worker 缓存可能放大内存。先小批验证，再按原子数和邻居数决定 batch，不必重新生成或下载数据。

## operation_limits
不修改源 xyz、不填补 stress、不按能量量级猜单位、不随机泄漏相邻构型。所有 split 清单、统计和模型缓存写到独立目标目录。
