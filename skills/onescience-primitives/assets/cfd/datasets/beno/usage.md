## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/BENO`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/BENO`。主要入口为 `data/Dirichlet` 和 `data/Neumann`。

## data_schema
读取同一边界类型和前缀下的 `RHS_*_all.npy`、`SOL_*_all.npy`、`BC_*_all.npy`，三者样本维必须一致。`RHS` 是输入场，`BC` 是边界条件，`SOL` 是目标解。

## task_usage
适用于 BENO、边界条件神经算子、二维椭圆 PDE 代理模型和异构图算子学习。

## integration_paths
优先使用 `cfd/datapipes/beno`，由 datapipe 完成边界归一化、平滑、梯度构造、节点采样和缓存。若自定义 reader，需输出 G1/G2/G1+2 异构图或规则网格 batch。

## preparation_requirements
检查前缀文件是否成组三个同时存在；确认 `RHS/SOL/BC` 样本数一致；确认 cache_dir 可写；过滤 `__MACOSX`。

## consumption_interfaces
OneScience BENO datapipe 输出 PyG `HeteroData`，包含 `G1.x`、`G2.x`、`G1+2.y`、边界、边特征和 sample id。

## evaluation_protocol
报告解场 L2、相对 L2、边界附近误差和不同边界类型/前缀上的分组误差。

## operation_limits
边界点数 128 是实现假设；没有独立 val split；训练/测试目标尺度处理可能不同，评测前要解码到一致尺度。
