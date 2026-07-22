# 阶段 2：数据与切分规划

目标：生成符合训练契约、且具有完整来源记录的数据计划。数据规划必须从 `training_request.json`、`source_capture.md`、`training_knowledge.md`、已召回资源内容、用户文件和项目原生数据约束派生，不把任何单一领域的数据源作为默认路径。

## 阶段资源评估

进入本阶段前，必须评估已召回资源是否足以支撑数据与切分规划。

- 从已召回资源中筛选能说明数据来源、字段/变量/shape、split、归一化、增强、采样、collate、领域元数据和数据适配方式的资源。
- 若缺少具体模型、datapipe、数据集、预处理或 split 知识，按“数据与切分规划”目标再次调用 `type=resource` 技能补充资源。
- 补充召回时应带上阶段 1 已确认的数据契约缺口，不得用固定领域默认数据源替代。
- 不得沿资源 `path` 直接读取资源文件来补洞；只能使用资源技能返回的 `content`、用户明确提供内容或上游已展开内容。
- 在 `data_preparation_plan.md` 和 `data_manifest.json` 中记录本阶段使用资源、资源限制、补召回结果、缺失字段和假设。

## 分析输入需求

从阶段 1 派生通用数据契约：

- 必需训练、验证、测试数据文件、目录、数据集 ID 或样本选择器
- 必需字段、变量、特征、坐标、结构、mesh、序列或张量 key
- 必需 shape、dimension、dtype、batch 组织和索引约定
- 必需单位、坐标系、参考版本、边界条件或归一化来源
- 必需文件格式和数组布局
- 必需预处理、增强、mask、padding、裁剪、重采样或 transform
- split 规则、时间泄漏风险、样本去重和随机种子要求

在下载、转换或构造数据前，将这些内容写入 `trainer_workdir` 下的 `data_preparation_plan.md`。该文件与 `data_manifest.json` 一起作为后续 codegen 与 execution 阶段的数据契约输入。

## 领域附加规则

仅在对应领域任务中应用以下附加检查：

- 气象/地球系统：检查时间范围、历史窗口、预测窗口、时间步长、变量、level、网格、投影、经纬度约定和单位。
- 生信：检查物种、参考基因组或蛋白数据库版本、序列坐标、feature schema、样本表、batch/condition 元数据和隐私/合规边界。
- 材料：检查结构文件、组成、晶胞、周期边界、单位、描述符、势函数或模型要求的 graph/neighbor 参数。
- 流体/CFD：检查 mesh、边界条件、初始条件、时间步、物理变量、无量纲参数、守恒量和网格/场数据布局。
- 通用科研模型：检查输入 schema、单位、坐标/索引、预处理和输出解释所需的元数据。

除非用户要求运行或明确允许获取数据，不要下载大型数据集。对于仅规划任务，生成精确的数据需求、split 规则、命令草案或下游 handoff，并将实际获取标记为 `pending`。

## 格式转换和切分适配

优先使用领域库、项目原生 datapipe 或已有 dataset 类，不要临时手写脆弱解析：

- 通用数组/表格：numpy、pandas、pyarrow、xarray、zarr、h5py
- 气象/地球系统：xarray、cfgrib、eccodes、netCDF4、zarr、xESMF、模型提供工具
- 生信：Biopython、pysam、anndata、scanpy、pyfaidx、Bio.PDB、RDKit 等与任务匹配的工具
- 材料：ASE、pymatgen、matscipy、e3nn/torch-geometric 相关 adapter 或模型原生工具
- 流体/CFD：meshio、vtk/pyvista、h5py、xarray、numpy/scipy 或项目原生 reader

将 `data_manifest.json` 保存到 `trainer_workdir`，并在其中保留元数据；该文件是后续 codegen 与 execution 阶段的数据输入清单与来源记录：

```json
{
  "train_source": "",
  "val_source": "",
  "test_source": "",
  "files": [],
  "input_format": "",
  "domain_metadata": {},
  "schema": {},
  "split_strategy": "",
  "sampling": "",
  "normalization": "",
  "augmentation": "",
  "collate_or_batching": "",
  "output_files": []
}
```

## 决策门

在至少存在一个可说明的训练样本契约或明确的代码生成目标之前，不要进入训练执行；如果用户明确只要求生成代码或规划则例外。如果无法准备数据，返回 `blocked` 或 `partial`，并在 `execution_result.observation.missing` 中说明缺少的数据源、凭据、字段映射、schema、split、单位、参考版本、结构、mesh 或其它关键元数据。
