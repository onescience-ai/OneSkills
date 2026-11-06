## access
优先显式 `MATTERGEN_MP20_DATASET_DIR`；否则取 `${ONESCIENCE_DATASETS_DIR}/matchem/mattergen/cache/mp_20`，未设置根变量时回退 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/mattergen/cache/mp_20`。本卡绑定缓存，不把 sibling raw CSV 当作相同 schema 的替代入口。

## data_schema
模型侧保留 `structure_id,num_atoms,atomic_numbers,frac_coords,cell` 和每个属性的 value/mask。原 `pos.npy` 映射 `frac_coords`；需要笛卡尔坐标时使用匹配 cell 转换并登记坐标约定。结构级条件不能沿原子维错误拼接。

## task_usage
适用于 MatterGen 晶体生成、条件属性生成、结构重建和小晶胞生成评测；属性预测时按缺失 mask 选择有效样本。不用于未经额外标注的能量/力势模型训练。

## integration_paths
`NPY mmap + JSON属性 -> 累积offset切片 -> 周期晶体对象/模型batch`。与 MatterGen 消费端对齐分数坐标、晶胞参数化、元素词表及条件 mask；通用材料图接口需要显式转为 cartesian pos，不直接把缓存 pos 填入按 Å 解释的字段。

## preparation_requirements
核对 `sum(num_atoms)` 与原子数组长度、cell/ID/属性长度与 S、元素范围、晶胞体积及有限值。保留属性 provenance，检查每种条件有效样本数；核对 split ID 及潜在等价结构。只从 train 拟合条件归一化和元素频率。

## consumption_interfaces
```python
import numpy as np
from pathlib import Path
root = Path(dataset_dir) / 'train'
n = np.load(root / 'num_atoms.npy', mmap_mode='r', allow_pickle=False)
pos = np.load(root / 'pos.npy', mmap_mode='r', allow_pickle=False)
z = np.load(root / 'atomic_numbers.npy', mmap_mode='r', allow_pickle=False)
cell = np.load(root / 'cell.npy', mmap_mode='r', allow_pickle=False)
offset = np.concatenate(([0], np.cumsum(n)))
i = 0
frac = pos[offset[i]:offset[i + 1]]
numbers = z[offset[i]:offset[i + 1]]
cart = frac @ cell[i]
```
属性 JSON 的 `values[i]` 与结构 i 对齐，另取 `isfinite` 构造条件 mask。转换产物应保留原 split/ID 和属性来源标识。

## evaluation_protocol
在保留 test 上按所采用 MatterGen/晶体生成协议评估结构有效性、组成有效性、唯一性、新颖性及有标签条件的达标情况；报告结构匹配容差和有效样本分母。属性误差只在相应 mask 有效项计算。生成样本未经过真实物理评估时，不宣称满足 DFT 稳定性或目标性能。

## resource_profile
约 4.5 万结构、46.4 万原子，NPY 可 mmap，按结构变长组 batch。避免为每个样本重新载入整份属性 JSON，按 split 建索引并缓存属性数组；大批生成的资源需求由模型决定，不由缓存体积推断。

## operation_limits
不合并 test 到训练，不填零缺失属性，不将 formation energy 当 total energy。分数坐标与晶胞/元素必须同结构同顺序；写出到独立目标目录，不覆盖已有缓存。
