## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/pinnsformer`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/pinnsformer`。入口为 `convection.mat` 和 `cylinder_nektar_wake.mat`。

## data_schema
MAT 文件内部键需在任务环境抽检；通常包含时空坐标、PDE 解场或圆柱尾迹时序。

## task_usage
适用于 PINNsFormer、PINN、物理残差监督、对流方程建模和圆柱尾迹预测。

## integration_paths
使用 scipy.io 或兼容 reader 读取 MAT；将数据点拆分为 supervised points、collocation points 和 evaluation grid。

## preparation_requirements
确认 MAT 版本和内部变量名；固定时间/空间采样策略；明确 PDE 方程参数和残差计算方式。

## consumption_interfaces
PINN 类模型通常消费 `x,t,u` 或 `x,y,t,u/v/p`，并额外需要 collocation 坐标。

## evaluation_protocol
报告数据点误差、物理残差、时间外推误差和 cylinder wake 的速度/压力误差。

## operation_limits
未探测键前不要硬编码读取；convection 和 cylinder wake 是不同任务；MAT reader 依赖需在运行环境提供。
