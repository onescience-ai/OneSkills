## description
为 Transolver-Airfoil-Design/AirfRANS VTK 数据选择 split、采样、构图和评测 workflow。

## when_to_use
任务需要二维翼型非结构网格 CFD 场预测或 Transolver-Airfoil 训练时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/Transolver-Airfoil-Design`。输入为 manifest 和每个样本的 VTK 文件。

## outputs
输出为 split key、采样策略、PyG Data schema、统计量和分 split 指标。

## procedure
1. 读取 manifest，选择 full/scarce/Reynolds/AoA split。
2. 校验样本目录和 `internal/aerofoil/freestream` 文件。
3. 抽样读取 VTK 字段。
4. 配置 AirfRANS datapipe、stats_dir 和采样策略。
5. 做单 batch 检查。
6. 训练并按 split 输出速度/压力/nut 指标。

## constraints
VTK 字段名和样本命名规则是硬约束；统计量只来自训练集；test 不做训练下采样。

## next_phase_recommendation
若 VTK 读取正常，进入 Transolver/GNO 模型训练。

## fallback
若 VTK 读取失败，先只解析 manifest 并报告缺失字段。
