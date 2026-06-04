# Domain Profiles

本文件用于给 `onescience-workflow` 提供领域友好的语义模板。

## 领域模板使用原则

1. 领域模板只负责补充语义，不复制执行逻辑。
2. 领域模板用于帮助理解用户说法、识别约束和完善交接摘要。
3. 无法准确判断领域时，使用 `general-science`，不要强行误判。

## `climate`

常见信号：

- 气象数据
- 区域气象
- 天气预报
- 短期预报
- 全球预报
- ERA5
- 气候预测
- 再分析资料
- 降水、温度、风场、气压

重点约束：

- 时空分辨率
- 多变量对齐
- 历史时段与预报时段切分
- 单位与物理量口径

推荐交接重点：

- 变量清单
- 时间范围
- 网格与分辨率
- 训练 / 推理目标

## `ocean`

常见信号：

- 海洋预报
- 海表温度、盐度、流速、海浪
- 海洋再分析或观测产品

重点约束：

- 深度层
- 区域范围
- 海陆掩码
- 多源数据对齐

推荐交接重点：

- 垂向层次
- 区域裁剪规则
- 变量口径
- 评估指标

## `cfd`

常见信号：

- CFD
- 流体、流场、空气动力学、翼型、绕流、涡脱落
- RANS、LES、Navier-Stokes、Euler 方程
- PDE、PDE 建模、PDE 代理模型、神经算子
- FNO、UNO、U-Net、Transolver、MeshGraphNet、PINO、DeepONet
- VTK、网格、非结构网格、点云、表面压力、压力系数、速度场、阻力/升力

领域归类说明：

- 当用户说的是 PDE 模型、PDE 数据集、PDEBench、神经算子或物理场代理，但没有明确指向天气、海洋、材料或生物时，默认归入 `cfd`
- 当 PDE 任务明确是流体、翼型、管道、腔体、圆柱绕流、气动外形、流场预测或稳态/非稳态流体代理时，归入 `cfd`
- 当 PDE 任务只是抽象数学求解、有限元泛化或未知物理领域时，可先标记为 `cfd` 候选，同时在交接摘要中注明领域仍需确认

重点约束：

- 网格组织方式
- 规则网格、非结构网格、点云或图结构之间的接口差异
- 输入物理量、目标变量、边界条件和几何参数的定义
- 稳态、瞬态、单步预测或多步 rollout 的任务区别
- 数据字段、shape、单位、坐标系和损坏样本的鲁棒处理
- 模型输入协议是否匹配，例如 PyG `Data`、DGL `Graph`、`(x, fx, y)` operator view 或规则网格张量

推荐交接重点：

- 数据集格式与目录结构
- 样本返回协议
- 输入变量、目标变量和几何/边界条件
- 是否需要字段/shape 探测脚本
- 推荐参考 datapipe
- 推荐候选模型与兼容性判断
- 是否需要 adapter / view 层桥接不同模型
- 训练、推理、评估和结果对比目标

推荐 `domain_task_family`：

- `data-interface`：新增或复用 CFD datapipe、数据字段探测、样本协议整理。
- `model-development`：模型适配、单模型训练、现有模型复用。
- `benchmark-comparison`：多模型 PDE / CFD / operator benchmark 对比。
- `inference`：推理、rollout、可视化和指标汇总。
- `end-to-end`：数据、模型、训练、推理和评估多阶段串联。

## `earth-observation`

常见信号：

- 遥感
- 卫星影像
- 栅格切片
- 多通道影像

重点约束：

- 投影与坐标系
- 分块策略
- 云掩码 / 质量控制
- 时序拼接

推荐交接重点：

- 数据组织方式
- patch / tile 策略
- 输入输出尺寸
- 标签来源

## `materials`

常见信号：

- 材料模拟
- 晶体结构
- 分子性质预测
- 第一性原理 / 计算化学
- MACE / UMA / 其它材料模型 / MLIP / U-MLIP
- extxyz / xyz / ASE / LAMMPS / DeepMD 数据
- OC20 / OMAT / OMOL
- 能量、力、应力、势函数、结构弛豫、MD

重点约束：

- 结构表示
- 图构建方式
- 物性标签
- 单位制与归一化
- 原子参考能、元素覆盖、DFT 设置一致性
- 周期边界、真空盒、charge/spin、下游物性验证

推荐交接重点：

- 样本表示
- 标签定义
- 训练目标
- 评估方式
- 模型路线：已登记材料模型路线；未登记时标记为 `unregistered_material_model`
- 数据格式与字段 key
- checkpoint / foundation model 来源
- 验证计划：RMSE 加下游材料性质

推荐 `domain_task_family`：

- `data-interface`：extxyz、ASE DB、LMDB、DeepMD、CIF 或轨迹数据接入。
- `model-development`：MACE / UMA / MLIP 训练、微调或模型路线适配。
- `inference`：结构弛豫、性质计算、calculator、MD 或批量推理。
- `evaluation`：RMSE、下游物性、OOD 构型、MD 稳定性或材料任务排查。
- `runtime`：本地、SLURM、多卡或远程提交意图。

## `biology`

常见信号：

- 蛋白
- 基因
- 生物序列
- 结构预测
- 生信
- 组学 / 单细胞 / 空间组学
- 变异检测 / 群体遗传
- 蛋白设计 / 药物设计
- 公共生物数据库 / 临床变异 / 实验室数据

重点约束：

- 序列长度
- 模态类型
- 标签稀疏性
- 数据拆分策略
- 物种、参考基因组、数据库版本
- 输入文件格式和 batch 协议
- 是否属于 OneScience 生信模型推理或模型改造

推荐交接重点：

- 序列或结构表示
- 标签任务
- 训练样本来源
- 指标口径
- `bio_task_family`
- OneScience 模型家族、entrypoint、checkpoint、输出校验
- 对传统生信流程、数据库和实验室任务，不要默认路由成 OneScience 模型改造

推荐 `domain_task_family`：

- `bio-inference`：执行已有 OneScience 生信模型推理、generation、sampling 或 scoring。
- `onescience-model-development`：OneScience 生信模型结构、训练、微调、batch 协议或 datapipe adapter 改造。
- `bio-workflow`：RNA-seq、single-cell、variant calling、multi-omics、protein design validation 等端到端分析链路。
- `data-foundation`：FASTQ、BAM/CRAM、VCF/BED、samplesheet、公共数据接入和底层格式处理。
- `analysis-tools`：Python/R/Bioconductor/Scanpy/RDKit/质谱/统计可视化等工具型任务。
- `knowledge-database`：文献、序列、变异、通路、结构、化合物和图谱数据库查询。
- `clinical-lab-quality`：临床方案、实验设计、仪器数据标准化、QC 报告和可复现交付。

## `general-science`

适用场景：

- 无法稳定识别具体领域
- 需求更偏工程实现而非领域语义

处理方式：

- 只保留通用工作流判断
- 不额外假设领域变量
- 交接给角色层继续判断

## 领域到交接摘要的最小字段

无论领域为何，建议在 `workflow_handoff` 中尽量补齐：

- `domain`
- `domain_route`
- `domain_task_family`
- `task_goal`
- `data_object`
- `key_constraints`
- `expected_deliverable`
- `remote_involved`

注意：

- `domain_profiles` 只做领域识别与粗任务族归类。
- 具体角色链、任务桶细化、coder assets、模型兼容性和交接模板由 `onescience-role` 继续完成。
