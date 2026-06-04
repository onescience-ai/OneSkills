# UMA Role Decomposition

## 角色定位

UMA 路线适合处理多任务通用原子势、催化/吸附/分子/晶体混合场景，以及基于 UMA checkpoint 的推理、微调和下游模拟。角色层要特别关注 task 名称、数据归一化、charge/spin、PBC 与 checkpoint 转换。

本文件是已登记材料模型路线之一。新增模型时不要把角色层逻辑写死到 UMA，而应在 `matchem_task_index.md` 中新增路线，并按 MACE 样板补齐该模型自己的 role/model/datapipe/contract 卡。

## 何时选择 UMA

优先选择 UMA，当用户目标包含：

- UMA / uma-s / `uma-s-1p1` checkpoint
- OC20、OMAT、OMOL、吸附、催化、分子/表面/晶体混合推理
- Hydra 配置、`ase_db`、`elem_refs`、`normalizer_rmsd`
- `load_predict_unit`、`FAIRChemCalculator`、异构 batch、relax 或 MD 推理
- 需要 dataset embedding、charge/spin embedding 或多任务 heads

## 拆解顺序

### 1. 科学目标

先明确目标是否只是推理，还是要微调：

- 推理：能量/力/应力预测、弛豫、MD、spin gap、异构 batch
- 微调：在 OC20/OMAT/OMOL 风格数据上适配 E、EF、EFS
- 模型改造：换 head、改 stress/force 预测、调整 OTF graph 或 MoE

### 2. 数据语义

UMA 交接必须写清：

- `dataset_name`: 通常要与 foundation task 一致，如 `oc20`、`omat`、`omol`
- `elem_refs`: 每元素参考能量列表，由数据准备脚本或统计过程生成
- `normalizer_rmsd`: 能量/力归一化常数
- `train/val src`: ASE DB/LMDB 目录
- `charge` / `spin`: 分子任务尤其重要
- `pbc` 和真空盒：分子/非周期结构需要大盒子，晶体/表面要保留周期性

### 3. 模型策略

默认复用 UMA checkpoint + HydraModel：

- Backbone：`eSCNMDBackbone` 或 `eSCNMDMoeBackbone`
- Head：`MLP_Energy_Head`、`MLP_EFS_Head`、`MLP_Stress_Head` 等
- 图构建：优先用 `otf_graph=True`，由模型按 cutoff/max_neighbors 构图
- 微调：优先从转换后的 checkpoint 开始，不直接用未转换权重

### 4. 训练与运行

交给 coder 时指向：

- 模型卡：`onescience-coder/assets/models/uma.md`
- 数据卡：`onescience-coder/assets/datapipes/materials_uma.md`
- 组件契约：`onescience-coder/assets/contracts/uma_material_stack.md`

优先复用 OneScience 示例：

- `./onescience/examples/matchem/uma/demo/run.sh`
- `./onescience/examples/matchem/uma/demo/configs/oc20_ef_*.yaml`
- `./onescience/examples/matchem/uma/configs/uma_sm_finetune_template.yaml`
- `./onescience/examples/matchem/uma/scripts/convert_model.py`
- `./onescience/examples/matchem/uma/scripts/create_uma_finetune_dataset.py`
- `./onescience/examples/matchem/uma/inference/*.py`

### 5. 验证

验证应覆盖：

- 训练/验证 metric：energy per-atom MAE、forces MAE/cosine/magnitude error、stress MAE
- 推理 sanity check：单结构能量、力维度、无 NaN、邻居数合理
- 结构任务：弛豫是否收敛、吸附结构是否物理、MD 是否稳定
- 多任务/异构 batch：不同 dataset/task 的 head 输出是否对应正确

## 默认交接模板

```yaml
model_route: uma
task_stage: finetune_or_inference
system_class: molecule_slab_bulk_adsorbate
structure_format: ase_db
target_properties: [energy, forces]
data_keys:
  dataset_name: oc20
  charge_spin_required: true_or_false
  elem_refs: provided_or_missing
  normalizer_rmsd: provided_or_missing
reference_model_or_checkpoint: uma-s-1p1_converted.pt
data_strategy: create_uma_finetune_dataset_or_existing_ase_db
validation_plan: task_metrics_plus_relax_or_md
runtime_intent: dry-run_or_slurm_or_local
```

## 角色层风险

- `Jd.pt` 和转换后的 checkpoint 是 UMA 常见前置依赖；缺失时不应假装训练可直接启动。
- `dataset_name`、元素参考能和 normalizer 不匹配会让微调指标失真。
- 分子任务若缺 charge/spin，要先在数据准备层补齐或明确默认值。
- `always_use_pbc` 与非周期结构的大真空盒必须配套考虑。
