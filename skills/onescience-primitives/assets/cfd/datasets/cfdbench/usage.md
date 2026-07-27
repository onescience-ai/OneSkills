## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/CFDBench`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/CFDBench`。入口按 `problem/subset/case*` 选择。

## data_schema
每个 case 读取 `case.json`、`u.npy`、`v.npy`。`u/v` 为时间序列速度场，`case.json` 为条件参数。

## task_usage
适用于二维规则网格 CFD 静态场预测、自回归一步预测、条件参数泛化和 CFDBench benchmark。

## integration_paths
优先使用 `cfd/datapipes/cfdbench`；配置 `source.data_name` 指定如 `cavity_bc`、`tube_prop`；datapipe 生成 `case_params`、`inputs/label/mask`。

## preparation_requirements
确认 problem 属于 `tube/cavity/cylinder/dam`，subset 属于 `bc/geo/prop`；抽检 `u/v` shape 一致；固定 seed 和 split ratios。

## consumption_interfaces
静态任务输出 `case_params,t,label`；自回归任务输出 `inputs,case_params,label,mask`。

## evaluation_protocol
报告 u/v RMSE、相对 L2、mask 内误差和多步 rollout 误差；按 problem/subset 分组。

## operation_limits
当前 datapipe 不读取压力；`task_type=auto` 与静态 batch 不兼容；delta time 转步数时可能有近似。
