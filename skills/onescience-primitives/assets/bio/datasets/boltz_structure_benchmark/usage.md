## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/Boltz_dataset/boltz_results_final`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/Boltz_dataset/boltz_results_final`。



已绑定的资源入口：

- `Boltz_dataset/boltz_results_final/targets`
- `Boltz_dataset/boltz_results_final/inputs`
- `Boltz_dataset/boltz_results_final/outputs`
- `Boltz_dataset/boltz_results_final/results_test.csv`
- `Boltz_dataset/boltz_results_final/results_casp.csv`
- `Boltz_dataset/boltz_results_final/physical_checks_test.csv`

## data_schema

评测单位为 tool × target × model/排名，参考结构与预测分开。results CSV 表头为 `tool,target,metric,oracle,average,top1`；physical_checks 包括 `tool,pdb_id,model_idx`、ligand/bond/angle/clash/chirality 等计数和 `clash_free,valid_ligand,valid`。targets/test 多为 `.cif.gz`，CASP15 为 `.cif`；工具预测目录格式须各自解析。

## task_usage

用于冻结预测的结构对齐、精度指标和物理检查结果复核；需要重跑预测时从 inputs 选择对应工具输入，保留 seed/model rank。

## integration_paths

target 清单 → 工具预测/参考配对 → chain/assembly 映射 → 匹配评测工具 → oracle/average/top1 与物理质量分别汇总。

## preparation_requirements

核实每个 target 的参考和候选、压缩格式、tool 命名、model_idx、链/配体映射；明确指标版本、排序与失败分母。

## consumption_interfaces

tool、target、reference_path、prediction_path、model_idx/rank，及独立标记的已有/新算指标；参考与预测角色必须显式。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

不能将 outputs 或来源结果 CSV 当真值用于训练。gzip、链名、assembly、残基映射和缺失原子处理须一致；历史结果与本地重算结果分开标记。
