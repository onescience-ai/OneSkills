## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/Transolver-Airfoil-Design`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/Transolver-Airfoil-Design`。入口为 `Dataset/manifest.json` 和每个翼型样本目录。

## data_schema
每个样本包含 internal `.vtu`、aerofoil `.vtp`、freestream `.vtp`；manifest 给出 full/scarce/Reynolds/AoA train/test 划分。

## task_usage
适用于 AirfRANS、Transolver-Airfoil、二维翼型非结构网格场预测和来流/几何泛化评测。

## integration_paths
优先使用 `cfd/datapipes/airfrans`；配置 `source.data_dir` 指向 `Dataset`，并设置 stats_dir、split 键、采样策略和 graph 构建参数。

## preparation_requirements
确认 manifest split 键；抽检 VTK 字段 `U,p,nut,implicit_distance,Normals`；训练集生成归一化统计。

## consumption_interfaces
输出 PyG Data：`x=[pos,u_inf,sdf,normal]`，`y=[v_x,v_y,p,nut]`，以及 `pos/surf/edge_index`。

## evaluation_protocol
报告速度、压力、nut 的点级误差；按 full/scarce/Reynolds/AoA split 分别评测。

## operation_limits
样本名解析失败会影响来流条件；test 不应参与统计量；VTK 读取依赖和字段名需提前验证。
