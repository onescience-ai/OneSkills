## description
为 PDENNEval/PDEBench HDF5 数据选择模型族 datapipe、降采样和评测 workflow。

## when_to_use
任务需要 FNO、DeepONet、MPNN、UNet、UNO 或 PINO 在 PDEBench 风格数据上训练评测时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/PDENNEval`。输入为 HDF5/H5 或生成数据 zip。

## outputs
输出为文件 schema、模型族 batch 协议、降采样参数、train/val split 和 PDE 指标。

## procedure
1. 选择具体 PDE 文件和模型族。
2. 探测 HDF5/H5 内部键、维度和变量。
3. 配置 initial_step、reduced_resolution、test_ratio。
4. 选择对应 OneScience datapipe 类。
5. 做单 batch shape 检查。
6. 训练并按变量/时间步评测。
7. 若使用 PINO，额外检查 PDE residual dataloader。

## constraints
不同模型族返回协议不同；无统一 test loader；HDF5 schema 不统一。

## next_phase_recommendation
schema 明确后进入模型配置；否则先停留在数据探测。

## fallback
若某文件读取失败，先换 PDEBench 已知 HDF5 文件做 smoke test。
