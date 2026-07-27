## content_principle
CFD_Benchmark 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/CFD_Benchmark` 下的多任务 CFD/PDE benchmark。它覆盖规则网格流场、神经算子基准和若干 PDE 场预测任务。

## data_schema
主要子集包括：`airfoil` 的 `NACA_Cylinder_Q/X/Y.npy`，`pipe` 的 `Pipe_Q/X/Y.npy`，`ns` 的 Navier-Stokes MAT，`darcy` 的 Darcy MAT，`diffusion_sorption` 的 H5，`elasticity` 的 mesh NumPy，`plas` 的 MAT，以及 `car` 的预处理压缩包。

## directory_layout
```text
/CFD_Benchmark
├── airfoil/{NACA_Cylinder_Q.npy,NACA_Cylinder_X.npy,NACA_Cylinder_Y.npy}
├── pipe/{Pipe_Q.npy,Pipe_X.npy,Pipe_Y.npy}
├── ns/NavierStokes_V1e-5_N1200_T20.mat
├── darcy/piececonst_r421_N1024_smooth{1,2}.mat
├── diffusion_sorption/1D_diff-sorp_NA_NA.h5
├── elasticity/Meshes/Random_UnitCell_*.npy
├── plas/plas_N987_T20.mat
└── car/mlcfd_data/preprocessed_data.tar.gz
```

## storage_format
混合 `.npy`、`.mat`、`.h5` 和压缩包。已探测：`airfoil/NACA_Cylinder_Q.npy=(2490,5,221,51)`，`airfoil/X/Y=(2490,221,51)`；`pipe/Pipe_Q.npy=(2310,3,129,129)`。

## scale_spec
不同子集分辨率、通道数和时间维不同；样本规模需要按子集单独统计。MAT/H5 的内部键需在任务环境中用 scipy/h5py 或兼容 reader 抽检。

## coverage_spec
覆盖翼型/圆柱、管道流、Navier-Stokes、Darcy、扩散-吸附、弹性和等离子体等任务，适合 FNO、DeepONet、CNO、PINO 等神经算子评测。

## label_spec
标签随子集变化：`Q` 通常为多通道物理场，`X/Y` 为坐标；MAT/H5 目标需按内部键确认。不能在跨子集训练中假设统一通道语义。

## split_strategy
若子集没有显式 split，应按样本索引固定划分；时间序列任务需保持时间因果，不能随机打散相邻时间步。

## constraints
多任务格式不统一；MAT/H5 需要依赖 reader；不同子集的单位、网格和通道含义必须单独记录；不要把 `car` 压缩包当作已解压样本目录。
