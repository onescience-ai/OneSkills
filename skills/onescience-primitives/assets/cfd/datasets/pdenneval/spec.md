## content_principle
PDENNEval 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/PDENNEval` 下的 PDEBench 风格数据和生成数据。该集合面向多类神经算子和 PDE benchmark。

## data_schema
`pdebench_data` 包含 `1D_Advection`、`1D_Burgers`、`1D_CFD`、`2D_CFD`、`2D_DarcyFlow`、`3D_CFD`、`ReacDiff`、`diff-sorp`、`rdb` 等 HDF5/H5 文件；`generated_data` 包含 Allen-Cahn、Euler、Maxwell、Black-Scholes-Barenblatt、Cahn-Hilliard 等 zip。

## directory_layout
```text
/PDENNEval
├── pdebench_data/*.hdf5
├── pdebench_data/*.h5
├── pdebench_data/download_pdebench_selected.sh
└── generated_data/*.zip
```

## storage_format
主格式为 HDF5/H5；生成数据仍为 zip，使用前需确认是否已解压。内部键可能是 `tensor`、`density/pressure/Vx/Vy/Vz` 或 seed group，需按文件抽检。

## scale_spec
不同 PDE 文件维度差异很大，规模由 batch 数、空间分辨率、时间步和变量通道共同决定。OneScience datapipe 支持 reduced batch/resolution/time。

## coverage_spec
覆盖一维、二维、三维 PDE/CFD 预测任务，可用于 FNO、DeepONet、MPNN、UNet、UNO、PINO 等模型族。

## label_spec
标签通常为完整未来轨迹或目标时间序列；PINO 还可使用 PDE residual 数据流。每个文件变量名和单位需独立确认。

## split_strategy
OneScience datapipe 可用 `test_ratio` 划分 train/val；没有统一 test loader。正式 benchmark 应固定文件、降采样参数、initial_step 和 split seed。

## constraints
不同模型族输出协议不同；HDF5 内部 schema 不统一；MPNN 多文件路径需复核；不要推断存在未实现的 datapipe 类。
