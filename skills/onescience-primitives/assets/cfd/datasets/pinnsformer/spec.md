## content_principle
PINNsFormer 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/pinnsformer` 下的示例 PDE MAT 数据。该集合主要用于物理约束 Transformer/PINN 训练和复现实验。

## data_schema
当前包含 `convection.mat` 与 `cylinder_nektar_wake.mat`。前者面向对流方程，后者面向圆柱尾迹/涡街数据。MAT 内部变量需用 scipy.io 或兼容 reader 抽检。

## directory_layout
```text
/pinnsformer
├── convection.mat
└── cylinder_nektar_wake.mat
```

## storage_format
MATLAB `.mat`。默认环境可能没有 scipy，任务环境需准备 MAT reader 或转换为 HDF5/NumPy。

## scale_spec
规模由 MAT 内部变量 shape 决定；训练前要记录空间点、时间点、变量通道和样本数。

## coverage_spec
覆盖对流方程和圆柱尾迹示例，适合 PINNsFormer、PINN、时空 Transformer 和物理残差监督实验。

## label_spec
标签通常是 PDE 解场或尾迹速度/压力序列；物理残差项需要由方程和坐标网格计算。

## split_strategy
按时间区间、空间采样点或样本索引划分，具体取决于 MAT 内部组织。时序预测不能随机打散时间点。

## constraints
不要在未探测 MAT 键前硬编码字段；物理残差和数据监督的采样点需分开记录；圆柱尾迹和对流方程不是同一任务。
