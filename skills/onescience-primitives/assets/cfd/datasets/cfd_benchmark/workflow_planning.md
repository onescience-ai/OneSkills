## description
为 CFD_Benchmark 多子集选择 reader、split、神经算子模型和评测路线。

## when_to_use
任务需要 Airfoil、pipe、Navier-Stokes、Darcy、diffusion-sorption 等 CFD/PDE benchmark 时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/CFD_Benchmark`。输入为按子集组织的 NPY、MAT、H5 或压缩包。

## outputs
输出为子集 reader、shape 记录、通道说明、train/val/test split、归一化和相对 L2 指标。

## procedure
1. 先明确目标子集和模型族。
2. 对 NPY 读取 shape，对 MAT/H5 抽检内部键。
3. 明确输入/目标通道和坐标网格。
4. 设置样本级或轨迹级 split。
5. 生成模型所需 batch，如 `(input,target,grid)`。
6. 运行小 batch 训练或推理检查。
7. 固化评测指标和降采样参数。

## constraints
不要跨子集硬编码通道；MAT/H5 依赖需可用；压缩包要先确认解压状态。

## next_phase_recommendation
若子集 schema 已确认，进入对应模型配置；若未确认，先只做数据探测。

## fallback
若 MAT/H5 读取不可用，先使用 airfoil/pipe 的 NPY 子集。
