## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/matchem/matris`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/matris`。入口文件为 `pbe_phonon_ref.csv` 和 `pbesol_phonon_ref.csv`。

## data_schema
CSV 以 `mp_id` 为主键，包含 `nsites`、`energy_pa`、`volume_pa`、`entropy`、`heat_capacity`、`free_energy`、`max_freq`、`avg_freq`、`stable`。这是材料级性质表，不含原子坐标和原子力。

## task_usage
适用于 MatRIS 性质预测、声子统计回归、热力学标量回归、稳定性分类和 PBE/PBEsol 泛函口径比较。

## integration_paths
以 pandas/CSV reader 读取表格，构造 `mp_id` 索引和目标列 mask。若模型需要结构输入，应通过 `mp_id` 关联外部结构数据库；若只做表格 baseline，可直接使用数值列和派生特征。

## preparation_requirements
需要统计缺失值、重复 `mp_id`、PBE/PBEsol 共有材料、目标分布和 `stable` 正负比例。多任务训练时每个目标列应有独立 mask，避免空值参与 loss。

## consumption_interfaces
可供 MatRIS 评测脚本、性质回归 datapipe 或表格 baseline 消费。典型 batch 包含 `mp_id`、输入特征、目标字典、mask 字典和可选结构引用。

## evaluation_protocol
回归目标报告 MAE/RMSE/R2，稳定性标签报告 accuracy、AUC 或 F1。PBE 与 PBEsol 不同口径需分表评测；共有 `mp_id` 可做 paired error 分析。

## resource_profile
CSV 体量通常较轻，可一次性读入内存；关键资源消耗来自外部结构关联、图构建或预训练表示提取。

## operation_limits
- 不要把该 CSV 表传给原子势模型当作结构轨迹。
- `energy_pa` 和 `volume_pa` 是每原子性质。
- PBE/PBEsol 混合训练必须记录泛函口径字段。
- 缺失值不能用 0 静默填充参与监督。
