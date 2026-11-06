## access
优先使用显式 `MPTRJ_DATASET_DIR`，未设置时绑定 `/work2/share/sugonhpcapp01/OneData/wangrui10/matchem/datasets/mptrj/`。此来源不在默认 onedatasets 根目录下，不得擅自改成 `${ONESCIENCE_DATASETS_DIR}/matchem/mptrj`。

## data_schema
统一输出可选 `atomic_numbers,pos,cell,pbc,energy,forces,stress` 及 `mp_id/task_id/calc_id/ionic_step`。extxyz 的 `pos` 与 HDF5/ASELMDB 的 `positions` 要显式映射；每个监督项保留有效性 mask 和原始权重，保留原始能量字段名以记录口径。

## task_usage
用于 MACE 或其它材料 MLIP 的能量/力训练、带应力训练及过滤视图接入验证。974 帧 smoke 仅用于 reader、batch、损失连通性检查。原始 JSON 适合追溯附加属性，不能未经 schema 核实直接作为现成训练 batch。

## integration_paths
小规模走 `ASE extxyz -> AtomicData`；大规模走 HDF5 分片 reader 或本地 ASELMDB 专用 reader。三类视图择一作为主样本源。HDF5 中先解码字符串、识别 `None`、读取 `property_weights` 再构造 batch；ASELMDB 不能套用 OMat24 reader。

## preparation_requirements
检查 split/shard 是否齐全、元素及原子数范围、cell/PBC、标签形状和有限值、占位项以及能量定义。用分组 ID/结构指纹检查跨 split 重复。只使用训练 split 计算归一化和元素参考能量；已有统计需先验证对应本轮过滤视图。

## consumption_interfaces
ASE 消费者可用 `ase.io.iread(path, format='extxyz')` 流式访问，从 `atoms.calc.results` 提取计算标签。HDF5 用 `h5py.File(path, 'r')`。LMDB 以 `readonly=True, lock=False, create=False, readahead=False, subdir=False` 打开现有文件并使用只读事务，不能创建或更新源库。输出给 `matchem/datapipes/materials` 或模型已声明的 AtomicData 接口。

## evaluation_protocol
在保留的 val 上报告 energy MAE/RMSE（注明总能或每原子能量）、force 分量 MAE/RMSE，有有效 stress 时另报应力误差及单位。按元素、原子数、材料/轨迹组分层；自建 test 明确标注划分来源，不能把 val 分数称为独立 test。不同能量口径分别评测。

## resource_profile
先用 974 帧 smoke 验证，再分片扩展。主 extxyz 逐帧读取，HDF5 每 worker 独立打开句柄，LMDB 每 worker 建立只读连接；避免一次载入原始大 JSON 或全部构型。batch 依据原子数与邻居数限额确定。

## operation_limits
不修改源 split、不覆盖 statistics、不重复合并同源视图。遇到单位、标签或 ID 映射不明时仅做结构读取检查，先补齐协议再启用相应损失；缺失 stress 不补零。
