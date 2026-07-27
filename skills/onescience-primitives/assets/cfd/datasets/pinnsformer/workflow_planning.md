## description
为 PINNsFormer MAT 数据选择变量探测、物理残差点和训练 workflow。

## when_to_use
任务需要 convection 或 cylinder_nektar_wake 示例数据进行 PINN/PINNsFormer 训练时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/pinnsformer`。输入为两个 MAT 文件。

## outputs
输出为 MAT 字段映射、监督点、collocation 点、PDE 参数和误差指标。

## procedure
1. 用 MAT reader 探测变量名和 shape。
2. 选择 convection 或 cylinder wake 任务。
3. 构造监督采样点和物理残差点。
4. 固定时间/空间划分。
5. 训练 PINN/Transformer 模型。
6. 报告数据误差和残差误差。

## constraints
未探测内部键前不能写死变量；两个 MAT 是不同任务；需要方程参数支持残差计算。

## next_phase_recommendation
先做 MAT 键探测，再进入训练脚本生成。

## fallback
若 scipy 不可用，使用任务环境或转换工具先导出 NumPy。
