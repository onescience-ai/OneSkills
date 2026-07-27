## content_principle
Eagle 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/Eagle` 下的变长网格 CFD 时序数据，支持窗口化网格预测和聚类辅助建模。

## data_schema
单个仿真目录含 `sim.npz`、`triangles.npy` 和可选 `constrained_kmeans_{10,20,30,40}.npy`。已探测 `sim.npz` 键为 `pointcloud, mask, VX, VY, PS, PG`，样例 shape：`pointcloud=(990,3434,2)`、`VX/VY/PS/PG=(990,3434)`、`triangles=(990,6703,3)`。

## directory_layout
```text
/Eagle
└── Eagle_dataset
    └── Cre/<case_group>/<case_id>/
        ├── sim.npz
        ├── triangles.npy
        └── constrained_kmeans_{10,20,30,40}.npy
```

## storage_format
主格式为 NumPy `.npz/.npy`。三角面可转为图边；速度为 `VX/VY`，压力相关通道为 `PS/PG`，mask 描述节点类型或有效区域。

## scale_spec
每个 case 是长时间序列，样例含 990 个时间步、3434 个点和 6703 个三角单元。实际节点数和单元数需逐 case 统计。

## coverage_spec
覆盖二维非结构网格 CFD 时序，适用于 Eagle 模型、变长 mesh sequence、cluster-aware prediction 和图神经算子。

## label_spec
标签通常为未来窗口的 velocity 和 pressure 序列；datapipe 不直接决定输入/目标步切分，训练脚本需要定义窗口预测协议。

## split_strategy
OneScience Eagle datapipe 依赖 `splits_dir/train.txt/valid.txt/test.txt`；当前数据目录本身主要是仿真数据，若没有 split 文件需先生成稳定 split。

## constraints
`valid.txt` 文件名不能写成 `val.txt`；`n_cluster` 只能取实现支持值；坏样本可能被 collate 过滤导致空 batch。
