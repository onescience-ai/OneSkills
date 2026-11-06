## access
优先显式 `ESEN_OXIDES_DATASET_DIR`；否则 `${ONESCIENCE_DATASETS_DIR}/matchem/esen/oxides`，根变量未设置时回退 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/esen/oxides/`。读取 `manifest.json` 后绑定对应 `train.db/val.db/test.db`。

## data_schema
输出 `atomic_numbers,pos,cell,pbc,energy,forces,stress` 与 `oxide,polymorph,xc,split,row_id`。使用 `row.toatoms()` 恢复结构，通过 row/计算结果提取标签；应力只在核实六分量协议后转为模型需要的矩阵或向量。

## task_usage
适合 eSEN 或其它材料势模型的氧化物小样本微调、能量/力/应力联合评估及跨多晶型组合测试。预训练 checkpoint 的实际元素/字段支持需单独核对，本卡不证明任何模型已兼容全部目标。

## integration_paths
`ASE SQLite row -> Atoms + 分组元数据 -> FairChem/eSEN 或材料 AtomicData adapter`。训练数据来自 train.db，保留 oxide/polymorph 标签供分层采样和评测，不将组标签误当连续物性。

## preparation_requirements
复核数据库行数、30 组分配、每行标签有限性、原子数、cell/PBC 及应力单位；检查目标 checkpoint 的元素和参考能量配置。仅用 train 估计修正或缩放参数，保留 row_id/组信息以便回查。

## consumption_interfaces
`ase.db.connect(path, use_lock_file=False)` 后只调用 select/get/toatoms 等读取接口，path 必须事先存在，禁止 write/update/delete；要求操作系统级只读时使用 SQLite `mode=ro` reader。数据库不同于 OMat24 LMDB，不使用 msgpack reader。对接目标模型时显式登记 stress 输出单位 `eV/Angstrom^3`。

## evaluation_protocol
用 val 选择配置，test 只用于最终评估。分别报告 energy 总能/每原子 MAE/RMSE、force 分量 MAE/RMSE、stress 误差及单位，按 oxide/polymorph 展示各组样本数。测试仅 29 条，报告组间差异和样本量，不能将随机行拆分结果与本分组测试直接比较。

## resource_profile
总计 295 行，可缓存为内存结构列表或小型图数据集；主要计算资源由预训练模型、邻居数和 batch 原子数决定。无需为读取此数据申请大规模训练节点，也不启动重建/下载预训练语料。

## operation_limits
不重划随机 split、不重复换算应力、不把不存在的标签填零。源目录只读，adapter 缓存、统计和训练输出写入独立目标目录。
