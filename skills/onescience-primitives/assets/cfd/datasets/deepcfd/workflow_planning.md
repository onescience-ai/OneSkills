## description
为 DeepCFD pickle 网格数据选择加载、split、训练和评测路线。

## when_to_use
任务需要使用 DeepCFD 的 `dataX.pkl/dataY.pkl` 做二维场回归时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/DeepCFD`。输入为成对 pickle 张量。

## outputs
输出为 train/test 索引、`x/y` batch、通道权重和逐通道指标。

## procedure
1. 校验两个 pickle 文件存在。
2. 读取 shape，确认样本数和输出通道数。
3. 固定 seed 和 split_ratio。
4. 生成 dataloader 并检查 `{"x","y"}`。
5. 获取 loss weights。
6. 训练并报告逐通道误差。

## constraints
全量加载内存；没有独立 val；不含坐标和 mask。

## next_phase_recommendation
小数据可直接训练；若内存不足，先改懒加载或转换为 chunk 格式。

## fallback
若 pickle 读取失败，记录协议版本并尝试用原 Python 环境读取。
