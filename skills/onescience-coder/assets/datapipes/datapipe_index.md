# Datapipe Index

## 使用建议

- 先按任务的数据组织方式选最接近的 datapipe，再看模型是否兼容。
- 先确认样本返回协议：是 `dict`、`(x, y, grid)`、PyG `Data/HeteroData`，还是 DGL `Graph`。
- 若 README 没写清字段名、shape 或 split 规则，先补只读探测，再决定生成什么 datapipe。
- 若现有 datapipe 不能直接喂给目标模型，优先加一层最小 adapter，不要直接重写整条训练链。
- 材料领域新增模型时，使用 `materials_<model_route>.md` 命名模型专用数据卡；当前 `materials_mace.md` 是最完整样板。
- 新数据集接入，特别是 benchmark / 多模型对比案例，datapipe 可以参考最接近的数据卡，但模型实现必须回到 `../models/model_index.md` 和具体模型卡确认；不要因为数据卡是 `pdenneval.md` 就把默认 benchmark 模型导入到 `onescience.models.pdenneval.*`。


## 已登记 Datapipe

| Datapipe | 领域 | 典型任务 / 数据组织 | 文档 |
| --- | --- | --- | --- |
| `ERA5Datapipe` | weather | 全球气象格点时序 | [era5.md](./era5.md) |
| `CMEMSDatapipe` | ocean | 海洋格点时序 / 变量切片 | [cmems.md](./cmems.md) |
| `TJDatapipe` | weather | 区域气象数据读取 | [tjweather.md](./tjweather.md) |
| `AirfRANSDatapipe` | cfd | 二维翼型非结构网格 / PyG 图样本 | [airfrans.md](./airfrans.md) |
| `ShapeNetCarDatapipe` | cfd | 车体表面 VTK / PyG 图样本 | [shapenetcar.md](./shapenetcar.md) |
| `DeepCFDDatapipe` | cfd | 规则网格 `pickle -> tensor` | [deepcfd.md](./deepcfd.md) |
| `DeepMind_CylinderFlowDatapipe` | cfd | 网格时序流场 / rollout | [deepmind_cylinderflow.md](./deepmind_cylinderflow.md) |
| `BENODatapipe` | cfd | 椭圆 PDE 异构图 / `npy -> HeteroData` | [beno.md](./beno.md) |
| `CFDBenchDatapipe` | cfd | Tube/Cavity/Cylinder/Dam 基准 / `dict` batch | [cfdbench.md](./cfdbench.md) |
| `DeepMindLagrangianDatapipe` | cfd | 粒子轨迹 TFRecord / DGL 图 | [deepmind_lagrangian.md](./deepmind_lagrangian.md) |
| `EagleDatapipe` | cfd | CFD 时序轨迹 / padding collate | [eagle.md](./eagle.md) |
| `DrivAerML_FigConvUnetDatapipe` | cfd | 车体表面分片二进制图 / 点采样张量 | [drivaerml_figconvunet.md](./drivaerml_figconvunet.md) |
| `Materials MACE pipeline` | materials | extxyz / xyz / DeepMD 转换后 PyG AtomicData / MACE 训练 | [materials_mace.md](./materials_mace.md) |
| `Materials UMA pipeline` | materials | ASE DB/LMDB / custom_stack AtomicData / Hydra 多任务 dataloader | [materials_uma.md](./materials_uma.md) |
| `PDEBenchFNODatapipe` | cfd / operator | HDF5 单文件或多文件 / `(history, target, grid)` | [pdenneval.md](./pdenneval.md) |
| `PDEBenchDeepONetDatapipe` | cfd / operator | HDF5 单文件或多文件 / `(history, target, grid)` | [pdenneval.md](./pdenneval.md) |
| `PDEBenchMPNNDatapipe` | cfd / graph operator | HDF5 -> 时空图训练前样本 | [pdenneval.md](./pdenneval.md) |
| `PDEBenchUNetDatapipe` | cfd / operator | HDF5 -> `(history, target)` | [pdenneval.md](./pdenneval.md) |
| `PDEBenchUNODatapipe` | cfd / operator | HDF5 -> `(history, target, grid)` | [pdenneval.md](./pdenneval.md) |
| `PDEBenchPINODatapipe` | cfd / physics-informed operator | HDF5 + supervised / PDE 双 loader | [pdenneval.md](./pdenneval.md) |
| `ProteinDataset / MultimerDataset` | biology | FASTA/MSA/结构文件发现与 Protenix JSON 推理样本 | [biology_protein.md](./biology_protein.md) |
| `ProtenixInferAdapter` | biology | Protenix / AF3 JSON -> feature dict + AtomArray | [biology_protein.md](./biology_protein.md) |
| `GenomeDataset / Evo2 SimpleFastaDataset` | biology | genome FASTA -> nucleotide/token sequence sample | [biology_genome.md](./biology_genome.md) |

## 新数据集接入时优先参考

- 新数据是二维或三维非结构表面/体网格，并且最后要喂给 PyG 图模型：先看 `AirfRANSDatapipe`、`ShapeNetCarDatapipe`。
- 新数据是规则网格上的 `X -> Y` 回归：先看 `DeepCFDDatapipe`；若带 case 参数、边界条件或自回归时间步，再看 `CFDBenchDatapipe`。
- 新数据是粒子轨迹、需要 DGL 图和 rollout：先看 `DeepMindLagrangianDatapipe`。
- 新数据是时序 CFD 轨迹，并且需要 padding、cluster 或窗口切片：先看 `EagleDatapipe`。
- 新数据是车体表面压力/切应力回归，并且模型直接吃点采样张量：先看 `DrivAerML_FigConvUnetDatapipe`。
- 新数据本身就是 HDF5 PDEBench 风格，目标是 FNO / UNO / PINO / DeepONet / MPNN / UNet：先看 `pdenneval.md`。
- 新任务需要异构图或多节点类型建模：先看 `BENODatapipe`。
- 新任务是 Protenix 统一推理，输入是 Protenix / AF3 JSON：先看 `biology_protein.md` 中的 `ProtenixInferAdapter`。
- 新任务是普通蛋白 FASTA/MSA/结构文件索引，并准备自己写 adapter：先看 `biology_protein.md` 中的 `ProteinDataset` 和 `UnifiedDataPipeline`。
- 新任务是 Evo2 或基因组 FASTA：先看 `biology_genome.md`，并确认是否走 Evo2 自带 tokenizer / dataset。
- 新数据是材料原子构型并要走 MACE：先看 `materials_mace.md`，重点确认 extxyz 字段、E0s、r_max 和 train/valid/test 划分。
- 新数据是材料原子构型并要走 UMA：先看 `materials_uma.md`，重点确认 ASE DB/LMDB、dataset_name、elem_refs、normalizer_rmsd、charge/spin 和 pbc。
- 新数据是材料原子构型但目标模型尚未登记：先标记 `unregistered_material_model`，再参考 `materials_mace.md` 提取需要补齐的格式、字段、构图、划分和验证要求。

## 新 CFD 数据集多模型对比时优先参考

- 非结构翼型、表面点云或网格采样：先看 `AirfRANSDatapipe`；如果原始文件是 VTK / surface mesh，再同时看 `ShapeNetCarDatapipe`。
- 规则网格稳态流场：先看 `DeepCFDDatapipe`；如果数据带 case 参数、边界条件、时间步或 benchmark 风格字段，再看 `CFDBenchDatapipe`。
- HDF5 PDE / operator 数据：先看 `pdenneval.md`，并按目标数据协议选择 `PDEBenchFNODatapipe`、`PDEBenchUNetDatapipe` 或 `PDEBenchUNODatapipe`；但默认 benchmark 模型 `FNO / U_Net / LSM` 仍优先来自 `cfd_benchmark` 模型卡。
- 多模型对比时，优先生成 canonical datapipe，再为 `Transolver / FNO / U_Net / LSM` 生成各自 adapter / view。
- 如果 README 没写清字段名、shape 或 split，先生成只读探测脚本或探测方案，再决定 datapipe 返回协议。

## 兼容性提醒

- `DeepCFDDatapipe` 和 `CFDBenchDatapipe` 都是规则网格数据，但 batch 协议完全不同，不能直接互换。
- `AirfRANSDatapipe`、`ShapeNetCarDatapipe`、`BENODatapipe` 都是图数据，但分别对应 `PyG Data`、`PyG HeteroData` 和不同字段约定。
- `DeepMindLagrangianDatapipe`、`EagleDatapipe` 都处理时序流场，但一个输出 DGL 图，一个输出 padding 后的普通张量字典。
- `PDEBench` family 看似共用一个源文件，但不同模型族的样本返回协议并不相同，写 train 脚本前必须先确认。
- `PDEBench` family 是数据接口和 PDENNEval 示例路线，不代表默认 benchmark 模型也在 `onescience.models.pdenneval` 下；尤其 `LSM` 只能来自 `onescience.models.cfd_benchmark.LSM`。
- `ProteinDataset` 当前最完整的 `__getitem__` 路径是 `input_json_path + protenix_infer_adapter`；非 JSON 分支需要补实现后再直接训练。
- `GenomeDataset` 的通用 pipeline 输出不等于 Evo2 训练 batch；Evo2 优先使用 `Evo2Tokenizer`、`SimpleFastaDataset` 或 examples 中的数据预处理流程。
- MACE 与 UMA 都是材料原子模型，但数据协议完全不同：MACE 主要走 extxyz + PyG AtomicData，UMA 主要走 custom_stack AtomicData + Hydra dataloader，不能直接互换。未来新增材料模型也必须在数据卡里明确自己的数据协议，不能默认套用 MACE 或 UMA。

## 材料数据卡新增接口

新增 `materials_<model_route>.md` 时至少写清：

- 原始格式和推荐中间格式
- 样本返回协议与 batch 结构
- 关键标签字段和单位
- 参考能/归一化/元素表等模型专有统计量
- train/valid/test 划分方式
- 与训练脚本或配置的桥接字段
- 常见不兼容点和最小 adapter 路径

