# Datapipe Card: Materials UMA

## 基本信息

- Datapipe 名：`UMA ase_db / custom_stack pipeline`
- 领域：`materials / universal MLIP`
- 典型任务：UMA fine-tuning、Hydra 训练、ASE DB/LMDB 数据接入、异构原子体系推理
- 主要源码：`./onescience/src/onescience/datapipes/materials/custom_stack/`

## 数据定位

UMA 训练入口使用 `custom_stack` 数据对象和 Hydra 配置。OneScience demo 默认以 `ase_db` 格式组织 train/val 数据，再通过 `create_concat_dataset` 和 `get_dataloader` 构造多任务 dataloader。

首选路径：

1. 准备 ASE DB/LMDB 或由脚本转换生成
2. 填写 `data.dataset_name`
3. 填写 `elem_refs` 和 `normalizer_rmsd`
4. 配置 transforms、heads、tasks_list
5. 通过 demo `run.sh` 生成 Hydra config 并启动训练

## 输入文件约定

### ASE DB / LMDB

训练数据目录通常包含：

- `train/`
- `val/`

Hydra 中写为：

```yaml
data:
  train_dataset:
    splits:
      train:
        src: <train_dir>
    format: ase_db
  val_dataset:
    splits:
      val:
        src: <val_dir>
    format: ase_db
```

### 必填统计量

- `dataset_name`: 例如 `oc20`、`omat`、`omol`
- `elem_refs`: 每元素参考能量列表
- `normalizer_rmsd`: 归一化常数

这些值应来自数据准备脚本或同一训练集统计，不要跨数据集硬复制。

## 样本返回协议

`custom_stack.core.atomic_data.AtomicData` 核心字段：

- `pos`: `(NumAtoms, 3)`
- `atomic_numbers`: `(NumAtoms,)`
- `cell`: `(NumGraphs, 3, 3)`
- `pbc`: `(NumGraphs, 3)`
- `natoms`: `(NumGraphs,)`
- `edge_index`: `(2, NumEdges)`
- `cell_offsets`: `(NumEdges, 3)`
- `nedges`: `(NumGraphs,)`
- `charge`: `(NumGraphs,)`
- `spin`: `(NumGraphs,)`
- `fixed`: `(NumAtoms,)`
- `tags`: `(NumAtoms,)`
- `batch`: `(NumAtoms,)`
- 可选 `energy` / `forces` / `stress` / `dataset`

UMA backbone 开启 `otf_graph=True` 时会重建图，但数据对象仍需要保留 cell/pbc/natoms/charge/spin 等基础字段。

## transforms

常见 transforms：

- `common_transform`
  - 设置 `dataset`
  - 补默认 `charge=0`、`spin=0`
  - 确保 energy 为 tensor
- `stress_reshape_transform`
  - 将 stress reshape 到 `(1, 9)`
- `omol_transform`
  - 分子任务需要 charge/spin
  - 对分子构建大真空盒
- `asedb_transform`
  - 设置 dataset 和 sid

## 训练配置桥接

demo YAML 中最常改：

- `data.dataset_name`
- `data.elem_refs`
- `data.normalizer_rmsd`
- `data.train_dataset.splits.train.src`
- `data.val_dataset.splits.val.src`
- `data.regress_stress`
- `data.heads`
- `data.tasks_list`
- `runner.train_eval_unit.model.checkpoint_location`
- `runner.train_eval_unit.model.overrides.backbone.max_neighbors`
- `runner.train_eval_unit.model.overrides.backbone.always_use_pbc`

## 推荐数据策略

- OC20/吸附/表面：保持 adsorbate/slab tags、fixed atoms、pbc、cell 语义
- OMOL/分子：必须确认 charge/spin，非周期体系使用足够大真空盒
- OMat/晶体：保留周期 cell 与 stress 语义
- E-only：使用 energy head 和 per-atom energy metric
- EF/EFS：使用 EFS head，force loss 建议使用 L2NormLoss，stress 需 reshape 与 normalizer

## 风险点

- `pbc` 在当前 graph generation 中要求一个 batch 内全 true 或全 false；混合周期体系要拆分或单独适配。
- 分子任务没有 charge/spin 时，`omol_transform` 会直接报错。
- `elem_refs` 长度和元素索引必须与 UMA 期望一致。
- `normalizer_rmsd` 影响 loss 尺度；错误值会让 loss 和 metric 失真。
- `format: ase_db` 要求数据目录可被 ASE DB loader 识别；普通 extxyz 不能直接冒充。

## 源码锚点

- `./onescience/src/onescience/datapipes/materials/custom_stack/core/atomic_data.py`
- `./onescience/src/onescience/datapipes/materials/custom_stack/storage/ase_datasets.py`
- `./onescience/src/onescience/datapipes/materials/custom_stack/storage/mt_concat_dataset.py`
- `./onescience/src/onescience/datapipes/materials/custom_stack/collaters/mt_collater.py`
- `./onescience/src/onescience/datapipes/materials/uma/dataloader_builder.py`
- `./onescience/src/onescience/datapipes/materials/uma_transforms.py`
- `./onescience/examples/matchem/uma/configs/uma_sm_finetune_template.yaml`
- `./onescience/examples/matchem/uma/demo/configs/*.yaml`
