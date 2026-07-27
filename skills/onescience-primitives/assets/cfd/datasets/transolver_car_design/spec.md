## content_principle
Transolver-Car-Design 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/Transolver-Car-Design` 下的三维汽车外流场图数据。它与 OneScience ShapeNetCar datapipe 对齐。

## data_schema
主要入口为 `mlcfd_data/preprocessed_data/param0..param8/<sample>/`，每个样本含 `x.npy`、`y.npy`、`pos.npy`、`surf.npy`、`edge_index.npy`。已探测样例：`x=(32186,7)`、`y=(32186,4)`、`pos=(32186,3)`、`surf=(32186,)`、`edge_index=(2,766506)`。

## directory_layout
```text
/Transolver-Car-Design
└── mlcfd_data
    ├── preprocessed_data/param0..param8/<sample>/{x,y,pos,surf,edge_index}.npy
    ├── preprocessed_data.tar.gz
    ├── linear_regression_code/*.npy
    ├── graph_raw_data/*.xlsx
    └── side_by_side_comparisons/*.png
```

## storage_format
主训练入口为预处理 NumPy 图缓存；压缩包、xlsx、png 和线性回归辅助文件不是主监督样本。`param0..param8` 对应 fold 分组。

## scale_spec
当前有 9 个 param fold；`param0` 探测到 100 个样本目录。每个样本节点数、边数可能不同，需逐样本统计。

## coverage_spec
覆盖三维汽车外流场表面/体点拼接数据，适用于 Transolver-Car、PyG 图模型、压力/速度联合预测和 fold 泛化验证。

## label_spec
`y` 通常为 `[v_x,v_y,v_z,p]`，`x` 通常为 `[pos_x,pos_y,pos_z,sdf,normal_x,normal_y,normal_z]`，`surf` 表示表面点。

## split_strategy
按 `param0..param8` 做 fold 划分，`fold_id` 指定验证 fold，其余为训练。不要随机跨 fold 混合后报告 fold 指标。

## constraints
需要保持 `surf` 和压力通道；图边可能很大，显存需先 smoke test；辅助可视化文件不参与训练。
