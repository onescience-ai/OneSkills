## content_principle
描述用户指定的 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/omat24-1m/omat24_full.lmdb` 本地 OMat24 衍生视图。资源名 1m 不表示恰好一百万帧，`full` 是该本地视图的文件名，不表示 OMat24 全量主库。2026-11-05 只读读取元数据和样本；此卡不声称已完成全库质量检查、来源去重或训练划分。

## data_schema

本地 LMDB 样本为 MessagePack 映射，原始键恰为 `coord,box,atype,energy,force,virial`。`coord(N,3)`、`box(3,3)`、`atype(N,)`、`force(N,3)`、`virial(3,3)` 为 `{type,shape,data}` 描述，data 是二进制 bytes；按 `np.frombuffer(data, dtype=type).reshape(shape)` 还原，`energy` 为标量。`__metadata__` 包含 `nframes`、`frame_idx_fmt='012d'` 等，样本 key 如 `000000000000`。元数据条目不计入样本。

`atype` 是类型编码，不能直接当作已核实的 atomic number：metadata 的 `system_info.natoms` 是长度 118 的类型计数向量，本次未找到足以证明元素映射的显式 type_map。必须绑定并验证转换器的元素表，不可凭值范围盲目加 1 或直接按 Z 解读。记录无显式 `pbc` 字段，须由来源/转换协议确定边界条件。

## directory_layout
```text
matchem/omat24-1m/
  omat24_full.lmdb/               # 路径实际为目录
    data.mdb
    lock.mdb
```
本卡仅绑定此 LMDB，不将其它 `omat24/1M` 归档自动视为逐帧一致的副本。

## storage_format
目录型 LMDB，value 为 MessagePack；首记录 coord/box/force/virial 为 float64，atype 为 int64。必须按每字段声明的 dtype 解码，不能沿用全量视图 float32 假设。`data.mdb` 大小为 2,191,659,008 bytes，约 2.19 GB。

## scale_spec
`__metadata__.nframes = 1,009,850`，entries 为 1,009,851（含一条 metadata）；frame_idx_fmt 为 012d。首样本 4 原子，atype 示例 `[80,80,79,15]`，本次未全量统计元素/原子数分布，未以这些编码推断元素。

## coverage_spec
OMat24 命名的本地百万级材料势数据视图。具体原始子类、采样策略、元素覆盖和与 full/subsampled 的对应关系未由现有证据确认，不能直接复述全量 OMat24 的所有覆盖作为本子集实测结论。

## label_spec
标量 energy、原子级 force、结构级 virial，配套 coord/box/atype。未确认额外标签、显式 PBC 或可直接使用的 atomic numbers；所有监督字段需完成 type_map、单位及 virial 协议核对后再消费。

## split_strategy
本地未确认现成 train/val/test。样本 key 仅为索引，不代表 split 或时间。新建 split 时优先按来源材料/轨迹分组；无来源 ID 时先做重复/近重复结构审计并保存可复现索引。与全量 OMat24 混合或作为其测试集之前，必须验证同源重叠，不能默认独立。

## constraints

- `virial` 不可直接改名为 stress；先固定单位、符号、体积因子和矩阵/Voigt 约定，再做可回验转换。
- 本地记录未充分声明坐标、能量、力和 virial 的源单位；消费前核实，不能以常见习惯冒充已核实事实。
- 使用只读 LMDB，禁止向源 `lock.mdb`/`data.mdb` 写入；不将临时下载文件、完成标记或日志当作有效样本。
- 数据使用/再分发许可需核对实际来源包的条款；metadata 的 visibility 仅指原语卡可见性。
