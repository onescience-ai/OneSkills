## content_principle
BENO 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/BENO` 下的边界条件神经算子数据。数据由右端项、解场和边界条件三组数组组成，适合构造成异构图或规则网格 PDE 样本。

## data_schema
样本按边界类型和前缀组织：`Dirichlet`、`Neumann` 下均有 `RHS_N32_<prefix>_all.npy`、`SOL_N32_<prefix>_all.npy`、`BC_N32_<prefix>_all.npy`，前缀包括 `0c`、`1c`、`2c`、`3c`、`4c`、`mix`。已探测样例：`RHS_N32_0c_all.npy=(1000,1024,4)`，`SOL_N32_0c_all.npy=(1000,1024,1)`，`BC_N32_0c_all.npy=(1000,128,4)`，dtype 为 `float64`。

## directory_layout
```text
/BENO
├── data/Dirichlet/{RHS,SOL,BC}_N32_{0c,1c,2c,3c,4c,mix}_all.npy
├── data/Neumann/{RHS,SOL,BC}_N32_{0c,1c,2c,3c,4c,mix}_all.npy
└── __MACOSX/
```

## storage_format
主格式为 NumPy `.npy`。`RHS` 通常含二维坐标、输入场和 cell state，`SOL` 是标量解场，`BC` 是边界点条件。`__MACOSX` 是归档残留目录，不作为数据入口。

## scale_spec
每个边界类型和前缀组合当前样例为 1000 个样本，空间底网格为 `32 x 32 = 1024`，边界点数为 128。

## coverage_spec
覆盖 Dirichlet 与 Neumann 边界条件下的二维椭圆/边界算子学习任务，可用于 BENO 异构图、神经算子和边界条件泛化评测。

## label_spec
监督目标为 `SOL` 标量场。训练时可用 `RHS` 和 `BC` 作为输入，`BC` 边界值和 `SOL` 解场归一化应保持同一数据 split 口径。

## split_strategy
OneScience BENO datapipe 默认按前 `ntrain` 个样本训练、后续 `ntest` 个样本测试，没有独立验证集。若需要验证集，应在样本索引层显式切分并记录前缀和边界类型。

## constraints
边界点数 128 和底网格 `resolution x resolution` 是当前实现的重要假设；不同边界类型不要无标识混合；缓存目录应写到任务输出目录，不写回共享数据路径。
