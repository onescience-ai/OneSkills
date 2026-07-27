## content_principle
CFDBench 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/CFDBench` 下的二维规则网格 CFD case 数据。它面向参数化边界、几何、物性条件下的速度场预测。

## data_schema
每个 case 目录包含 `case.json`、`u.npy`、`v.npy`。`case.json` 存储边界条件、几何或物性参数；`u.npy/v.npy` 存储速度分量时间序列。已探测 `cavity/bc/case0000/u.npy=(10,64,64)`，`v.npy=(10,64,64)`，`case.json` 含 `height,width,vel_top,density,viscosity,rotated`。

## directory_layout
```text
/CFDBench
├── cavity/{bc,geo,prop}/case*/{case.json,u.npy,v.npy}
├── cylinder/{bc,geo,prop}/case*/{case.json,u.npy,v.npy}
├── dam/{bc,geo,prop}/case*/{case.json,u.npy,v.npy}
└── tube/{bc,geo,prop}/case*/{case.json,u.npy,v.npy}
```

## storage_format
参数为 JSON，速度场为 NumPy `.npy`。OneScience `cfdbench` datapipe 将 `u/v` 和 mask 组合为输入/标签，并支持静态帧预测和自回归一步预测。

## scale_spec
问题类型为 `tube/cavity/cylinder/dam`，子集为 `bc/geo/prop`。每个 case 的时间步数和网格大小需按 `u/v` 实际 shape 统计。

## coverage_spec
覆盖二维规则网格内流、绕流、溃坝等场景，适合条件化 CFD surrogate、auto-regressive rollout 和参数泛化。

## label_spec
标签为 `u`、`v` 速度分量；压力当前不在 OneScience CFDBench datapipe 读取范围内。mask 由问题几何派生。

## split_strategy
OneScience datapipe 按随机种子打乱 case 后用 `split_ratios` 划分 train/val/test；若要复现实验，必须固定 seed 和 data_name。

## constraints
只支持四类 problem；`data_name` 需要能解析出 problem 和 subset；静态模式和 `task_type=auto` 的 batch 协议不同。
