## description
为 DeepCFD pickle 网格数据选择加载、split、训练和评测路线。

## when_to_use
任务需要使用 DeepCFD 的 `dataX.pkl/dataY.pkl` 做二维场回归时使用。

## inputs
输入为成对 pickle 张量，`source.data_dir` 使用 `usage.md` 中直接包含两文件的目录。

## outputs
输出为 train/test 索引、`x/y` batch、通道权重和逐通道指标。

## procedure
1. 校验两个 pickle 文件存在。
2. 读取 shape，确认样本数、网格尺寸与 `spec.md` 的输入和标签通道顺序。
3. 用固定 seed 和 split_ratio 生成一份共享索引，按该索引选择成对样本。
4. 生成 dataloader 并检查 `{"x","y"}`。
5. 复现时按原实现计算通道权重；严格留出验证时只用训练段统计权重。
6. 训练并按任务定义的归约方式报告逐通道误差。

## constraints
全量加载内存；没有独立 val；不含坐标和 mask。

## next_phase_recommendation
小数据可直接训练；若内存不足，先改懒加载或转换为 chunk 格式。

## fallback
若 pickle 读取失败，记录协议版本并尝试用原 Python 环境读取。
