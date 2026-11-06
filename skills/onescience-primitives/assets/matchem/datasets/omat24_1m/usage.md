## access
优先 `OMAT24_1M_LMDB` 显式覆盖；否则取 `${ONESCIENCE_DATASETS_DIR}/matchem/omat24-1m/omat24_full.lmdb`，未设根变量时回退 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/omat24-1m/omat24_full.lmdb`。末端路径是目录，不能假定文件不存在或自动创建新库。

## data_schema
原始 `coord,box,atype,energy,force,virial` 显式映射到目标字段；保留 float64 信息，降精度由消费配置决定并记录。atype 需经已核实类型表转换，PBC 和 virial->stress 由来源物理协议确定，不能静默补默认值。

## task_usage
用于百万级材料势数据接入、reader 性能验证及制定划分后的能量/力训练。不能因为视图较小而称其为独立测试基准，也不能当作全量 OMat24 的完整覆盖。

## integration_paths
与 `omat24` 卡使用同一 MessagePack 数组解码协议，但各自保留路径、dtype、样本计数和 split；先建立读取器与类型/单位映射，再输出材料图 batch。不得将其当作 MPtrj ASELMDB 或 ASE SQLite。

## preparation_requirements
确认现有目录、metadata 计数、小批 key 可解码性、bytes 与 dtype/shape、有限值及 cell 体积。取得类型表、单位和来源采样说明；按分组/指纹生成并保存 split，统计量只从所定义 train 拟合。

## consumption_interfaces
用 `lmdb.open(path, subdir=True, readonly=True, lock=False, create=False, readahead=False, meminit=False)`，在只读事务中按 `f'{i:012d}'.encode()` 取记录，再 `msgpack.unpackb(raw, raw=False)`。逐数组以 `np.frombuffer(item['data'], dtype=item['type']).reshape(item['shape'])` 还原；先验证 key 存在，跳过 `__metadata__`，每 worker 独立连接。仅在映射完成后输出模型所需 `atomic_numbers/pos/cell/pbc/energy/forces` 及可选 virial。

## evaluation_protocol
报告自建划分的分组依据、种子、训练/验证/测试帧数及与全量 OMat24 的重叠核查状态；按统一能量/单位定义计算 energy/force MAE/RMSE，virial/stress 另列。来源去重尚未完成时，分数标为本地划分结果，不能宣称独立数据外推。

## resource_profile
约 2.19 GB 磁盘数据、约百万帧，采用 LMDB 惰性随机/顺序读取和按原子数分批；float64 的样本开销不同于 float32 full 视图，不按文件名估计 GPU batch。避免一次把 metadata 的所有帧索引展开为 Python 对象。

## operation_limits
不修改源库、不按顺序 key 虚构现成 split、不盲目合并全量或拿同源视图评测。缺失类型表/单位/划分时先交付读取验证和缺口，不能直接输出未经核实的训练数据。
