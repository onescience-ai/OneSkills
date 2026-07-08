# description
`uma_escn_md` 的规划决策知识用于指导 agent 在材料原子势任务中选择、配置和调用 UMA eSCNMD backbone。决策重点不是单独替换一个网络类，而是同时约束数据对象、checkpoint、dataset embedding、charge/spin、PBC、构图策略、head 类型、loss/normalizer 和资源开销，使 backbone 输出的等变节点表示能够稳定服务 energy-only、EF、EFS、relaxation、MD 或批量推理任务。

# when_to_use
- 任务目标是材料、分子、晶体、表面或吸附体系的通用 MLIP 表征。
- 已有或计划使用 UMA checkpoint，例如 `uma-s-1p1_converted.pt`。
- 输入可以整理为 `AtomicData` 风格字段，包括坐标、原子序数、batch、cell、charge、spin、dataset 和 PBC。
- 需要预测 energy、forces、stress，或要接入结构弛豫、MD、批量性质推理。
- 数据来自 OC20、OMAT、OMOL 或与其相近的多任务材料场景，并需要 charge/spin/dataset 条件信息。
- 需要一个共享 backbone 配合多个 task head，而不是为每个任务训练完全独立模型。

不优先使用：

- 输入不是原子结构，无法形成局部邻域图。
- 任务只需简单标量回归且不需要几何等变性或物理梯度一致性。
- 没有可靠 energy/forces/stress 标签，也无法校准单位、PBC 和数据集统计量。
- 目标是明确的 MoE 专家路由改造时，应优先评估 `eSCNMDMoeBackbone`。

# inputs
- 任务类型：`checkpoint_inference`、`finetune_energy`、`finetune_ef`、`finetune_efs`、`relax_or_md`、`batch_inference`、`molecule_charge_spin`、`crystal_or_adsorbate_pbc` 或 `moe_advanced`。
- 结构数据：ASE DB、LMDB、AtomicData、trajectory 或可转换为原子结构的数据文件。
- 核心字段：`pos`、`atomic_numbers`、`batch`、`natoms`、`cell`、`pbc`、`charge`、`spin`、`dataset`。
- 标签字段：energy、forces、stress 的字段名、单位、shape 和符号约定。
- checkpoint：转换后的 UMA checkpoint 路径，以及可选 starting checkpoint / finetune override。
- 数据统计：`elem_refs`、`normalizer_rmsd`，必须来自目标训练集或同源数据。
- 模型配置：`dataset_list`、`otf_graph`、`cutoff`、`max_neighbors`、`regress_stress`、`always_use_pbc`、`jd_path`。
- head/task 配置：energy-only、EF、EFS 的 head、loss、normalizer、metric。
- 资源约束：设备类型、显存、batch size、最大原子数、最大边数和训练/推理时限。

# outputs
- 原语选择结论：使用 `uma_escn_md` 的 `eSCNMDBackbone`，或转向 `eSCNMDMoeBackbone` / 其他 MLIP。
- 数据契约：必须存在的 AtomicData 字段、PBC 策略、charge/spin 默认值、dataset 映射和标签字段。
- 模型装配：backbone 参数、head 类型、是否冻结 backbone、是否从 checkpoint 微调。
- 训练/推理配置：checkpoint、dataset、elem_refs、normalizer、loss、metric、batch size、学习率和评估间隔。
- 运行命令：Hydra override 或 demo YAML 启动命令。
- 验证计划：小 batch forward、loss 检查、E/F/S shape 检查、PBC/构图检查、下游 MD/relaxation smoke test。
- 风险清单：Jd 路径缺失、dataset_list 为空、PBC 混合、无边图、统计量不同源、checkpoint 不兼容、显存不足。

# procedure
1. 判断任务是否是原子尺度材料势函数问题；若不是局部几何图任务，停止选择该原语。
2. 明确输出目标：
   - energy-only：backbone + `MLP_Energy_Head`。
   - energy-force：backbone + `MLP_EFS_Head`，保持 `regress_stress=false`。
   - energy-force-stress：backbone + `MLP_EFS_Head`，设置 `regress_stress=true` 并配置 stress task。
3. 确认 checkpoint 路径；OneScience 微调优先使用转换后的 `uma-s-1p1_converted.pt`。
4. 检查 `Jd.pt` 是否可解析；推荐显式设置 `jd_path`，避免环境变量差异造成初始化失败。
5. 梳理数据字段：确认 `pos`、`atomic_numbers`、`batch`、`natoms`、`cell`、`charge`、`spin`、`dataset` 和 `pbc`。
6. 制定 PBC 策略：
   - 晶体、表面、吸附：通常允许 PBC。
   - 分子：通常设置 `always_use_pbc=false`，并提供 `pbc=false` 与足够大 cell。
   - 混合 PBC batch：先拆分 batch，避免当前实现的全 true/全 false 限制。
7. 选择构图方式：
   - 常规训练/推理：`otf_graph=true`。
   - 数据已预计算邻接：`otf_graph=false`，必须提供 `edge_index`、`cell_offsets`、`nedges`。
8. 固定 baseline 超参：`cutoff=5.0`、`max_neighbors=300`、`sphere_channels=128`、`lmax=2`、`mmax=2`、`num_layers=2`。
9. 绑定数据集统计：从目标数据生成或读取 `elem_refs` 和 `normalizer_rmsd`，并保证与 `dataset_name`、head 和 tasks 同源。
10. 生成 Hydra override 或 YAML；包含 checkpoint、backbone、head、data、loss、optim 和 trainer 参数。
11. 先执行 dry-run 或小 batch smoke test，检查构图是否有边、输出 dict 结构是否符合 head 预期、loss 是否能计算。
12. 正式训练或推理后，按任务检查 energy MAE、force MAE、stress MAE、结构弛豫收敛、MD 稳定性和异常近邻样本。

# constraints
- 不要在未确认 checkpoint 结构的情况下随意改变 `sphere_channels`、`lmax`、`mmax`、`num_layers` 等权重形状相关参数。
- `dataset_list` 必须非空，且输入 `dataset` 必须被覆盖。
- `elem_refs`、`normalizer_rmsd`、`dataset_name`、`heads` 和 `tasks_list` 必须同源。
- EF 任务不得误开 `regress_stress=true`；EFS 任务必须同时具备 stress 标签、stress loss 和 stress-compatible 输出。
- 分子 charge/spin 任务必须显式提供 charge/spin 或定义清晰的数据默认策略。
- 同一 batch 不混合全周期与非周期 PBC。
- `always_use_pbc=true` 用于非周期分子时必须保证真空盒足够大。
- `otf_graph=false` 时不得省略预计算图字段。
- 资源评估应按边数而不是只按原子数估算。

# next_phase_recommendation
- 为目标数据集补充数据卡，记录字段名、单位、PBC、charge/spin、dataset 名称、elem_refs、normalizer_rmsd 和 train/val/test 划分。
- 建立最小 UMA 配置模板，分别覆盖 energy-only、EF、EFS 和 inference 四类任务。
- 对新材料体系先冻结或小学习率微调 backbone，确认 head 和数据统计无误后再扩大训练规模。
- 对分子和晶体混合任务建立 batch 分流策略，避免 PBC 限制在运行时触发。
- 对部署到 MD/relaxation 的模型，增加短轨迹稳定性、异常力、能量漂移和结构弛豫收敛检查。
- 若多数据域性能冲突明显，再评估 `uma_escn_moe` 或 dataset-specific head，而不是先改基础 backbone。

# fallback
- checkpoint 加载失败：确认是否为转换后 UMA checkpoint，检查权重结构参数和 `HydraModel` 装配配置。
- `Jd.pt` 缺失：显式设置 `jd_path` 或配置 `ONESCIENCE_UMA_JD_PATH`，再重新初始化模型。
- `dataset_list` 为空：从数据配置或 checkpoint 元信息补齐 dataset 列表，不要用空字符串占位。
- 构图后无边：检查 cutoff、cell、PBC、坐标单位和单原子样本；必要时过滤单原子或增大 cutoff。
- PBC 断言失败：按 PBC 类型拆分 batch，或在 datapipe 层统一周期条件。
- 显存不足：优先降低 batch size 和 max_neighbors，开启 activation checkpointing；仍不足时再评估缩小通道或层数。
- EFS loss 异常：核对 stress shape、符号、单位、`regress_stress` 和 head/task 配置是否一致。
- 分子 charge/spin 输出异常：检查 `r_data_keys`、charge/spin 默认值、真空盒和 `always_use_pbc`。
- 下游 MD 不稳定：增加异常近邻和高能构型验证，重新平衡 force/stress loss，并筛选更稳定 checkpoint。
