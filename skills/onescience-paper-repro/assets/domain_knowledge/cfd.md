# CFD Domain Knowledge

| 字段 | 摘要 |
| --- | --- |
| 适用领域 | 流体、PDE、CFD、仿真加速和物理场预测论文。 |
| 召回信号 | fluid、PDE、CFD、Navier-Stokes、mesh、solver、velocity、pressure、boundary condition、Reynolds、Mach、residual。 |
| 核心用途 | 提示 PDE/边界条件/网格/状态变量/rollout/残差和守恒类指标的提取与审计。 |
| 注意事项 | 只作为检查清单；只有论文或用户材料出现的内容才能写成确定要求。 |

用于流体、PDE、CFD、仿真加速和物理场预测论文的提取提示。这里只提供检查清单，不提供论文事实。

## 常见数据对象

- PDE 类型、状态变量、边界条件、初始条件。
- 网格类型：structured、unstructured、mesh、point cloud、spectral grid。
- 速度、压力、密度、温度、涡量、level set、signed distance field。
- time step、CFL、Reynolds/Mach/Prandtl 等无量纲参数。

## 提取时重点检查

- 输入状态、输出状态、预测 delta/residual/full state 必须分开。
- solver 生成数据的设置、稳定性条件和 boundary condition 要写清证据。
- shape ledger 要区分 batch、time、node/cell、field/channel、coordinate、edge feature。
- PDE residual loss、boundary loss、conservation loss 不能默认存在；论文没说就标缺失或假设。
- rollouts、teacher forcing、autoregressive update 和 evaluation horizon 分开记录。

## 常见评估提示

- L2/MSE/MAE、relative error、rollout stability、conservation error。
- drag/lift、pressure coefficient、vorticity error、spectrum error。
- boundary violation、PDE residual、long-horizon drift。

只有论文实际出现或用户材料提供的指标才能写成确定评估要求。
