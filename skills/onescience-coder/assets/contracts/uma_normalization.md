# Contract: UMA Normalization and References

## 基本信息

- 组件名：`UMA Normalization and Element References`
- 所属模块族：`materials / uma / normalization`
- 统一入口：`Normalizer / ElementReferences`
- 注册名：`not_applicable`
- 主源码：
  - `./onescience/src/onescience/utils/uma/normalization/normalizer.py`
  - `./onescience/src/onescience/utils/uma/normalization/element_references.py`

## 组件职责

管理 UMA 多任务训练中的能量参考、normalizer、RMSD 标度和 task 输出反归一化。

## 输入契约

- `elem_refs`: 按元素索引排列的参考能列表
- `normalizer_rmsd`
- task `mean` / `rmsd`
- dataset name
- train/val ASE DB 或 LMDB 数据统计

## 输出契约

- `ElementReferences`
- `Normalizer`
- 训练 loss 使用的标准化 target
- 推理时恢复物理尺度的输出

## 关键参数

- `mean`
- `rmsd`
- `element_references`
- `dataset_name`
- `fit_references`
- `fit_normalizers`

## 典型调用位置

- UMA Hydra `tasks_list`
- `create_uma_finetune_dataset.py`
- `fit_references.py`
- `fit_normalizers.py`
- `MLIPTrainEvalUnit.compute_loss`

## 常见修改点

- 新数据集：必须重新生成 `elem_refs` 和 `normalizer_rmsd`。
- 多任务：每个 task 的 normalizer 和 reference 要单独确认。
- 切换 `dataset_name`：同步 transforms、task datasets 和 checkpoint 预训练任务。

## 风险点

- `elem_refs` 长度或元素索引错位会造成系统性能量偏移。
- 复用旧 normalizer 到新数据集会导致 loss 尺度错误。
- energy 和 forces 共用同一个 rmsd 时必须确认配置语义。
- 推理侧 normalizer 与训练侧不一致会导致物理量数值错误。

## 源码锚点

- `./onescience/src/onescience/utils/uma/normalization/normalizer.py`
- `./onescience/src/onescience/utils/uma/normalization/element_references.py`
- `./onescience/src/onescience/utils/uma/scripts/fit_references.py`
- `./onescience/src/onescience/utils/uma/scripts/fit_normalizers.py`

## 下钻关系

- training unit：`./uma_mlip_unit.md`
- loss：`./uma_loss.md`
- data：`../datapipes/materials_uma.md`
- calculator：`./uma_calculator.md`
