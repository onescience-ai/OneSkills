## description
为 Eagle 变长网格时序数据选择 split、窗口、聚类和 batch padding workflow。

## when_to_use
任务需要 Eagle CFD 网格时序、cluster-aware 预测或变长 mesh graph 模型时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/Eagle`。输入为 `sim.npz`、`triangles.npy` 和可选 kmeans。

## outputs
输出为 split 文件、窗口长度、cluster 配置、padded batch schema 和速度/压力误差。

## procedure
1. 枚举 `Eagle_dataset/Cre` 下仿真目录。
2. 生成或读取 `train.txt/valid.txt/test.txt`。
3. 抽样检查 `sim.npz` 键和 triangles。
4. 选择窗口长度和 `n_cluster`。
5. 构造 datapipe 并检查 padding 后 batch。
6. 训练并记录过滤空样本情况。

## constraints
缺少 split 文件不能直接用 datapipe；cluster 取值需匹配文件；坏样本过滤可能造成 batch 为空。

## next_phase_recommendation
先生成小 split 做 smoke test，再扩大到完整训练。

## fallback
若 cluster 文件不可用，设置 `n_cluster=1` 或禁用 cluster 分支。
