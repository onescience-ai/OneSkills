## content_principle
本原语描述 `/work2/share/sugonhpcapp01/OneData/wangrui10/matchem/datasets/omat24/` 中的 OMat24 本地包。归档、解包、下采样、合并和 LMDB 是不同处理视图，存在同源重叠，不能相加作为互不重复的数据规模。本卡以已读取元数据和样本的 full LMDB 为主要可接入视图；2026-11-05 核查未执行全量样本质量扫描。

## data_schema

本地 LMDB 样本为 MessagePack 映射，原始键恰为 `coord,box,atype,energy,force,virial`。`coord(N,3)`、`box(3,3)`、`atype(N,)`、`force(N,3)`、`virial(3,3)` 为 `{type,shape,data}` 描述，data 是二进制 bytes；按 `np.frombuffer(data, dtype=type).reshape(shape)` 还原，`energy` 为标量。`__metadata__` 包含 `nframes`、`frame_idx_fmt='012d'` 等，样本 key 如 `000000000000`。元数据条目不计入样本。

`atype` 是类型编码，不能直接当作已核实的 atomic number：metadata 的 `system_info.natoms` 是长度 118 的类型计数向量，本次未找到足以证明元素映射的显式 type_map。必须绑定并验证转换器的元素表，不可凭值范围盲目加 1 或直接按 Z 解读。记录无显式 `pbc` 字段，须由来源/转换协议确定边界条件。

## directory_layout
```text
omat24/
  train/*.tar.gz
  val/*.tar.gz
  1M/omat24_1M_251210.tar.gz
  extracted/{train,val}/
  extracted_subsampled/{train,val}/
  lmdb/
    omat24_train_full.lmdb/{data.mdb,lock.mdb}
    omat24_val_full.lmdb/{data.mdb,lock.mdb}
    stats.json
    shards/
  lmdb_subsampled/
    omat24_train_subsampled.lmdb/
    omat24_val_subsampled.lmdb/
    stats.json
  lmdb_combined/
    omat24_train_combined.lmdb
    omat24_val_combined.lmdb
  logs/
```
extracted 视图含 `aimd-from-PBE-1000-npt/nvt`、`aimd-from-PBE-3000-npt/nvt`、`rattled-300/500/1000`、`rattled-relax` 等子类。实际文件列表须以当前挂载为准。

## storage_format
full/subsampled 的 `.lmdb` 为含 `data.mdb` 的目录，不能按扩展名当作单文件；根据 `Path(path).is_dir()` 选择 subdir。MessagePack 数组需尊重每条记录声明的 dtype/shape；full 首条记录的浮点数组为 float32，atype 为 int64。不能套用 MPtrj 的 zlib+ASE JSON reader，也不能以 pickle 盲解来源值。

## scale_spec
full LMDB 的 `nframes`：train **89,505,421**，val **908,976**，各库 entries 为样本数加 1 个元数据项。subsampled 的 stats.json 声明 train **11,319,164**、val **116,385**，此数字不是本次全量逐帧验收。combined 与归档的去重关系、完整性未验证，不给出独立总数；文件名中的日期不作为采集日期证明。

## coverage_spec
目录标签显示覆盖基于 PBE 起点的 AIMD、不同温度/系综及扰动/弛豫构型，适合材料势模型预训练和构型泛化评估。目录覆盖不能替代实际类型表、元素频率和温度/来源元数据的逐项验证。

## label_spec
原始标签为标量 `energy`、原子级 `force` 和结构级 `virial`，结构字段为 `coord/box/atype`。full train 首样本为 6 原子，atype 示例 `[31,31,51,51,73,73]`；只记录原编码，不推断化学组成。缺失 PBC、类型映射或单位协议未补齐时，不产生可用的通用 MLIP 监督契约。

## split_strategy
优先保留 full 的 train/val；subsampled 沿用其 train/val 视图，combined 必须先核对合并来源。没有已核实独立 test。抽样不得跨目录混用重叠构型作为训练和评测；需用来源轨迹/材料 ID 或结构指纹审计，并保存选样索引及随机种子。

## constraints

- `virial` 不可直接改名为 stress；先固定单位、符号、体积因子和矩阵/Voigt 约定，再做可回验转换。
- 本地记录未充分声明坐标、能量、力和 virial 的源单位；消费前核实，不能以常见习惯冒充已核实事实。
- 使用只读 LMDB，禁止向源 `lock.mdb`/`data.mdb` 写入；不将临时下载文件、完成标记或日志当作有效样本。
- 数据使用/再分发许可需核对实际来源包的条款；metadata 的 visibility 仅指原语卡可见性。
