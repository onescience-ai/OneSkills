## description
为 Transolver-Car-Design 预处理图数据选择 fold、PyG datapipe、训练和评测 workflow。

## when_to_use
任务需要三维汽车外流场压力/速度预测或 ShapeNetCar/Transolver-Car datapipe 时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/Transolver-Car-Design`。输入为 `preprocessed_data/param0..param8` 图缓存。

## outputs
输出为 fold_id、训练/验证样本、PyG Data schema、统计量和表面压力指标。

## procedure
1. 校验 `param0..param8` 存在。
2. 选择 `fold_id` 作为验证 fold。
3. 抽样读取 `x/y/pos/surf/edge_index`。
4. 配置 ShapeNetCar preprocessed 模式。
5. 做单 batch 显存和 shape 检查。
6. 训练并按 fold 报告速度/压力误差。

## constraints
边数很大，batch size 需谨慎；不要跨 fold 泄漏；辅助文件不是训练样本。

## next_phase_recommendation
先在单 fold 小 batch 上验证，再全量训练。

## fallback
若图边过大，可临时使用 radius_graph 重构或降低采样点数。
