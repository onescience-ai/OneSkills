## access
优先 `OMAT24_DATASET_DIR`，默认 `/work2/share/sugonhpcapp01/OneData/wangrui10/matchem/datasets/omat24/`。full 入口为 `lmdb/omat24_train_full.lmdb` 和 `lmdb/omat24_val_full.lmdb`；此路径不能自动替换成 onedatasets 根目录。

## data_schema
将 `coord -> pos`、`box -> cell`、`force -> forces` 显式映射；仅在 verified type_map 绑定后将 `atype -> atomic_numbers`。保留原始 `virial` 和 dtype，待物理约定固定后按消费端要求转换。`__metadata__` 只提供索引/分组信息，不进入 batch。

## task_usage
用于大规模材料能量/力/virial 监督、预训练数据接入和按构型来源分层评测。full、subsampled 或 combined 中选择一个明确视图；若资源有限优先验证小批索引，不默认为全量训练授权。

## integration_paths
`LMDB只读事务 -> msgpack.unpackb(raw=False) -> 逐数组解码 -> 已核实type_map/PBC/单位映射 -> 材料图数据接口`。与 `omat24_1m` 原语可能同源，应记录视图 ID 及去重关系。原始归档按其内部 schema 另建 adapter，不假设与本地 LMDB 完全一致。

## preparation_requirements
验证目录完整性、nframes 与实际 key 范围、随机小批可解码性、bytes 长度与 dtype/shape 一致性、有限值和 cell 体积。先核对 type_map、PBC、virial 转换和来源单位，再拟合训练统计。统计/完成标记只能作为线索，不能替代质量检查。

## consumption_interfaces
```python
from pathlib import Path
import lmdb, msgpack, numpy as np
path = Path(dataset_dir) / 'lmdb/omat24_train_full.lmdb'
with lmdb.open(str(path), subdir=path.is_dir(), readonly=True,
               lock=False, create=False, readahead=False, meminit=False) as env:
    with env.begin() as txn:
        raw = txn.get(b'000000000000')
        if raw is None:
            raise KeyError('missing frame 0')
        frame = msgpack.unpackb(raw, raw=False)
        item = frame['coord']
        coord = np.frombuffer(item['data'], dtype=item['type']).reshape(item['shape'])
```
示例只读取一个样本，不包含元素映射或单位转换。输出 batch 通常为 `pos,atomic_numbers,cell,pbc,energy,forces,virial`，以模型声明的契约为准。

## evaluation_protocol
固定数据视图和 train/val，报告能量总量/每原子误差、力分量 MAE/RMSE；virial 或转换后 stress 单独标注定义、单位和归一化。能追溯到 AIMD/rattled 子类时分别报告；无法追溯时注明分层评测缺项。val 不称为独立 test，禁止用重叠下采样副本做测试。

## resource_profile
full 达约九千万训练帧，使用惰性读取、分布式索引和按原子数/邻居数的 batch 限额。`__metadata__` 含大型按帧索引，full train 约 89 MB，不要为读取 nframes 就反序列化为海量 Python 列表；用 buffer/流式 MessagePack 读取需要的头部字段，或消费已核实摘要。不要递归解压所有归档或一次载入整个数据库。

## operation_limits
不写源 LMDB，不擅自合并 full/subsampled/combined，不把 atype 当 Z，不直接将 virial 当 stress。若元素表或单位尚未落实，只完成原字段读取与契约缺口记录，不输出伪造的可训练样本。
