## content_principle
Transolver-Airfoil-Design 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/Transolver-Airfoil-Design` 下的二维翼型非结构网格 VTK 数据。它与 OneScience AirfRANS datapipe 对齐。

## data_schema
`Dataset/manifest.json` 包含 split 键：`full_train=800`、`scarce_train=200`、`reynolds_train=504`、`aoa_train=804`、`full_test=200`、`reynolds_test=496`、`aoa_test=196`。每个样本目录含 `<name>_internal.vtu`、`<name>_aerofoil.vtp`、`<name>_freestream.vtp`。

## directory_layout
```text
/Transolver-Airfoil-Design
└── Dataset
    ├── manifest.json
    └── airFoil2D_SST_.../
        ├── *_internal.vtu
        ├── *_aerofoil.vtp
        └── *_freestream.vtp
```

## storage_format
VTK XML：内部流场为 `.vtu`，翼型表面和远场为 `.vtp`，split 为 JSON。AirfRANS datapipe 读取 `U,p,nut,implicit_distance,Normals` 等字段并转换为 PyG Data。

## scale_spec
manifest 中 full split 为 800 train / 200 test，其它 split 用于 scarce、Reynolds 外推和 AoA 外推评测。

## coverage_spec
覆盖二维翼型 RANS/SST 工况，适用于非结构网格场预测、Transolver、GNO/GNOT、MeshGraphNet 风格模型。

## label_spec
点级目标通常为速度 `U`、压力 `p` 和湍粘性 `nut`；输入包括坐标、来流条件、SDF 和法向量。

## split_strategy
优先使用 manifest 的 split 键；训练/验证可从对应 train 列表中按固定比例再切分，test 使用对应 test 键。

## constraints
样本名解析来流条件，命名不合规会失败；VTK 字段名是硬约束；归一化统计只能从训练集生成。
