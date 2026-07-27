## description
为 MatRIS CSV 性质表选择读取、目标构造、划分和评测路线的规划知识。

## when_to_use
当任务需要使用 `matchem/matris` 的 PBE/PBEsol 声子参考表进行 MatRIS 性质预测、热力学回归或稳定性分类时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/matchem/matris`。任务输入规范：以 `mp_id` 为主键的 CSV 性质表。

## outputs
输出为表格 datapipe、目标列配置、缺失值 mask、材料级 split、评测指标和可选结构关联索引。

## procedure
1. 读取 `pbe_phonon_ref.csv` 和/或 `pbesol_phonon_ref.csv`。
2. 校验列名、dtype、缺失值、重复 `mp_id` 和稳定性标签比例。
3. 根据任务选择目标列和 loss 类型：回归或分类。
4. 若模型需要结构输入，通过 `mp_id` 关联结构数据；否则构建表格 baseline。
5. 按 `mp_id` 建立训练/验证/测试划分。
6. 为每个目标生成 mask，避免缺失值参与监督。
7. 分泛函口径输出 MAE/RMSE/R2 或分类指标。

## constraints
该数据不是原子结构轨迹，不能直接用于 energy/force 势模型训练；PBE 与 PBEsol 口径不能无标识混合；每原子性质不能当作结构总量。

## next_phase_recommendation
若结构关联已准备好，进入 MatRIS 图模型训练；若没有结构数据，先做 CSV 性质表评测或构造外部结构索引。

## fallback
若某列缺失严重，降级为可用目标多任务训练；若无法关联结构，仅支持表格/embedding 级任务。
