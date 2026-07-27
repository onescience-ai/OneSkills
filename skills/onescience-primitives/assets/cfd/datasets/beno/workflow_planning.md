## description
为 BENO `RHS/SOL/BC` 数据选择异构图预处理、缓存、训练和评测路线。

## when_to_use
任务需要使用 BENO 数据做边界算子学习、二维 PDE 解场预测或 BENO 模型训练时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/BENO`。输入为 Dirichlet/Neumann 下成组的 `RHS/SOL/BC` NumPy 文件。

## outputs
输出为边界类型、前缀、train/test 索引、缓存路径、HeteroData schema 和解场误差指标。

## procedure
1. 选择边界类型和 `N32_*` 前缀。
2. 校验 `RHS/SOL/BC` 三文件同时存在且样本数一致。
3. 配置 `source.data_dir`、`file_prefix` 和可写 `cache_dir`。
4. 执行小样本预处理，检查 G1/G2 特征和目标 shape。
5. 固定 `ntrain/ntest`，运行训练和测试。
6. 输出整体误差和分边界类型误差。

## constraints
边界点数、resolution、train/test 切分方式与 datapipe 实现强绑定；缓存不可写回共享数据目录。

## next_phase_recommendation
若预处理成功，进入 BENO 训练；若 shape 不一致，先生成坏文件清单。

## fallback
若图预处理失败，可先把数组作为规则网格监督数据做 reader smoke test。
